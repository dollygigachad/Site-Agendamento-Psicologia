from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

print('\n=== TESTE 1: Criar Sala ===')
room_data = {"name":"Sala TestClient","description":"Teste in-process","capacity":5}
r = client.post('/api/rooms', json=room_data)
print('status:', r.status_code)
print('body:', r.text)

print('\n=== TESTE 2: Criar Paciente ===')
patient_data = {"name":"Paciente TestClient","email":"paciente.testclient@email.com","phone":"(44) 99999-1111","is_child":False}
r = client.post('/api/patients', json=patient_data)
print('status:', r.status_code)
print('body:', r.text)

print('\n=== TESTE 3: Criar Usuário ===')
user_data = {"name":"Usuario TestClient","email":"usuario.testclient@email.com","password":"senha12345","role":"student"}
r = client.post('/api/users', json=user_data)
print('status:', r.status_code)
print('body:', r.text)

print('\n=== TESTE 4: Criar Supervisor ===')
supervisor_data = {"name":"Supervisor TestClient","email":"supervisor.testclient@email.com","password":"senha12345","role":"professor"}
r = client.post('/api/users', json=supervisor_data)
print('status:', r.status_code)
print('body:', r.text)

print('\n=== TESTE 5: Criar Agendamento ===')
import datetime
from datetime import timezone, timedelta

# Ler ids criados
room = client.post('/api/rooms', json=room_data).json() if isinstance(r := client.post('/api/rooms', json=room_data), object) else None
# Use previous created objects (the initial posts) de fato retornaram antes; tentar obter via GET
rooms = client.get('/api/rooms').json()
patients = client.get('/api/patients').json()
users = client.get('/api/users').json()

if not rooms or not patients or not users:
	print('Não foi possível obter dados necessários para criar agendamento')
else:
	room_id = rooms[0]['id']
	patient_id = patients[0]['id']
	# localizar student e supervisor pelos emails
	student = next((u for u in users if u['email'] == user_data['email']), None)
	supervisor = next((u for u in users if u['email'] == supervisor_data['email']), None)
	if not student or not supervisor:
		print('Student ou supervisor não encontrados nos usuários retornados')
	else:
		start = (datetime.datetime.now(timezone.utc) + timedelta(hours=2)).isoformat()
		end = (datetime.datetime.now(timezone.utc) + timedelta(hours=3)).isoformat()
		ap_data = {
			'start_dt': start,
			'end_dt': end,
			'room_id': room_id,
			'patient_id': patient_id,
			'student_id': student['id'],
			'supervisor_id': supervisor['id'],
			'notes': 'Teste agendamento'
		}
		r = client.post('/api/appointments', json=ap_data)
		print('status:', r.status_code)
		try:
			print('body:', r.json())
		except Exception:
			print('body text:', r.text)
