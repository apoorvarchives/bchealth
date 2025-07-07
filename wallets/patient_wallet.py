from Signatures import generate_keys

class PatientWallet:
    def __init__(self, patient_id):
        self.patient_id = patient_id
        self.private_key, self.public_key = generate_keys()

    def get_public_key(self):
        return self.public_key

    def get_private_key(self):
        return self.private_key
