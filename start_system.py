# -*- coding: utf-8 -*-
import sys
import time
import subprocess
from pathlib import Path
import hashlib
import io
import os

# Forçar UTF-8 em todas as streams
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
if sys.stderr.encoding != 'utf-8':
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
os.environ['PYTHONIOENCODING'] = 'utf-8'
# Em ambientes onde o arquivo de DB pode estar bloqueado por outro processo
# usar um banco em memória evita falhas na inicialização localmente.
os.environ.setdefault('AGENDA_USE_IN_MEMORY_DB', '1')

# Tentar importar módulos do backend; se faltar dependência, avisar claramente.
try:
    from backend.database import create_db_and_tables, get_session_context, DB_FILE
    from backend.models import Room, Patient, User
    from backend.enums import UserRole
except Exception as e:
    print("\n❌ Erro ao importar módulos do backend:")
    print(f"  {e}\n")
    print("Verifique se as dependências estão instaladas. Execute:")
    print("  pip install -r backend/requirements.txt")
    sys.exit(1)

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def recreate_and_seed():
    """Recriar banco e popular dados."""
    if DB_FILE.exists():
        try:
            DB_FILE.unlink()
        except PermissionError:
            print(f"  ⚠️ Não foi possível remover {DB_FILE}; está em uso por outro processo. Continuando sem recriar o arquivo.")
    create_db_and_tables()
    try:
        with get_session_context() as session:
            rooms_data = [
                {"name": "Consultório 01", "description": "Sala de consulta individual", "capacity": 2},
                {"name": "Consultório 02", "description": "Sala de consulta individual", "capacity": 2},
                {"name": "Sala de Grupo", "description": "Sala para atendimento em grupo", "capacity": 10},
            ]
            for room_data in rooms_data:
                session.add(Room(**room_data))
            users_data = [
                {"name": "Prof. João Silva", "email": "joao@clinica.com", "hashed_password": hash_password("senha123"), "role": UserRole.PROFESSOR, "is_active": True},
                {"name": "Prof. Maria Santos", "email": "maria@clinica.com", "hashed_password": hash_password("senha123"), "role": UserRole.PROFESSOR, "is_active": True},
                {"name": "Admin User", "email": "admin@clinica.com", "hashed_password": hash_password("admin123"), "role": UserRole.ADMIN, "is_active": True},
                {"name": "Estagiário Teste", "email": "estagiario@clinica.com", "hashed_password": hash_password("estagio123"), "role": UserRole.STUDENT, "is_active": True},
            ]
            for user_data in users_data:
                session.add(User(**user_data))
            patients_data = [
                {"name": "João Silva", "email": "joao.paciente@email.com", "phone": "(44) 99999-0001", "is_child": False, "active": True},
                {"name": "Maria Santos", "email": "maria.paciente@email.com", "phone": "(44) 99999-0002", "is_child": False, "active": True},
                {"name": "Pedro Costa", "email": "pedro.paciente@email.com", "phone": "(44) 99999-0003", "is_child": True, "active": True},
                {"name": "Ana Oliveira", "email": "ana.paciente@email.com", "phone": "(44) 99999-0004", "is_child": False, "active": True},
            ]
            for patient_data in patients_data:
                session.add(Patient(**patient_data))
            session.commit()
        return True
    except Exception:
        return False

def start_services():
    """Iniciar backend (uvicorn) e frontend (http.server) e retornar os processos."""
    # Executar uvicorn a partir da raiz do projeto e referenciar o módulo como
    # `backend.main:app` para evitar problemas com imports relativos.
    backend_cwd = Path(__file__).parent
    print("  ⏳ Iniciando backend (uvicorn)...")
    backend_proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"],
        cwd=str(backend_cwd),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    time.sleep(1)
    print(f"  ✓ Backend iniciado (PID: {backend_proc.pid})")
    print(f"    📍 http://localhost:8000")
    print(f"    📚 Docs: http://localhost:8000/docs\n")

    # Iniciar Frontend
    print("  ⏳ Iniciando frontend (http.server porta 3000)...")
    frontend_cwd = Path(__file__).parent / "frontend"
    frontend_proc = subprocess.Popen(
        [sys.executable, "-m", "http.server", "3000", "--directory", str(frontend_cwd)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    time.sleep(1)
    print(f"  ✓ Frontend iniciado (PID: {frontend_proc.pid})")
    print(f"    📍 http://localhost:3000\n")

    return backend_proc, frontend_proc

def main():
    """Função principal: recriar/semear DB e iniciar serviços."""
    try:
        print("\nInicializando banco de dados e seed...")
        if not recreate_and_seed():
            print("\n  ❌ Falha ao inicializar banco de dados!")
            sys.exit(1)

        backend_proc, frontend_proc = start_services()

        print("\n  ✅ SISTEMA INICIADO COM SUCESSO!")
        print("  🌐 URLs:")
        print("    • Frontend: http://localhost:3000")
        print("    • Backend:  http://localhost:8000")
        print("    • API Docs: http://localhost:8000/docs")
        print("\n  ℹ️  Pressione Ctrl+C para parar os serviços")

        try:
            while True:
                time.sleep(1)
                if backend_proc.poll() is not None or frontend_proc.poll() is not None:
                    print("\n⚠️  Processo encerrado. Saindo...")
                    break
        except KeyboardInterrupt:
            print("\n  🛑 Parando serviços...")
            backend_proc.terminate()
            frontend_proc.terminate()
            try:
                backend_proc.wait(timeout=5)
                frontend_proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                backend_proc.kill()
                frontend_proc.kill()
            print("  ✓ Serviços parados")

    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
