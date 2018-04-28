from __future__ import absolute_import
from argparse import ArgumentParser
from getpass import getpass
from gopapi.crypto import cipher_auth, decipher_auth
import requests
import json
import os


class API:
    api_url = 'https://api.godaddy.com/v1'
    _shared = None

    def __init__(self, key, secret):
        self.key = key
        self.secret = secret

    @classmethod
    def shared(cls):
        if not cls._shared:
            cls._shared = API(None, None)
        return cls._shared

    def get(self, path):
        headers = {
            'Authorization': 'sso-key {}:{}'.format(self.key, self.secret)
        }
        url = '{}/{}'.format(self.api_url, path)
        return requests.get(url, headers=headers)

    def patch(self, path, **kwargs):
        headers = {
            'Authorization': 'sso-key {}:{}'.format(self.key, self.secret),
            'Content-Type': 'application/json',
        }
        url = '{}/{}'.format(self.api_url, path)
        print(url)
        return requests.patch(url, headers=headers, **kwargs)


def handle_domain(args):
    api = API.shared()

    domain = args.domain[0]
    action = args.action[0]

    if action == 'records':
        response = api.get('domains/{}/records'.format(domain))
        data = response.json()
        
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
                'type': args.data[0], # A / CNAME
                'name': args.data[1], # fulano., mangano.
                'data': args.data[2], # points to ip/domain
            }
        ]
        response = api.patch(url, data=json.dumps(params))
        print(response)

def main():
    parser = ArgumentParser()

    subparsers = parser.add_subparsers(dest='entity')
    domain_parser = subparsers.add_parser('domain')
    domain_parser.add_argument('domain', nargs=1)
    domain_parser.add_argument('action', nargs=1)
    domain_parser.add_argument('data', nargs='*')
    domain_parser.add_argument('-t', dest='only_type')

    domains_parser = subparsers.add_parser('domains')

    api = API.shared()
    args = parser.parse_args()

    config_file = os.path.expanduser('~/.gopapi')
    if not os.path.isfile(config_file):
        api.key = getpass('API Key: ')
        api.secret = getpass('Secret: ')

        should_save = raw_input('should save auth? (y/n): ')

        if should_save.lower().startswith('y'):
            passwd = getpass('password protection: ')
            with open(config_file, 'w') as fp:
                serialized = cipher_auth(api.key, api.secret, passwd)
                fp.write(serialized)
    else:
        passwd = getpass('unlock auth: ')
        with open(config_file, 'r') as fp:
            data = fp.read()
            auth = decipher_auth(data, passwd)
            api.key, api.secret = auth

    if args.entity == 'domain':
        handle_domain(args)

    elif args.entity == 'domains':
        data = api.get('/domains')
        for domain in data.json():
            print(domain['domain'])

if __name__ == '__main__':
    main()