# 🏥 Sistema de Agendamento - UNIPAR

Sistema completo separado em **Backend** e **Frontend** para fácil manutenção e escalabilidade.

## 📁 Estrutura do Projeto

```
agendamentotcc/
├── backend/                      # 🔧 FastAPI Backend
│   ├── main.py                   # Aplicação principal
│   ├── models.py                 # SQLModel definitions
│   ├── schemas.py                # Pydantic validation
│   ├── service.py                # Business logic
│   ├── repository.py             # Data access layer
│   ├── database.py               # SQLite setup
│   ├── security.py               # JWT authentication
│   ├── routers/                  # API endpoints
│   ├── tests/                    # Unit tests (16 testes)
│   ├── requirements.txt
│   ├── pytest.ini
│   └── README.md                 # Documentação backend
│
├── frontend/                     # 🎨 Vanilla JS Frontend
│   ├── index.html                # Dashboard principal
│   ├── assets/
│   │   ├── css/style.css         # Estilos responsivos
│   │   └── js/app.js             # Lógica SPA
│   └── README.md                 # Documentação frontend
│
├── start_system.py               # 🚀 Script para iniciar tudo
├── DOCUMENTACAO.md               # 📚 Documentação completa
└── README.md                     # Este arquivo
```

## 🚀 Início Rápido (Tudo em Um Comando)

### Windows (PowerShell)
```powershell
cd c:\Users\HBK\Downloads\agendamentotcc
.venv\Scripts\Activate.ps1
python start_system.py
```

### Linux/Mac
```bash
cd agendamentotcc
source .venv/bin/activate
python start_system.py
```

## 🌐 Acesso Após Iniciar

| Componente | URL | Descrição |
|---|---|---|
| **Frontend** | http://localhost:3000 | Dashboard com 4 abas |
| **Backend** | http://localhost:8000 | API REST |
| **API Docs** | http://localhost:8000/docs | Swagger UI interativa |
| **ReDoc** | http://localhost:8000/redoc | Documentação ReDoc |

## 📦 Inicialização Automática

O script `start_system.py` automaticamente:
1. ✅ Recria banco de dados SQLite
2. ✅ Popula com dados de teste
3. ✅ Inicia Backend (uvicorn porta 8000)
4. ✅ Inicia Frontend (http.server porta 3000)

## 👀 Dados Iniciais Criados

### 🏢 Salas (3)
- Consultório 01 (capacidade: 2)
- Consultório 02 (capacidade: 2)
- Sala de Grupo (capacidade: 10)

### 👥 Usuários (4)
- Prof. João Silva (Professor)
- Prof. Maria Santos (Professor)
- Admin User (Administrador)
- Estagiário Teste (Estagiário/Estudante)

### 🏥 Pacientes (4)
- João Silva (Adulto)
- Maria Santos (Adulto)
- Pedro Costa (Infantojuvenil)
- Ana Oliveira (Adulto)

## 🔒 Credenciais para Teste

```json
{
  "email": "admin@clinica.com",
  "password": "admin123"
}
```

## 📚 Documentação Separada

### 🔧 Backend
- [backend/README.md](backend/README.md) - Guia completo do backend
- Configuração uvicorn
- Estrutura de rotas
- Testes unitários

### 🎨 Frontend
- [frontend/README.md](frontend/README.md) - Guia completo do frontend
- Estrutura JavaScript
- Integração com API
- Deploy em produção

## ✅ Validações Automáticas

Cada agendamento é validado:
1. ✓ Datas válidas (fim > início)
2. ✓ Duração 30-120 minutos
3. ✓ Entidades existem
4. ✓ Sem conflitos de horário
5. ✓ Estagiário ≤ 4h/dia

## 🧪 Testes

```powershell
# Navegar para backend
cd backend

# Executar testes
python -m pytest tests/ -v

# Resultado esperado: 16/16 testes ✅
```

## 🚀 Iniciar Backend Apenas

```powershell
cd backend
pip install -r requirements.txt
python -m uvicorn main:app --reload --port 8000
```

## 🌐 Iniciar Frontend Apenas

```powershell
cd frontend
python -m http.server 3000
```

## 🎯 Features

- ✅ **JWT Authentication** com roles
- ✅ **Validação de Conflitos** automática
- ✅ **Limites de Horário** para estagiários
- ✅ **Soft Delete** para agendamentos
- ✅ **Responsivo** (Mobile, Tablet, Desktop)
- ✅ **Zero Dependências** no Frontend
- ✅ **16 Testes** passando (100%)
- ✅ **CORS** habilitado
- ✅ **Logging** completo
- ✅ **Banco SQLite** para desenvolvimento

## 🔄 Workflow Típico

1. **Iniciar sistema**
   ```bash
   python start_system.py
   ```

2. **Acessar frontend**
   - Ir para http://localhost:3000

3. **Usar as 4 abas:**
   - **Agendamentos** - Criar, editar, deletar
   - **Pacientes** - Gerenciar pacientes
   - **Salas** - Gerenciar consultórios
   - **Usuários** - Gerenciar staff

4. **Parar sistema**
   - Pressionar Ctrl+C no terminal

## 🛠️ Troubleshooting

### "Cannot reach backend"
- Verificar se backend está rodando em :8000
- Abrir DevTools (F12) → Console
- Verificar requisições na aba Network

### "Port already in use"
- Backend: `lsof -i :8000` (Linux/Mac) ou `netstat -ano | findstr :8000` (Windows)
- Frontend: `lsof -i :3000` ou `netstat -ano | findstr :3000`

### Testes falhando
```bash
cd backend
pytest -v --tb=short
```

## 📚 Recursos Adicionais

- [DOCUMENTACAO.md](DOCUMENTACAO.md) - Documentação completa
- [backend/README.md](backend/README.md) - Guia técnico backend
- [frontend/README.md](frontend/README.md) - Guia técnico frontend
- http://localhost:8000/docs - API Swagger UI

## 🚀 Próximos Passos

### Desenvolvimento
- [ ] Adicionar mais validações
- [ ] Implementar filtros avançados
- [ ] Adicionar relatórios
- [ ] Sincronização em tempo real

### Production
- [ ] Migrar para PostgreSQL
- [ ] Usar Gunicorn/Nginx
- [ ] Adicionar HTTPS
- [ ] Implementar rate limiting
- [ ] Setup Docker

## 📝 Notas

- Frontend auto-refresh a cada 10 segundos
- Soft delete para agendamentos (não deleta, marca como inativo)
- Banco SQLite é ideal para desenvolvimento
- Para produção, usar PostgreSQL + Gunicorn

---


**Versão:** 1.0  
**Status:** 🟢 Production Ready  
**Data:** 23 de novembro de 2025
