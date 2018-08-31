from __future__ import absolute_import, print_function
from argparse import ArgumentParser
from getpass import getpass
from gopapi.crypto import cipher_auth, decipher_auth
from gopapi.api import API
import requests
import json
import sys
import os


def handle_domain(args):
    api = API.shared()

    domain = args.domain[0]
    action = args.action[0]

    if action == 'records':
        response = api.get('domains/{}/records'.format(domain))
        data = response.json()

        print(response)
        
        for record in data:
            if not args.only_type \
            or record['type'].lower() == args.only_type.lower():
                print("{}\t{}\t{}".format(record['type'],
                                          record['name'],
                                          record['data']
                                          ))

    elif action == 'add-record':
        url = 'domains/{}/records'.format(domain)
        params = [
            {
                'type': args.data[0].upper(), # A / CNAME
                'name': args.data[1], # fulano., mangano.
                'data': args.data[2], # points to ip/domain
            }
        ]
        response = api.patch(url, data=json.dumps(params))

        if response.status_code != 200:
            info = response.json()
            print(info['code'], file=sys.stderr)
            sys.exit(1)

    elif action == 'suggest':
        url = 'domains/suggest'
        domains = args.data[0].split(',')
        response = api.get(url, tlds=domains)
        #print(response.content)

    elif action == 'available' or action == 'check':
        response = api.get('domains/available', domain=domain)
        data = response.json()
        if data['available']:
            print('available')
        else:
            print('not available')
        

def main():
    parser = ArgumentParser()

    subparsers = parser.add_subparsers(dest='entity')
    domain_parser = subparsers.add_parser('domain')
    domain_parser.add_argument('domain', nargs=1,
                               help=('Domain to be managed. '
                                     'e.g. mydomain.com')
                               )
    domain_parser.add_argument('action', nargs=1,
                               help='What to do with the domain')
    domain_parser.add_argument('data', nargs='*')
    domain_parser.add_argument('-t', dest='only_type')

    domains_parser = subparsers.add_parser('domains')

    inter_parser = subparsers.add_parser('i')

    api = API.shared()
    args = parser.parse_args()

    config_file = os.path.expanduser('~/.gopapi')
    if not os.path.isfile(config_file):
        api.key = getpass('API Key: ').encode()
        api.secret = getpass('Secret: ').encode()

        should_save = input('should save auth? (y/n): ')

        if should_save.lower().startswith('y'):
            passwd = getpass('password protection: ').encode()
            with open(config_file, 'wb') as fp:
                serialized = cipher_auth(api.key, api.secret, passwd)
                fp.write(serialized)
    else:
        passwd = getpass('unlock auth: ').encode()
        with open(config_file, 'rb') as fp:
            data = fp.read()
            auth = decipher_auth(data, passwd)
            api.key, api.secret = auth

    if args.entity == 'domain':
        handle_domain(args)

    elif args.entity == 'domains':
        data = api.get('/domains')
        for domain in data.json():
            print(domain['domain'])

    elif args.entity == 'i':
        from gopapi import interactive

if __name__ == '__main__':
    main()