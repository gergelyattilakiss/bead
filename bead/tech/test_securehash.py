import os
import pytest
from .. import tech

securehash = tech.securehash
write_file = tech.fs.write_file


def test_file_hash(tmp_path):
    """Test hashing a file."""
    # given a file
    file_path = tmp_path / 'file'
    write_file(file_path, b'with some content')
    
    # when file is hashed
    with open(file_path, 'rb') as f:
        hashresult = securehash.file(f, os.path.getsize(file_path))
    
    # then result is an ascii string of more than 32 chars
    hashresult.encode('ascii')
    assert isinstance(hashresult, str)
    assert len(hashresult) > 32


def test_bytes_hash():
    """Test hashing bytes."""
    # given some bytes
    some_bytes = b'some bytes'
    
    # when bytes are hashed
    hashresult = securehash.bytes(some_bytes)
    
    # then result is an ascii string of more than 32 chars
    hashresult.encode('ascii')
    assert isinstance(hashresult, str)
    assert len(hashresult) > 32


def test_bytes_and_file_compatibility(tmp_path):
    """Test that bytes and file hashing are compatible."""
    # given some bytes and file with those bytes
    some_bytes = b'some bytes'
    file_path = tmp_path / 'file'
    write_file(file_path, some_bytes)
    
    # when file and bytes are hashed
    bytes_hash = securehash.bytes(some_bytes)
    with open(file_path, 'rb') as f:
        file_hash = securehash.file(f, os.path.getsize(file_path))
    
    # then the hashes are the same
    assert bytes_hash == file_hash
