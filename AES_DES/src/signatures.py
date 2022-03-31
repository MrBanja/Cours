import rsa


def get_key_pair_bytes() -> tuple[bytes, bytes]:
    (pubkey, privkey) = rsa.newkeys(512)
    return pubkey.save_pkcs1(), privkey.save_pkcs1()


def sign_file(file: bytes, private_key: bytes) -> bytes:
    private_key = rsa.PrivateKey.load_pkcs1(private_key)
    return rsa.sign(file, private_key, 'SHA-1')


def validate_signature(
        file: bytes,
        signature: bytes,
        public_key: bytes,
):
    rsa.verify(file, signature, rsa.PublicKey.load_pkcs1(public_key))
