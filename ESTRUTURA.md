# 📊 Estrutura do Projeto - Separação Backend e Frontend

## 🎯 Organização Completa

```
agendamentotcc/
│
├── 🔧 BACKEND (backend/)
│   ├── main.py                    # FastAPI application principal
│   ├── config.py                  # Variáveis de ambiente e configuração
│   ├── database.py                # SQLite connection & setup
│   ├── models.py                  # SQLModel definitions (ORM)
│   ├── schemas.py                 # Pydantic schemas (validation/response)
│   ├── service.py                 # Business logic & validações
│   ├── repository.py              # Data access layer (queries)
│   ├── security.py                # JWT auth & password hashing
│   ├── enums.py                   # Enums (UserRole, etc)
│   ├── logger.py                  # Logging configuration
│   ├── utils.py                   # Utility functions
│   ├── conftest.py                # Pytest fixtures
│   │
│   ├── routers/                   # API Endpoints
│   │   ├── __init__.py
│   │   ├── auth.py               # POST /api/auth/register, /login
│   │   ├── appointments.py       # CRUD /api/appointments
│   │   ├── patients.py           # CRUD /api/patients
│   │   ├── rooms.py              # CRUD /api/rooms
│   │   └── users.py              # CRUD /api/users
│   │
│   ├── tests/                     # Unit & Integration Tests
│   │   ├── test_appointments.py  # Validações de agendamentos
│   │   ├── test_conflict.py      # Testes de conflitos
│   │   └── test_endpoints.py     # Testes de API
│   │
│   ├── requirements.txt           # Python dependencies
│   ├── pytest.ini                # Pytest configuration
│   └── README.md                 # Backend documentation
│
├── 🎨 FRONTEND (frontend/)
│   ├── index.html                # Dashboard principal (4 abas)
│   ├── index_backup.html         # Backup (removível)
│   │
│   ├── assets/
│   │   ├── css/
│   │   │   └── style.css         # Estilos responsivos (CSS3)
│   │   │
│   │   └── js/
│   │       └── app.js            # Lógica SPA (Vanilla JS ES6+)
│   │
│   └── README.md                 # Frontend documentation
│
├── 📚 RAIZ (Arquivos na raiz)
│   ├── README.md                 # Este arquivo (guia principal)
│   ├── DOCUMENTACAO.md           # Documentação completa consolidada
│   ├── start_system.py           # 🚀 Script para iniciar tudo
│   ├── .env                      # Variáveis de ambiente
│   ├── .gitignore                # Git ignore rules
│   ├── agendamentotcc.db         # Banco SQLite (criado ao iniciar)
│   └── .venv/                    # Virtual environment Python
│
└── 🗂️ DIRETÓRIOS AUXILIARES
    ├── __pycache__/              # Cache Python
    ├── .pytest_cache/            # Cache Pytest
    └── scripts/                  # Scripts utilitários
```

## 🔀 Fluxo de Comunicação

```
┌─────────────────────────────────────────────────────────┐
│               FRONTEND (Port 3000)                      │
│                                                         │
│  index.html (4 abas)                                    │
│  ├── Agendamentos                                       │
│  ├── Pacientes                                          │
│  ├── Salas                                              │
│  └── Usuários                                           │
│                                                         │
│  assets/                                                │
│  ├── css/style.css (Responsivo)                         │
│  └── js/app.js (Vanilla JS)                             │
│       └── fetch() HTTP Requests                         │
└─────────────────────────────────────────────────────────┘
                         │
                         │ HTTP JSON
                         ▼
        ┌────────────────────────────────────┐
        │   CORS Middleware (Frontend:3000)  │
        └────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│               BACKEND (Port 8000)                       │
│                                                         │
│  main.py (FastAPI Application)                          │
│  ├── CORS Configuration                                 │
│  ├── Error Handlers                                     │
│  └── Route Registration                                 │
│                                                         │
│  routers/                                               │
│  ├── auth.py                                            │
│  │   ├── POST /api/auth/register                        │
│  │   └── POST /api/auth/login                           │
│  ├── appointments.py                                    │
│  │   ├── GET /api/appointments                          │
│  │   └── POST /api/appointments (com validações)        │
│  ├── patients.py                                        │
│  ├── rooms.py                                           │
│  └── users.py                                           │
│                                                         │
│  service.py (Business Logic)                            │
│  ├── Validações de conflitos                            │
│  ├── Limites de horário                                 │
│  └── Regras de negócio                                  │
│                                                         │
│  repository.py (Data Access)                            │
│  └── SQLAlchemy queries                                 │
│                                                         │
│  database.py                                            │
│  └── SQLite connection                                  │
└─────────────────────────────────────────────────────────┘
                         │
                         ▼
        ┌────────────────────────────────────┐
        │   SQLite Database                   │
        │   (agendamentotcc.db)               │
        │                                    │
        │   ├── users                         │
        │   ├── rooms                         │
        │   ├── patients                      │
        │   ├── appointments                  │
        │   └── ...                           │
        └────────────────────────────────────┘
```

