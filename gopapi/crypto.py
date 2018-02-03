from Crypto.Cipher import AES
from binascii import hexlify
from hashlib import sha256
from os import urandom

salt = lambda: urandom(16)
iv = 'GoDaddy Auth 123'

def cipher_auth(key, secret, password):
    hashed_pwd = sha256(password).digest()
    aes = AES.new(hashed_pwd, AES.MODE_CBC, iv)
    data = '{}{:<48}{:<48}{}'.format(salt(), key, secret, salt())
    return aes.encrypt(data)

def decipher_auth(serialized, password):
    hashed_pwd = sha256(password).digest()
    aes = AES.new(hashed_pwd, AES.MODE_CBC, iv)
    data = aes.decrypt(serialized)
    key = data[16:64].strip()
    secret = data[64:112].strip()
    return (key, secret, )
