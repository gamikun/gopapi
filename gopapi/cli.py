from argparse import ArgumentParser
from getpass import getpass
from Crypto.Cipher import AES
from hashlib import md5
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
    domains_parser = subparsers.add_parser('domain')
    domains_parser.add_argument('domain', nargs=1)
    domains_parser.add_argument('action', nargs=1)
    domains_parser.add_argument('data', nargs='*')

    api = API.shared()
    args = parser.parse_args()

    config_file = os.path.expanduser('~/.gopapi')
    if not os.path.isfile(config_file):
        api.key = getpass('API Key: ')
        api.secret = getpass('Secret: ')

        should_save = raw_input('should save auth? (y/n): ')

        if should_save.lower().startswith('y'):
            cipher_passwd = md5(getpass('password protection: ')).hexdigest()
            aes = AES.new(cipher_passwd, AES.MODE_CBC, 'GoDaddy Auth 123')
            padded = '{:>128}'.format('{},{}'.format(api.key, api.secret))
            ciphered = aes.encrypt(padded)
            with open(config_file, 'w') as fp:
                fp.write(ciphered)
    else:
        cipher_passwd = md5(getpass('unlock auth: ')).hexdigest()
        aes = AES.new(cipher_passwd, AES.MODE_CBC, 'GoDaddy Auth 123')
        with open(config_file, 'r') as fp:
            decrypted = aes.decrypt(fp.read()).strip()
            apikey, secret = decrypted.split(',')
            api.key = apikey
            api.secret = secret

    if args.entity == 'domain':
        handle_domain(args)

if __name__ == '__main__':
    main()