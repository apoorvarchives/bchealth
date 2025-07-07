class PatientHistoryTracker:
    def __init__(self):
        self.history = {}  # patient_id → list of reports

    def add_report(self, report_dict):
        pid = report_dict['patient_id']
        if pid not in self.history:
            self.history[pid] = []
        self.history[pid].append(report_dict)

    def get_history(self, patient_id):
        return self.history.get(patient_id, [])

    def print_history(self, patient_id):
        reports = self.get_history(patient_id)
        if not reports:
            print(f"\n❌ No records found for {patient_id}")
            return

        print(f"\n🩺 Patient History for {patient_id}:")
        for i, r in enumerate(reports, 1):
            vitals = ", ".join(f"{k}: {v}" for k, v in r['vitals'].items())
            print(
                f"\n  📄 Report #{i}\n"
                f"     Doctor    : {r['doctor_id']}\n"
                f"     Symptoms  : {r['symptoms']}\n"
                f"     Diagnosis : {r['diagnosis']}\n"
                f"     Vitals    : {vitals}\n"
                f"     Notes     : {r['notes']}\n"
            )
