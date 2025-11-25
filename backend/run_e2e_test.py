#!/usr/bin/env python3
"""Script para rodar test E2E com backend em background."""
import time
import sys
import requests
from datetime import datetime, timedelta, timezone

BASE = 'http://localhost:8000'

def wait_for_backend(max_retries=20, timeout=2):
    """Aguardar backend estar pronto."""
    for attempt in range(max_retries):
        try:
            requests.get(f'{BASE}/', timeout=timeout)
            return True
        except:
            print(f"  Tentativa {attempt+1}/{max_retries}...", end='\r')
            time.sleep(1)
    return False

def run_test_e2e():
    """Executar teste E2E."""
    EMAIL = f'usuario_teste_{int(time.time())}@example.com'

    print("\n" + "="*70)
    print("  🧪 TESTE E2E: CRIAR USUÁRIO + AGENDAMENTO")
    print("="*70)

    # 1. Buscar dados de suporte
    print("\n1️⃣  Buscando dados de suporte...")
    rooms = requests.get(f'{BASE}/api/rooms').json()
    patients = requests.get(f'{BASE}/api/patients').json()
    users = requests.get(f'{BASE}/api/users').json()
    print(f"   ✓ {len(rooms)} salas encontradas")
    print(f"   ✓ {len(patients)} pacientes encontrados")
    print(f"   ✓ {len(users)} usuários encontrados\n")

    # 2. Registrar novo usuário
    print("2️⃣  Registrando novo usuário...")
    resp_register = requests.post(
        f'{BASE}/api/auth/register',
        json={
            'name': 'Usuário Teste E2E',
            'email': EMAIL,
            'password': 'senha_teste_123',
            'role': 'student'
        }
    )
    if resp_register.status_code == 200:
        user_data = resp_register.json()
        print(f"   ✓ Usuário criado com ID: {user_data.get('id')}")
        print(f"   ✓ Email: {user_data.get('email')}")
        print(f"   ✓ Role: {user_data.get('role')}\n")
    else:
        print(f"   ❌ Erro: {resp_register.status_code}")
        print(f"   {resp_register.text}\n")
        return False

    # 3. Criar agendamento
    print("3️⃣  Criando novo agendamento...")
    now = datetime.now(timezone.utc)
    start_dt = (now + timedelta(hours=2)).isoformat()
    end_dt = (now + timedelta(hours=3)).isoformat()

    # Escolher um supervisor válido (primeiro usuário ativo que não seja 'student')
    supervisor_id = None
    for u in users:
        role = (u.get('role') or '').lower()
        if role == 'professor' and u.get('is_active', True):
            supervisor_id = u['id']
            break
    if supervisor_id is None:
        # fallback: primeiro usuário ativo que não seja student
        for u in users:
            if (u.get('role') or '').lower() != 'student' and u.get('is_active', True):
                supervisor_id = u['id']
                break
        if supervisor_id is None:
            supervisor_id = users[1]['id'] if len(users) > 1 else users[0]['id']

    resp_appt = requests.post(
        f'{BASE}/api/appointments',
        json={
            'start_dt': start_dt,
            'end_dt': end_dt,
            'room_id': rooms[0]['id'],
            'patient_id': patients[0]['id'],
            'student_id': user_data['id'],
            'supervisor_id': supervisor_id,
            'notes': 'Agendamento criado por teste E2E'
        }
    )
    if resp_appt.status_code == 201:
        appt_data = resp_appt.json()
        print(f"   ✓ Agendamento criado com ID: {appt_data.get('id')}")
        print(f"   ✓ Sala: {rooms[0]['name']}")
        print(f"   ✓ Paciente: {patients[0]['name']}")
        print(f"   ✓ Status: {appt_data.get('status')}\n")
    else:
        print(f"   ❌ Erro: {resp_appt.status_code}")
        print(f"   {resp_appt.text}\n")
        return False

    # 4. Validar agendamento na lista
    print("4️⃣  Validando agendamento na lista...")
    appts = requests.get(f'{BASE}/api/appointments').json()
    if appts:
        last_appt = appts[-1]
        print(f"   ✓ Total de agendamentos: {len(appts)}")
        print(f"   ✓ Último agendamento ID: {last_appt.get('id')}")
        print(f"   ✓ Paciente: {last_appt.get('patient_name')}")
        print(f"   ✓ Sala: {last_appt.get('room_name')}\n")
    else:
        print(f"   ⚠️  Nenhum agendamento encontrado\n")

    print("="*70)
    print("  ✅ TESTE E2E CONCLUÍDO COM SUCESSO!")
    print("="*70 + "\n")
    return True

if __name__ == '__main__':
    print("\n⏳ Aguardando backend estar pronto...")
    if wait_for_backend():
        print("✓ Backend pronto!\n")
        success = run_test_e2e()
        sys.exit(0 if success else 1)
    else:
        print(f"\n❌ Backend não respondeu.")
        sys.exit(1)

