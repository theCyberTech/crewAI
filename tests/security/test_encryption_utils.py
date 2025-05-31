import os
import pytest
from src.crewai.security.encryption_utils import encrypt, decrypt, DecryptionError # Assuming DecryptionError might be used later or was part of the original design. For now, ValueError is raised.

# Helper to generate a random key
def generate_key():
    return os.urandom(32)

class TestEncryptionUtils:
    def test_encrypt_decrypt_symmetric(self):
        """Test that data encrypted can be decrypted with the same key."""
        key = generate_key()
        plaintext = "This is a secret message. Sshhh!"

        encrypted_data = encrypt(plaintext, key)
        assert encrypted_data != plaintext, "Encrypted data should not be the same as plaintext."

        decrypted_data = decrypt(encrypted_data, key)
        assert decrypted_data == plaintext, "Decrypted data should match the original plaintext."

    def test_decrypt_invalid_key(self):
        """Test that decryption fails with an incorrect key."""
        key_a = generate_key()
        key_b = generate_key()
        while key_a == key_b: # Ensure keys are different
            key_b = generate_key()

        plaintext = "Another secret to guard."
        encrypted_data = encrypt(plaintext, key_a)

        with pytest.raises(ValueError) as excinfo:
            decrypt(encrypted_data, key_b)
        assert "Decryption failed" in str(excinfo.value), "Error message should indicate decryption failure."

    def test_decrypt_corrupted_data(self):
        """Test that decryption fails if the encrypted data is tampered with."""
        key = generate_key()
        plaintext = "Sensitive information here."
        encrypted_data_b64 = encrypt(plaintext, key)

        # Tamper with the encrypted data (decode, tamper, re-encode might be too complex here,
        # let's try a simpler modification of the base64 string)
        # A simple way to corrupt is to change a character in the base64 string.
        # This will likely lead to either a base64 decoding error or an InvalidTag error.
        if len(encrypted_data_b64) > 1:
            char_to_change = encrypted_data_b64[0]
            if char_to_change == 'A':
                corrupted_b64 = 'B' + encrypted_data_b64[1:]
            else:
                corrupted_b64 = 'A' + encrypted_data_b64[1:]
        else:
            corrupted_b64 = "corrupted_data" # Fallback if data is too short

        with pytest.raises(ValueError) as excinfo:
            decrypt(corrupted_b64, key)
        # The error could be "Invalid base64 input" or "Decryption failed: Invalid authentication tag"
        # or "Encrypted data is too short" depending on how corruption affects the payload.
        assert ("Invalid base64 input" in str(excinfo.value) or \
                "Decryption failed" in str(excinfo.value) or \
                "Encrypted data is too short" in str(excinfo.value)), \
                "Error message should indicate data corruption or decryption failure."

    def test_encrypt_requires_32_byte_key(self):
        """Test that encrypt function requires a 32-byte key."""
        plaintext = "Test data"
        short_key = os.urandom(16) # Not 32 bytes
        long_key = os.urandom(48) # Not 32 bytes

        with pytest.raises(ValueError) as excinfo_short:
            encrypt(plaintext, short_key)
        assert "Encryption key must be 32 bytes" in str(excinfo_short.value)

        with pytest.raises(ValueError) as excinfo_long:
            encrypt(plaintext, long_key)
        assert "Encryption key must be 32 bytes" in str(excinfo_long.value)

        with pytest.raises(ValueError) as excinfo_invalid_type:
            encrypt(plaintext, "not_bytes_key_neither_32_len__") #type: ignore
        assert "Encryption key must be 32 bytes" in str(excinfo_invalid_type.value)


    def test_decrypt_requires_32_byte_key(self):
        """Test that decrypt function requires a 32-byte key."""
        # We need some valid encrypted data first to test decryption against
        valid_key = generate_key()
        encrypted_data = encrypt("dummy data", valid_key)

        short_key = os.urandom(16) # Not 32 bytes
        long_key = os.urandom(48) # Not 32 bytes

        with pytest.raises(ValueError) as excinfo_short:
            decrypt(encrypted_data, short_key)
        assert "Decryption key must be 32 bytes" in str(excinfo_short.value)

        with pytest.raises(ValueError) as excinfo_long:
            decrypt(encrypted_data, long_key)
        assert "Decryption key must be 32 bytes" in str(excinfo_long.value)

        with pytest.raises(ValueError) as excinfo_invalid_type:
            decrypt(encrypted_data, "not_bytes_key_neither_32_len__") #type: ignore
        assert "Decryption key must be 32 bytes" in str(excinfo_invalid_type.value)

    def test_decrypt_invalid_base64_input(self):
        """Test decryption with invalid base64 input."""
        key = generate_key()
        invalid_b64_string = "This is not valid base64!@#$%^"
        with pytest.raises(ValueError) as excinfo:
            decrypt(invalid_b64_string, key)
        assert "Invalid base64 input" in str(excinfo.value)

    def test_decrypt_data_too_short(self):
        """Test decryption when payload is too short to contain nonce and tag."""
        key = generate_key()
        # Nonce (12) + Tag (16) = 28 bytes minimum. Base64 encodes 3 bytes to 4 chars.
        # So, a payload of less than ~ceil(28/3)*4 chars will be too short.
        # For simplicity, an empty string or very short string after base64 decode.
        short_payload_b64 = "short" # base64.b64encode(os.urandom(5)).decode('utf-8')

        with pytest.raises(ValueError) as excinfo:
            decrypt(short_payload_b64, key)
        # This might raise "Invalid base64 input" if not valid b64, or "Encrypted data is too short"
        assert ("Invalid base64 input" in str(excinfo.value) or \
                "Encrypted data is too short" in str(excinfo.value)), \
                "Error should indicate data is too short or invalid base64."

# To run these tests, you would typically use `pytest` in your terminal
# in the directory containing this file (or the project root).
# Example: pytest tests/security/test_encryption_utils.py
