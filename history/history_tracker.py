import time # Import time for ctime

class PatientHistoryTracker:
    """
    Tracks and displays the health history for patients.
    Now stores block hash with each report and displays more details.
    """
    def __init__(self):
        # Stores reports as: patient_id -> list of {'report': report_dict, 'block_hash': hash}
        self.history = {}

    def add_report(self, report_dict, block_hash=None): # This line needs to be updated in your file
        """
        Adds a health report dictionary to the patient's history,
        along with the hash of the block it was included in.
        """
        pid = report_dict['patient_id']
        if pid not in self.history:
            self.history[pid] = []
        self.history[pid].append({'report': report_dict, 'block_hash': block_hash})

    def get_history(self, patient_id):
        """Returns the list of reports for a given patient ID."""
        return self.history.get(patient_id, [])

    def print_history(self, patient_id):
        """
        Prints the detailed health history for a given patient ID.
        Includes new fields and block hash.
        """
        reports_with_hashes = self.get_history(patient_id)
        if not reports_with_hashes:
            print(f"\n❌ No records found for {patient_id}")
            return

        print(f"\n🩺 Patient History for {patient_id}:")
        for i, entry in enumerate(reports_with_hashes, 1):
            r = entry['report']
            block_hash = entry['block_hash']
            vitals = ", ".join(f"{k}: {v}" for k, v in r['vitals'].items())
            
            # Safely get new fields using .get() for robustness
            medications = r.get('medications', 'N/A')
            allergies = r.get('allergies', 'N/A')
            follow_up_date = r.get('follow_up_date')
            hospital_clinic = r.get('hospital_clinic', 'N/A')
            patient_age = r.get('patient_age', 'N/A')
            patient_gender = r.get('patient_gender', 'N/A')

            follow_up_date_str = time.ctime(follow_up_date) if follow_up_date else 'N/A'

            print(
                f"\n  📄 Report #{i}\n"
                f"     Block Hash: {block_hash[:10]}...\n" if block_hash else "     Block Hash: N/A\n"
                f"     Timestamp : {time.ctime(r['timestamp'])}\n"
                f"     Doctor    : {r['doctor_id']}\n"
                f"     Hospital  : {hospital_clinic}\n" # New detail
                f"     Age       : {patient_age}\n"     # New detail
                f"     Gender    : {patient_gender}\n"   # New detail
                f"     Symptoms  : {r['symptoms']}\n"
                f"     Diagnosis : {r['diagnosis']}\n"
                f"     Vitals    : {vitals}\n"
                f"     Medications : {medications}\n"
                f"     Allergies   : {allergies}\n"
                f"     Follow-up   : {follow_up_date_str}\n"
                f"     Notes     : {r['notes']}\n"
            )

