import os
import shutil
import tarfile
from pathlib import Path

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt


class IncorrectPasswordOrFileCorrupted(Exception):
    pass


def encrypt_file(path: Path, password: str) -> Path:
    data = path.read_bytes()

    salt = os.urandom(16)
    nonce = os.urandom(12)
    kdf = Scrypt(
        salt=salt,
        length=32,
        n=2**14,
        r=8,
        p=1,
    )
    key = kdf.derive(password.encode())
    aes = AESGCM(key)
    ciphertext = aes.encrypt(nonce, data, None)

    out = path.with_name(path.name + '.lock')
    out.write_bytes(salt + nonce + ciphertext)
    path.unlink()
    return out


def decrypt_file(path: Path, password: str) -> Path:
    data = path.read_bytes()

    salt = data[:16]
    nonce = data[16:28]
    ciphertext = data[28:]
    kdf = Scrypt(
        salt=salt,
        length=32,
        n=2**14,
        r=8,
        p=1,
    )
    key = kdf.derive(password.encode())
    aes = AESGCM(key)
    try:
        plaintext = aes.decrypt(nonce, ciphertext, None)
    except InvalidTag as exc:
        raise IncorrectPasswordOrFileCorrupted(
            'Invalid password or file corrupted'
        ) from exc

    out = path.with_suffix('')
    out.write_bytes(plaintext)
    path.unlink()
    return out


def encrypt_dir(path: Path, password: str) -> Path:
    tar_path = path.with_suffix('.tar')

    with tarfile.open(tar_path, mode='w') as tar:
        tar.add(path, arcname=path.name)

    encrypted_dir_path = encrypt_file(
        path=tar_path,
        password=password,
    )

    shutil.rmtree(path)
    return encrypted_dir_path


def decrypt_dir(path: Path, password: str) -> Path:
    tar_path = decrypt_file(path=path, password=password)

    tar_dir = tar_path.parent

    with tarfile.open(tar_path, mode='r') as tar:
        tar.extractall(path=tar_dir)

    tar_path.unlink()

    return tar_dir / tar_path.stem
