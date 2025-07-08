import random
import time
import json
import base64 # Import base64 for encoding/decoding bytes
from Signatures import sign, verify, deserialize_public_key, serialize_public_key

class HealthReport:
    """
    Represents a health report, now including fields for doctor's signature
    and public key to ensure authenticity and integrity.
    Added new fields: medications, allergies, follow_up_date,
    hospital_clinic, patient_age, patient_gender.
    """
    def __init__(self, patient_id, doctor_id, symptoms, diagnosis, vitals, notes,
                 medications, allergies, follow_up_date, hospital_clinic, patient_age, patient_gender,
                 doctor_public_key_serialized=None, signature=None, timestamp=None):
        self.patient_id = patient_id
        self.doctor_id = doctor_id
        self.symptoms = symptoms
        self.diagnosis = diagnosis
        self.vitals = vitals
        self.notes = notes
        self.medications = medications
        self.allergies = allergies
        self.follow_up_date = follow_up_date
        self.hospital_clinic = hospital_clinic # New field
        self.patient_age = patient_age       # New field
        self.patient_gender = patient_gender   # New field
        self.timestamp = timestamp if timestamp is not None else time.time()
        self.doctor_public_key_serialized = doctor_public_key_serialized
        self.signature = signature # This can be bytes or a base64 string initially

    def to_dict(self, include_signature=True):
        """
        Converts the health report to a dictionary.
        Optionally excludes signature for signing purposes.
        Converts signature bytes to base64 string for JSON serialization.
        Includes new fields.
        """
        report_dict = {
            'patient_id': self.patient_id,
            'doctor_id': self.doctor_id,
            'symptoms': self.symptoms,
            'diagnosis': self.diagnosis,
            'vitals': self.vitals,
            'notes': self.notes,
            'medications': self.medications,
            'allergies': self.allergies,
            'follow_up_date': self.follow_up_date,
            'hospital_clinic': self.hospital_clinic, # New field
            'patient_age': self.patient_age,       # New field
            'patient_gender': self.patient_gender,   # New field
            'timestamp': self.timestamp,
            'doctor_public_key_serialized': self.doctor_public_key_serialized,
        }
        if include_signature and self.signature:
            # Convert signature bytes to base64 string for JSON serialization
            report_dict['signature'] = base64.b64encode(self.signature).decode('utf-8')
        elif include_signature and self.signature is None:
            report_dict['signature'] = None # Explicitly set to None if signature is not present
        return report_dict

    def get_message_for_signing(self):
        """
        Generates a consistent message string for signing,
        excluding the signature itself.
        """
        # Create a dictionary without the signature field
        report_data = self.to_dict(include_signature=False)
        # Convert to a JSON string and encode to bytes for signing
        return json.dumps(report_data, sort_keys=True).encode('utf-8')

    def sign_report(self, doctor_private_key):
        """
        Signs the health report using the doctor's private key.
        Sets the signature and the serialized public key of the doctor.
        """
        message = self.get_message_for_signing()
        self.signature = sign(message, doctor_private_key)
        # Ensure public key is serialized and stored with the report
        if self.doctor_public_key_serialized is None:
            pass # It should be set during generation

    def verify_signature(self):
        """
        Verifies the digital signature of the health report.
        Returns True if the signature is valid, False otherwise.
        """
        if not self.signature or not self.doctor_public_key_serialized:
            return False # Cannot verify without signature or public key

        try:
            # If signature is a base64 string, decode it back to bytes
            if isinstance(self.signature, str):
                signature_bytes = base64.b64decode(self.signature.encode('utf-8'))
            else: # Assume it's already bytes if not a string (e.g., just signed)
                signature_bytes = self.signature

            public_key = deserialize_public_key(self.doctor_public_key_serialized.encode('utf-8'))
            message = self.get_message_for_signing()
            return verify(message, signature_bytes, public_key)
        except Exception as e:
            # Log the error for debugging, but return False for verification failure
            print(f"Error verifying signature: {e}")
            return False

    @staticmethod
    def generate(patient_id, doctor_wallet):
        """
        Generates a random health report and signs it using the provided doctor's wallet.
        Includes new fields: medications, allergies, follow_up_date,
        hospital_clinic, patient_age, patient_gender.
        """
        symptoms_list = ["cough", "fever", "fatigue", "headache", "nausea", "sore throat", "dizziness"]
        diagnosis_list = ["flu", "cold", "migraine", "infection", "gastritis", "bronchitis", "allergies"]
        medications_list = ["Paracetamol", "Ibuprofen", "Amoxicillin", "Antihistamine", "Cough Syrup", "None", "Antibiotics"]
        allergies_list = ["Pollen", "Dust", "Penicillin", "None", "Pet Dander", "Food Allergies"]
        hospital_clinic_list = ["City General Hospital", "Community Health Clinic", "St. Jude's Medical Center", "Family Care Doctors"]
        gender_list = ["Male", "Female", "Other"]

        symptoms = random.choice(symptoms_list)
        diagnosis = random.choice(diagnosis_list)
        medications = random.choice(medications_list)
        allergies = random.choice(allergies_list)
        follow_up_date = (time.time() + random.randint(7, 30) * 24 * 3600) # 7 to 30 days from now
        hospital_clinic = random.choice(hospital_clinic_list)
        patient_age = random.randint(18, 80)
        patient_gender = random.choice(gender_list)

        vitals = {
            "BP": f"{random.randint(110, 140)}/{random.randint(70, 90)}",
            "HR": random.randint(60, 100),
            "SpO2": f"{random.randint(95, 100)}%",
            "Temp": f"{random.uniform(97.0, 102.0):.1f} F"
        }
        notes = random.choice([
            "Prescribed rest and fluids.",
            "Advised follow-up after 3 days.",
            "Recommended blood test.",
            "Referred to specialist.",
            "No critical signs.",
            "Patient responding well to treatment.",
            "Discussed lifestyle changes.",
            "Patient advised to avoid allergens."
        ])

        # Create the report instance
        report = HealthReport(
            patient_id=patient_id,
            doctor_id=doctor_wallet.doctor_id,
            symptoms=symptoms,
            diagnosis=diagnosis,
            vitals=vitals,
            notes=notes,
            medications=medications,
            allergies=allergies,
            follow_up_date=follow_up_date,
            hospital_clinic=hospital_clinic,
            patient_age=patient_age,
            patient_gender=patient_gender,
            doctor_public_key_serialized=doctor_wallet.get_public_key_serialized()
        )
        # Sign the report with the doctor's private key
        report.sign_report(doctor_wallet.get_private_key())
        return report

    @staticmethod
    def from_dict(report_dict):
        """
        Reconstructs a HealthReport object from a dictionary,
        useful when loading from blockchain data.
        Decodes signature from base64 string back to bytes.
        Includes new fields.
        """
        signature = report_dict.get('signature')
        # Decode signature from base64 string to bytes if it exists and is a string
        if isinstance(signature, str):
            signature = base64.b64decode(signature.encode('utf-8'))
        elif isinstance(signature, list): # Handle cases where JSON might convert bytes to list of ints
            signature = bytes(signature)

        return HealthReport(
            patient_id=report_dict['patient_id'],
            doctor_id=report_dict['doctor_id'],
            symptoms=report_dict['symptoms'],
            diagnosis=report_dict['diagnosis'],
            vitals=report_dict['vitals'],
            notes=report_dict['notes'],
            medications=report_dict.get('medications'),
            allergies=report_dict.get('allergies'),
            follow_up_date=report_dict.get('follow_up_date'),
            hospital_clinic=report_dict.get('hospital_clinic'), # New field
            patient_age=report_dict.get('patient_age'),       # New field
            patient_gender=report_dict.get('patient_gender'),   # New field
            timestamp=report_dict['timestamp'],
            doctor_public_key_serialized=report_dict['doctor_public_key_serialized'],
            signature=signature
        )

