import base64

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.fernet import Fernet


SHA_ITERS = 480_000
LENGTH = 32


def encrypt_data(data: bytes, master_key: bytes, salt_token: bytes):
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256,
        length=LENGTH,
        salt=salt_token,
        iterations=SHA_ITERS,
        backend=default_backend(),
    )
    # Derive encryption key from master key
    encryption_key = base64.urlsafe_b64encode(kdf.derive(master_key))
    # Encrypt data using Fernet
    cipher = Fernet(encryption_key)
    encrypted_data = cipher.encrypt(data)
    return encrypted_data


def decrypt_data(encrypted_data: bytes, master_key: bytes, salt_token: bytes):
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256,
        length=LENGTH,
        salt=salt_token,
        iterations=SHA_ITERS,
        backend=default_backend(),
    )
    # Derive encryption key from master key
    encryption_key = base64.urlsafe_b64encode(kdf.derive(master_key))
    # Decrypt data using Fernet
    cipher = Fernet(encryption_key)
    decrypted_data = cipher.decrypt(encrypted_data)
    return decrypted_data.decode()

if __name__ == "__main__":
    secret_string = "hello world"
    
    encrypted_secret = encrypt_data(secret_string.encode(), b'bad_pass', b'bad salt')
    
    print(encrypted_secret)
    
    decrypted_secret = decrypt_data(encrypted_secret, b'bad_pass', b'bad salt')
    
    print(decrypted_secret)