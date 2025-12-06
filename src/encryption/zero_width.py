import base64
import random
import re
from typing import Optional

from src.config import (
    ZW_START_CHAR,
    ZW_END_CHAR,
    ZW_BINARY_MAP,
    ZW_REVERSE_BINARY_MAP,
    ZW_PADDING_CHAR,
)

def encode_to_zero_width(text: str, padding_level: int = 3) -> str:
    """
    Encodes a string into a sequence of zero-width characters.

    The process:
    1.  Converts the input string to its binary representation (UTF-8).
    2.  Translates each '0' and '1' in the binary string to a specific
        zero-width character based on ZW_BINARY_MAP.
    3.  Inserts a random amount of padding characters at random positions
        to obfuscate the data length. The amount of padding is controlled
        by the padding_level.
    4.  Wraps the entire sequence with start and end sentinel characters.

    Args:
        text (str): The string to encode (e.g., a Base64 encoded string).
        padding_level (int): Controls the amount of random padding.
                             Higher numbers mean more padding.

    Returns:
        str: The invisible, zero-width encoded string.
    """
    # 1. Convert the string to a binary string representation.
    binary_string = ''.join(format(byte, '08b') for byte in text.encode('utf-8'))

    # 2. Translate binary string to zero-width characters.
    zero_width_list = [ZW_BINARY_MAP[bit] for bit in binary_string]

    # 3. Add randomized padding.
    if padding_level > 0:
        # Calculate number of padding chars to add, making it variable.
        num_padding_chars = len(zero_width_list) // max(1, 10 - padding_level)
        for _ in range(num_padding_chars):
            random_pos = random.randint(0, len(zero_width_list))
            zero_width_list.insert(random_pos, ZW_PADDING_CHAR)
    
    zero_width_string = "".join(zero_width_list)

    # 4. Wrap with start and end sentinels.
    return f"{ZW_START_CHAR}{zero_width_string}{ZW_END_CHAR}"


def decode_from_zero_width(text_with_hidden_message: str) -> Optional[str]:
    """
    Decodes a zero-width character sequence from a larger string.

    The process:
    1.  Finds the start and end sentinel characters in the input string.
    2.  Extracts the content between them.
    3.  Strips all padding characters from the extracted content.
    4.  Translates the remaining zero-width characters back into a binary string.
    5.  Converts the binary string back into a standard UTF-8 string.

    Args:
        text_with_hidden_message (str): A string potentially containing a
                                        hidden zero-width message.

    Returns:
        Optional[str]: The decoded string (e.g., a Base64 encoded string),
                       or None if no valid message is found.
    """
    try:
        # 1. Find and extract the message using a regular expression.
        # This is more robust than simple find/rfind.
        # The pattern looks for START_CHAR, followed by any characters (non-greedy),
        # and then the END_CHAR.
        pattern = f"{ZW_START_CHAR}(.*?){ZW_END_CHAR}"
        match = re.search(pattern, text_with_hidden_message)
        
        if not match:
            return None

        # 2. Extract the core zero-width message.
        zero_width_string = match.group(1)

        # 3. Remove all padding characters.
        cleaned_zw_string = zero_width_string.replace(ZW_PADDING_CHAR, '')

        # 4. Translate back to a binary string.
        binary_string = ''.join(ZW_REVERSE_BINARY_MAP[char] for char in cleaned_zw_string)

        # 5. Convert binary string back to bytes, then decode to a UTF-8 string.
        # The binary string is processed in 8-bit (byte) chunks.
        byte_list = [int(binary_string[i:i+8], 2) for i in range(0, len(binary_string), 8)]
        decoded_bytes = bytes(byte_list)
        
        return decoded_bytes.decode('utf-8')

    except (KeyError, TypeError, IndexError):
        # Catches errors from invalid characters, malformed binary, etc.
        return None
    except Exception:
        # Catch-all for any other unexpected errors during decoding.
        return None