## 📦 Dependências por Componente

### Backend (`backend/requirements.txt`)
```
fastapi==0.121.2
uvicorn==0.27.0
sqlmodel==0.0.27
sqlalchemy==2.0.44
pydantic==1.10.24
python-jose==3.3.0
passlib==1.7.4
pytest==8.2.2
```

### Frontend
```
Sem dependências externas!
✓ HTML5
✓ CSS3
✓ JavaScript ES6+
✓ Fetch API
```

## 🚀 Scripts de Inicialização

### 1. **start_system.py** (Raiz)
- Inicializa banco de dados
- Popular com seed data
- Inicia Backend (porta 8000)
- Inicia Frontend (porta 3000)

### 2. **backend/seed_data.py**
- Script para popular banco separadamente
- Cria 3 salas, 4 usuários, 4 pacientes

### 3. **backend/run_e2e_test.py**
- Testes end-to-end da API

## 📁 Locais Importantes

| Item | Localização | Propósito |
|------|-------------|----------|
| Backend Code | `backend/` | Todas as APIs |
| Frontend Code | `frontend/` | Interface web |
| Testes | `backend/tests/` | Unit tests |
| Banco de dados | `agendamentotcc.db` | SQLite storage |
| Start System | `start_system.py` | Iniciar tudo |
| Documentação | `DOCUMENTACAO.md` | Docs consolidada |
| Config | `.env` | Variáveis env |

## 🔄 Workflow de Desenvolvimento

1. **Modificar Backend?**
   - Edite arquivos em `backend/`
   - Não precisa reiniciar frontend

2. **Modificar Frontend?**
   - Edite `frontend/index.html` ou `frontend/assets/js/app.js`
   - Apenas refresh no navegador

3. **Testar API?**
   - http://localhost:8000/docs (Swagger UI)

4. **Rodar Testes?**
   ```bash
   cd backend
   pytest -v
   ```

## 🌐 URLs Importantes

| URL | Propósito |
|-----|-----------|
| http://localhost:3000 | Frontend dashboard |
| http://localhost:8000 | Backend API |
| http://localhost:8000/docs | Swagger UI (tester interativa) |
| http://localhost:8000/redoc | ReDoc (documentação) |
| http://localhost:8000/health | Health check |

## 📊 Estatísticas

- **Arquivos Python**: 20+
- **Rotas API**: 13+
- **Testes Unitários**: 16
- **Linhas de Código**: 4,800+
- **Linguagens**: Python, HTML, CSS, JavaScript

## ✅ Checklist para Novo Desenvolvedor

- [ ] Clone o projeto
- [ ] Crie `.venv` virtual environment
- [ ] Execute `pip install -r backend/requirements.txt`
- [ ] Execute `python start_system.py`
- [ ] Acesse http://localhost:3000
- [ ] Leia `DOCUMENTACAO.md` para contexto
- [ ] Leia `backend/README.md` para detalhes técnicos
- [ ] Execute `cd backend && pytest -v` para verificar testes

---

**Versão**: 1.0  
**Data**: 23 de novembro de 2025  
**Status**: 🟢 Production Ready
