# 🔧 Backend - Sistema de Agendamento UNIPAR

FastAPI backend com validações de negócio, autenticação JWT e persistência SQLite.

## 🚀 Quick Start

### Pré-requisitos
- Python 3.10+ (testado em 3.11, 3.13)
- PowerShell 5.1+ (Windows) ou bash (Linux/Mac)

### Instalação

1. **Criar ambiente virtual:**
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

2. **Instalar dependências:**
```powershell
pip install -r requirements.txt
```

3. **Criar e popular banco de dados:**
```powershell
python seed_data.py
```

### Executar Backend

```powershell
$env:PYTHONUNBUFFERED=1
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Acesso:**
- API: http://localhost:8000
- Docs Swagger: http://localhost:8000/docs
- Docs ReDoc: http://localhost:8000/redoc

## 📋 Estrutura

```
backend/
├── main.py              # Aplicação FastAPI principal
├── models.py            # SQLModel definitions
├── schemas.py           # Pydantic validation
├── database.py          # SQLite setup
├── service.py           # Business logic
├── repository.py        # Data access layer
├── security.py          # JWT auth & hashing
├── config.py            # Configuration
├── enums.py             # Enumerations
├── logger.py            # Logging
├── utils.py             # Utilities
├── routers/             # API endpoints
│   ├── auth.py         # Autenticação
│   ├── appointments.py # Agendamentos
│   ├── patients.py     # Pacientes
│   ├── rooms.py        # Salas
│   └── users.py        # Usuários
├── tests/              # Unit tests (16 testes)
├── requirements.txt    # Dependências
└── pytest.ini         # Pytest config
```

## 🧪 Testes

```powershell
python -m pytest tests/ -v
```

**Resultado esperado: 16/16 testes passando ✅**

## 🔐 Autenticação

### Registrar
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "João Silva",
    "email": "joao@unipar.br",
    "password": "senha123",
    "role": "student"
  }'
```

### Login
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "joao@unipar.br",
    "password": "senha123"
  }'
```

## 📚 API Endpoints

### Salas
- `GET /api/rooms` - Listar salas
- `POST /api/rooms` - Criar sala

### Pacientes
- `GET /api/patients` - Listar pacientes
- `POST /api/patients` - Criar paciente

### Usuários
- `GET /api/users` - Listar usuários
- `POST /api/users` - Criar usuário

### Agendamentos
- `GET /api/appointments` - Listar agendamentos
- `POST /api/appointments` - Criar agendamento (com validações)

## ✅ Validações

Cada agendamento passa por:
1. Datas válidas (fim após início)
2. Duração 30-120 minutos
3. Entidades existem e ativas
4. Sem conflitos (sala, estagiário, supervisor)
5. Estagiário ≤ 4h/dia

## 📝 Seed Data

Ao executar `python seed_data.py`:
- **3 salas**: Consultório 01, 02, Sala de Grupo
- **4 usuários**: Admin, 2 Professores, 1 Estagiário
- **4 pacientes**: Mix adultos/infantojuvenil

## 🚀 Deploy em Produção

```bash
# Com Gunicorn
gunicorn main:app -w 4 -b 0.0.0.0:8000

# Com Docker (exemplo)
docker run -p 8000:8000 agendamento-backend:latest
```

Recomendações:
1. Migrar para PostgreSQL
2. Usar Gunicorn/Nginx
3. Adicionar HTTPS
4. Rate limiting
5. Logging centralizado
