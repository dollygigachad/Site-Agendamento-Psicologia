import sys
import os
from fastapi.testclient import TestClient

# Garantir que o diretório raiz do projeto esteja no caminho de importação
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
sys.path.insert(0, ROOT)

from backend.main import app
from datetime import datetime, timezone, timedelta


def run():
    with TestClient(app) as client:
        print('Health:', client.get('/health').json())

        rooms = client.get('/api/rooms').json()
        patients = client.get('/api/patients').json()
        students = client.get('/api/users/students').json()
        professors = client.get('/api/users/professors').json()

        print('Rooms:', rooms)
        print('Patients:', patients)
        print('Students:', students)
        print('Professors:', professors)

        if not (rooms and patients and students and professors):
            print('Dados insuficientes para criar agendamento')
            return

        room_id = rooms[0]['id']
        patient_id = patients[0]['id']
        student_id = students[0]['id']
        supervisor_id = professors[0]['id']

        now = datetime.now(timezone.utc)
        start_dt = (now + timedelta(hours=5)).isoformat()
        end_dt = (now + timedelta(hours=6)).isoformat()

        payload = {
            'start_dt': start_dt,
            'end_dt': end_dt,
            'room_id': room_id,
            'patient_id': patient_id,
            'student_id': student_id,
            'supervisor_id': supervisor_id,
            'notes': 'Teste de agendamento via TestClient'
        }

        r = client.post('/api/appointments', json=payload)
        print('Create appointment status:', r.status_code)
        try:
            print('Response:', r.json())
        except Exception:
            print('Response text:', r.text)


if __name__ == '__main__':
    run()
