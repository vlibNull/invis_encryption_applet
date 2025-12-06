import os
import secrets
from typing import List, Optional

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

# Define the directory where keys will be stored relative to the project root
KEY_DIR = '.keys'
KEY_FILE_EXTENSION = '.key'

def _get_key_path(key_name: str) -> str:
    """Helper function to get the full path for a key file."""
    return os.path.join(KEY_DIR, f"{key_name}{KEY_FILE_EXTENSION}")

def generate_key(key_name: str, length_bytes: int = 32) -> bytes:
    """
    Generates a new secure random key of specified length and saves it.
    AES-256 requires a 32-byte key.

    Args:
        key_name (str): The name to save the key as (e.g., 'my_secret_key').
        length_bytes (int): The length of the key in bytes. Defaults to 32 (AES-256).

    Returns:
        bytes: The newly generated key.
    
    Raises:
        ValueError: If a key with the given name already exists.
    """
    os.makedirs(KEY_DIR, exist_ok=True)
    key_path = _get_key_path(key_name)
    if os.path.exists(key_path):
        raise ValueError(f"Key with name '{key_name}' already exists.")

    key = secrets.token_bytes(length_bytes)
    with open(key_path, 'wb') as f:
        f.write(key)
    return key

def save_key(key_name: str, key_data: bytes) -> None:
    """
    Saves an existing key to a file.

    Args:
        key_name (str): The name to save the key as.
        key_data (bytes): The raw key data to save.
        
    Raises:
        ValueError: If a key with the given name already exists.
    """
    os.makedirs(KEY_DIR, exist_ok=True)
    key_path = _get_key_path(key_name)
    if os.path.exists(key_path):
        raise ValueError(f"Key with name '{key_name}' already exists.")

    with open(key_path, 'wb') as f:
        f.write(key_data)

def load_key(key_name: str) -> Optional[bytes]:
    """
    Loads a key from a file in the KEY_DIR.

    Args:
        key_name (str): The name of the key to load.

    Returns:
        Optional[bytes]: The key as bytes if found, None otherwise.
    """
    key_path = _get_key_path(key_name)
    if not os.path.exists(key_path):
        return None
    with open(key_path, 'rb') as f:
        key = f.read()
    return key

def list_keys() -> List[str]:
    """
    Lists all available key names (without extension) in the KEY_DIR.

    Returns:
        List[str]: A list of key names.
    """
    if not os.path.exists(KEY_DIR):
        return []
    
    key_files = [f for f in os.listdir(KEY_DIR) if f.endswith(KEY_FILE_EXTENSION) and os.path.isfile(os.path.join(KEY_DIR, f))]
    return [os.path.splitext(f)[0] for f in key_files]

def delete_key(key_name: str) -> bool:
    """
    Deletes a key file from the KEY_DIR.

    Args:
        key_name (str): The name of the key to delete.

    Returns:
        bool: True if the key was deleted, False if it did not exist.
    """
    key_path = _get_key_path(key_name)
    if os.path.exists(key_path):
        os.remove(key_path)
        return True
    return False

def export_key(key_name: str, password: str) -> Optional[bytes]:
    """
    Encrypts and exports a key, protected by a password.

    Args:
        key_name (str): The name of the key to export.
        password (str): The password to protect the exported key.

    Returns:
        Optional[bytes]: The encrypted key data (salt + nonce + ciphertext), or None if the key doesn't exist.
    """
    raw_key = load_key(key_name)
    if not raw_key:
        return None

    # --- Key Derivation ---
    salt = os.urandom(16)
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=480000, # Recommended number of iterations
    )
    derived_key = kdf.derive(password.encode('utf-8'))
    
    # --- Encryption (AES-GCM) ---
    aesgcm = AESGCM(derived_key)
    nonce = os.urandom(12) # GCM recommended nonce size
    ciphertext = aesgcm.encrypt(nonce, raw_key, None) # No associated data

    # Return a single blob: salt + nonce + ciphertext
    return salt + nonce + ciphertext

def import_key(encrypted_data: bytes, password: str) -> Optional[bytes]:
    """
    Decrypts and imports a key that was protected by a password.

    Args:
        encrypted_data (bytes): The exported key data (salt + nonce + ciphertext).
        password (str): The password the key was protected with.

    Returns:
        Optional[bytes]: The raw decrypted key, or None if decryption fails.
    """
    try:
        # --- Extract data from the blob ---
        salt = encrypted_data[:16]
        nonce = encrypted_data[16:28] # 16 + 12
        ciphertext = encrypted_data[28:]

        # --- Key Derivation ---
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=480000,
        )
        derived_key = kdf.derive(password.encode('utf-8'))
        
        # --- Decryption (AES-GCM) ---
        aesgcm = AESGCM(derived_key)
        raw_key = aesgcm.decrypt(nonce, ciphertext, None)
        
        return raw_key
    except Exception:
        # Broad exception to catch any error during unpacking or decryption (e.g., wrong password)
        return None

# Example usage (for testing purposes, not part of the main app logic)
if __name__ == '__main__':
    print("Listing keys:", list_keys())

    try:
        # Generate a new key
        new_key_name = "test_key_1"
        print(f"Generating key '{new_key_name}'...")
        key = generate_key(new_key_name)
        print(f"Key '{new_key_name}' generated and saved. Raw key (first 8 bytes): {key[:8].hex()}...")

        # Load the key
        loaded_key = load_key(new_key_name)
        if loaded_key:
            print(f"Key '{new_key_name}' loaded. Raw key (first 8 bytes): {loaded_key[:8].hex()}...")
        else:
            print(f"Failed to load key '{new_key_name}'.")

        print("Listing keys after generation:", list_keys())

        # Try generating an existing key (should raise an error)
        try:
            generate_key(new_key_name)
        except ValueError as e:
            print(f"Attempted to re-generate '{new_key_name}': {e}")
        
        # Delete the key
        print(f"Deleting key '{new_key_name}'...")
        if delete_key(new_key_name):
            print(f"Key '{new_key_name}' deleted.")
        else:
            print(f"Failed to delete key '{new_key_name}'.")
        
        print("Listing keys after deletion:", list_keys())

    except Exception as e:
        print(f"An error occurred: {e}")
