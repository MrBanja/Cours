import pathlib

from Cryptodome.Cipher import AES, DES
from hashlib import md5, sha256


def pad(text: bytes) -> bytes:
    while len(text) % 8 != 0:
        text = text + b' '
    return text


def aes_encrypt_file(passkey: str, file_data: bytes) -> tuple[bytes, bytes]:
    aes = AES.new(md5(passkey.encode()).digest(), AES.MODE_EAX)
    ciphertext, tag = aes.encrypt_and_digest(file_data)
    with pathlib.Path(__file__).parent.parent.joinpath('static/aes_encrypted.txt').open('wb') as fp:
        fp.write(ciphertext)

    return aes.nonce, tag


def aes_decrypt_file(passkey: str, file_data: bytes, nonce: bytes, tag: bytes):
    aes = AES.new(md5(passkey.encode()).digest(), AES.MODE_EAX, nonce=nonce)
    plaintext = aes.decrypt(file_data)
    aes.verify(tag)
    with pathlib.Path(__file__).parent.parent.joinpath('static/aes_decrypted.txt').open('wb') as fp:
        fp.write(plaintext)


def des_encrypt_file(passkey: str, file_data: bytes):
    des = DES.new(sha256(passkey.encode()).digest()[:8], DES.MODE_ECB)
    encrypt_result = des.encrypt(pad(file_data))
    with pathlib.Path(__file__).parent.parent.joinpath('static/des_encrypted.txt').open('wb') as fp:
        fp.write(encrypt_result)


def des_decrypt_file(passkey: str, file_data: bytes):
    des = DES.new(sha256(passkey.encode()).digest()[:8], DES.MODE_ECB)
    decrypt_result = des.decrypt(file_data)
    decrypt_result.decode('utf-8')  # Raises UnicodeDecodeError if passkey is incorrect.
    with pathlib.Path(__file__).parent.parent.joinpath('static/des_decrypted.txt').open('wb') as fp:
        fp.write(decrypt_result)
