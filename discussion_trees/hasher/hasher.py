import os
# import cbor2
import hashlib


def calculate_sha256_from_file(file_path):
    """Calculate the SHA256 hash of a file."""
    sha256 = hashlib.sha256()
    with open(file_path, 'rb') as file:
        # Reading in chunks to handle large files
        for chunk in iter(lambda: file.read(4096), b''):
            sha256.update(chunk)
    return sha256.hexdigest()


def calculate_sha256(data):
    """Calculate the SHA256 hash of a string or bytes."""
    sha256 = hashlib.sha256()
    
    if isinstance(data, str):
        sha256.update(data.encode('utf-8'))
    elif isinstance(data, bytes):
        sha256.update(data)
    else:
        raise TypeError("Expected data to be of type str or bytes")
    
    return sha256.hexdigest()