# wallets/doctor_wallet.py
from Signatures import generate_keys, serialize_public_key

class DoctorWallet:
    """
    Represents a doctor's wallet, holding their private and public keys
    for signing health reports.
    """
    def __init__(self, doctor_id):
        self.doctor_id = doctor_id
        self.private_key, self.public_key = generate_keys()
        # Store serialized public key for easy inclusion in reports
        self.public_key_serialized = serialize_public_key(self.public_key).decode()

    def get_public_key(self):
        """Returns the doctor's public key object."""
        return self.public_key

    def get_private_key(self):
        """Returns the doctor's private key object."""
        return self.private_key

    def get_public_key_serialized(self):
        """Returns the doctor's public key in a serialized (string) format."""
        return self.public_key_serialized

    def __str__(self):
        return f"DoctorWallet(ID: {self.doctor_id}, Public Key: {self.public_key_serialized[:10]}...)"

