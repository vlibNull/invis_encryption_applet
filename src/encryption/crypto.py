import os
from typing import Optional

try:
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    from cryptography.hazmat.primitives import padding
    from cryptography.hazmat.backends import default_backend
except ImportError:
    # This is a fallback for static analysis, actual dependency is in requirements.txt
    Cipher, algorithms, modes, padding, default_backend = None, None, None, None, None

# AES specifications
AES_BLOCK_SIZE_BYTES = 16  # 128 bits
AES_KEY_SIZE_BYTES = 32   # 256 bits

def encrypt(plaintext: bytes, key: bytes, filename: str) -> Optional[bytes]:
    """
    Encrypts plaintext using AES-256-CBC and prepends the file extension.

    The process:
    1.  Extracts the file extension from the filename.
    2.  Creates a header containing the extension (e.g., ".txt|").
    3.  Prepends the header to the plaintext.
    4.  Encrypts the combined data (header + plaintext).
    5.  Returns the IV + encrypted data.

    Args:
        plaintext (bytes): The data to encrypt.
        key (bytes): The 32-byte (256-bit) encryption key.
        filename (str): The original name of the file, used to get the extension.

    Returns:
        Optional[bytes]: The encrypted data (IV + ciphertext), or None if encryption fails.
    """
    if not all([Cipher, algorithms, modes, padding, default_backend]):
        raise ImportError("Cryptography library not found. Please install it with 'pip install cryptography'.")

    if len(key) != AES_KEY_SIZE_BYTES:
        raise ValueError(f"Invalid key size. Key must be {AES_KEY_SIZE_BYTES} bytes long.")

    try:
        # Get file extension, including the dot
        _, ext = os.path.splitext(filename)
        header = f"{ext}|".encode('utf-8')
        
        # Prepend header to the actual plaintext
        data_to_encrypt = header + plaintext

        # Generate a random IV for each encryption
        iv = os.urandom(AES_BLOCK_SIZE_BYTES)

        # Pad the plaintext to be a multiple of the block size
        padder = padding.PKCS7(algorithms.AES.block_size).padder()
        padded_data = padder.update(data_to_encrypt) + padder.finalize()

        # Create AES-CBC cipher
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        encryptor = cipher.encryptor()

        # Encrypt the data
        ciphertext = encryptor.update(padded_data) + encryptor.finalize()

        # Prepend the IV to the ciphertext for use during decryption
        return iv + ciphertext
    except Exception:
        # Broad exception to catch any potential crypto errors
        return None

def decrypt(encrypted_data: bytes, key: bytes) -> Optional[tuple[bytes, Optional[str]]]:
    """
    Decrypts data encrypted with AES-256-CBC and extracts the original file extension.

    The process:
    1.  Splits the input into IV and ciphertext.
    2.  Decrypts the ciphertext.
    3.  Unpads the decrypted data.
    4.  Parses the result to separate the original file extension from the plaintext.
    5.  Returns the plaintext and the extension.

    Args:
        encrypted_data (bytes): The data to decrypt (must be IV + ciphertext).
        key (bytes): The 32-byte (256-bit) encryption key.

    Returns:
        Optional[tuple[bytes, Optional[str]]]: A tuple containing the original
        plaintext and the file extension (e.g., (b'data', '.txt')). Returns
        None if decryption fails.
    """
    if not all([Cipher, algorithms, modes, padding, default_backend]):
        raise ImportError("Cryptography library not found. Please install it with 'pip install cryptography'.")
        
    if len(key) != AES_KEY_SIZE_BYTES:
        raise ValueError(f"Invalid key size. Key must be {AES_KEY_SIZE_BYTES} bytes long.")

    if len(encrypted_data) < AES_BLOCK_SIZE_BYTES:
        return None

    try:
        # Extract the IV and ciphertext
        iv = encrypted_data[:AES_BLOCK_SIZE_BYTES]
        ciphertext = encrypted_data[AES_BLOCK_SIZE_BYTES:]

        # Create AES-CBC cipher
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()

        # Decrypt the data
        padded_plaintext = decryptor.update(ciphertext) + decryptor.finalize()

        # Unpad the plaintext
        unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
        plaintext_with_header = unpadder.update(padded_plaintext) + unpadder.finalize()
        
        # Split the header from the content
        try:
            header, plaintext = plaintext_with_header.split(b'|', 1)
            ext = header.decode('utf-8')
            return plaintext, ext
        except (ValueError, UnicodeDecodeError):
            # If split fails or header is not valid utf-8, it means there was no header
            # or the data is from an older version. Return the whole content.
            return plaintext_with_header, None

    except (ValueError, TypeError):
        # Invalid padding or key
        return None
    except Exception:
        # Other crypto errors
        return None
