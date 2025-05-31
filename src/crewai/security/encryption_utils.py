"""Utility functions for encryption and decryption using AES-GCM."""

import base64
import os

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.exceptions import InvalidTag


def encrypt(data: str, key: bytes) -> str:
    """
    Encrypts data using AES-GCM.

    Args:
        data: The string data to encrypt.
        key: The encryption key (must be 32 bytes for AES-256).

    Returns:
        A base64 encoded string representing the nonce, ciphertext, and GCM tag.
    """
    if not isinstance(key, bytes) or len(key) != 32:
        raise ValueError("Encryption key must be 32 bytes.")

    nonce = os.urandom(12)  # GCM standard nonce size
    aesgcm = AESGCM(key)
    data_bytes = data.encode('utf-8')
    ciphertext = aesgcm.encrypt(nonce, data_bytes, None)  # No associated data

    # Concatenate nonce, ciphertext, and the GCM tag (which is appended by encrypt)
    # The tag is typically 16 bytes for AES-GCM.
    # AESGCM().encrypt() already appends the tag to the ciphertext.
    encrypted_payload = nonce + ciphertext # ciphertext already includes the tag

    return base64.b64encode(encrypted_payload).decode('utf-8')


def decrypt(encrypted_data_b64: str, key: bytes) -> str:
    """
    Decrypts data encrypted with AES-GCM.

    Args:
        encrypted_data_b64: The base64 encoded string of nonce, ciphertext, and tag.
        key: The decryption key (must be 32 bytes for AES-256).

    Returns:
        The original string data.

    Raises:
        ValueError: If decryption fails (e.g., invalid key, corrupted data, or invalid tag).
    """
    if not isinstance(key, bytes) or len(key) != 32:
        raise ValueError("Decryption key must be 32 bytes.")

    try:
        encrypted_payload = base64.b64decode(encrypted_data_b64)
    except base64.binascii.Error as e:
        raise ValueError(f"Invalid base64 input: {e}")


    if len(encrypted_payload) < 12 + 16: # Nonce (12) + minimum ciphertext (0) + Tag (16)
        raise ValueError("Encrypted data is too short to be valid.")

    nonce = encrypted_payload[:12]
    # Ciphertext includes the tag, which is the last 16 bytes
    ciphertext_with_tag = encrypted_payload[12:]

    aesgcm = AESGCM(key)

    try:
        decrypted_bytes = aesgcm.decrypt(nonce, ciphertext_with_tag, None) # No associated data
        return decrypted_bytes.decode('utf-8')
    except InvalidTag:
        raise ValueError("Decryption failed: Invalid authentication tag. Data may be corrupted or key incorrect.")
    except Exception as e:
        # Catch any other potential decryption errors
        raise ValueError(f"Decryption failed due to an unexpected error: {e}")

class DecryptionError(Exception):
    """Custom exception for decryption failures."""
    pass
