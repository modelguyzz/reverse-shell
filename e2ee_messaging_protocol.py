import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.exceptions import InvalidTag


class E2EEMessagingProtocol:
    def __init__(self, key: bytes):
        """
        Initialize the protocol with a 256-bit (32-byte) shared key.

        Args:
            key (bytes): 32-byte shared secret key.
        """
        if not isinstance(key, bytes) or len(key) != 32:
            raise ValueError("Key must be 32 bytes (256 bits)")
        self.key = key
        self.aesgcm = AESGCM(self.key)

    def encrypt_message(self, plaintext: str) -> bytes:
        """
        Encrypt a message using AES-256 GCM.

        Args:
            plaintext (str): Message to encrypt.

        Returns:
            bytes: Concatenation of nonce and ciphertext (nonce || ciphertext).
        """
        # Encode plaintext to bytes
        data = plaintext.encode("utf-8")
        # Generate a unique 12-byte nonce
        nonce = os.urandom(12)
        # Encrypt the data with AES-GCM
        ciphertext = self.aesgcm.encrypt(nonce, data, associated_data=None)
        # Return nonce + ciphertext
        return nonce + ciphertext
        # made by modelguyzz

    
    def decrypt_message(self, encrypted_message: bytes) -> str:
        """
        Decrypt a message using AES-256 GCM.

        Args:
            encrypted_message (bytes): The concatenation of nonce and ciphertext.

        Returns:
            str: Decrypted plaintext.

        Raises:
            ValueError: If decryption fails or the message is tampered with.
        """
        if len(encrypted_message) < 12:
            raise ValueError("Encrypted message is too short to contain nonce")
        # Extract nonce (first 12 bytes)
        nonce = encrypted_message[:12]
        ciphertext = encrypted_message[12:]
        try:
            decrypted_data = self.aesgcm.decrypt(nonce, ciphertext, associated_data=None)
        except InvalidTag:
            raise ValueError("Invalid authentication tag. Message may be tampered with.")
        return decrypted_data.decode("utf-8")
