# src/config.py

"""
Central configuration for the application.
This file contains static configuration values, such as the characters used
for zero-width encoding, to allow for easy modification without changing
core application logic.
"""

# --- Zero-Width Character Configuration ---

# The set of invisible characters used to encode the data.
# Using a distinct set of characters makes the decoding process more robust.

# Using Left-to-Right Mark as a start sentinel
ZW_START_CHAR = '\u200e'

# Using Right-to-Left Mark as an end sentinel
ZW_END_CHAR = '\u200f'

# Dictionary mapping binary digits to their zero-width representation
ZW_BINARY_MAP = {
    '0': '\u200b',  # Zero Width Space
    '1': '\u200c',  # Zero Width Non-Joiner
}

# A character to use for random padding to obfuscate the message length
ZW_PADDING_CHAR = '\u200d'  # Zero Width Joiner

# A reverse map for efficient decoding
ZW_REVERSE_BINARY_MAP = {v: k for k, v in ZW_BINARY_MAP.items()}

# --- UI and Application Configuration ---

APP_NAME = "InvisCrypt"
APP_VERSION = "1.1.0"
ORGANIZATION_NAME = "NullZero"
ORGANIZATION_DOMAIN = "nullzero.dev"

# --- Key Management Configuration ---
KEY_DIR = '.keys'
KEY_FILE_EXTENSION = '.key'
DEFAULT_KEY_SIZE_BYTES = 32  # 256-bit
