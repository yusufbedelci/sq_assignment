from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from pathlib import Path

# Get the directory path of this file
dir_path = Path(__file__).resolve().parent
keys_dir = dir_path / "keys"

# Generate private key
private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,
)

# Serialize and save private key to private.pem
private_key_path = keys_dir / "private.pem"
with private_key_path.open("wb") as key_file:
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
public_key_path = keys_dir / "public.pem"
with public_key_path.open("wb") as key_file:
    key_file.write(
        public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
    )
