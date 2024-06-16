from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
import os

# Get the directory path of this file
dir_path = os.path.dirname(os.path.realpath(__file__))

# Generate private key
private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,
)

# Serialize and save private key to private.pem
with open(f"{dir_path}/private.pem", "wb") as key_file:
    key_file.write(
        private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )
    )

# Generate public key
public_key = private_key.public_key()

# Serialize and save public key to public.pem
with open(f"{dir_path}/public.pem", "wb") as key_file:
    key_file.write(
        public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
    )
