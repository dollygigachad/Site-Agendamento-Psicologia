# 🎨 Frontend - Sistema de Agendamento UNIPAR

Interface web vanilla JavaScript/HTML/CSS para o sistema de agendamento.

## 🚀 Início Rápido

### Instalação

1. **Navegar para a pasta frontend:**
```powershell
cd frontend
```

2. **Iniciar servidor web local:**
```powershell
python -m http.server 3000
```

**Acesso:**
- Frontend: http://localhost:3000
- Backend: http://localhost:8000

## 📋 Estrutura

```
frontend/
├── index.html          # Dashboard com 4 abas
├── index_backup.html   # Backup (removível)
└── assets/
    ├── css/
    │   └── style.css   # Estilos responsivos
    └── js/
        └── app.js      # Lógica SPA (Vanilla JS)
```

## 📱 4 Abas Principais

1. **Agendamentos** 📅
   - CRUD com validação de conflitos
   - Filtros por sala, paciente, estagiário
   - Auto-refresh a cada 10 segundos

2. **Pacientes** 🏥
   - Gerenciamento de pacientes
   - Tipo: Adulto / Infantojuvenil
   - Contato e dados pessoais

3. **Salas** 🏢
   - Gerenciamento de consultórios
   - Nome, descrição, capacidade
   - Status ativo/inativo

4. **Usuários** 👥
   - Gerenciamento de roles
   - Admin, Professor, Estagiário
   - Ativação/desativação

## 🔧 Dependências

- **Nenhuma dependência externa!**
- Vanilla JavaScript (ES6+)
- HTML5
- CSS3 (Responsive Design)
- Fetch API para comunicação com backend

## 🎨 Recursos

- ✅ Responsivo (Mobile, Tablet, Desktop)
- ✅ Sem frameworks (Zero overhead)
- ✅ Auto-refresh a cada 10 segundos
- ✅ Validação de formulários no frontend
- ✅ UX amigável com feedback visual

## 📝 Comunicação com Backend

O frontend faz requisições HTTP para:

```javascript
// Exemplo: Listar pacientes
fetch('http://localhost:8000/api/patients')
  .then(r => r.json())
  .then(data => populateTable('patientsTable', data))

// Exemplo: Criar paciente
fetch('http://localhost:8000/api/patients', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(patient)
})
```

## 🌐 Configuração CORS

O backend CORS está habilitado para `http://localhost:3000`:

```python
# backend/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    ...
)
```

## 🚀 Deploy em Produção

### Opção 1: Nginx
```nginx
server {
    listen 80;
    server_name example.com;
    root /path/to/frontend;
    index index.html;
}
```

### Opção 2: Python HTTP Server
```bash
cd frontend
python -m http.server 80
```

### Opção 3: Node.js (http-server)
```bash
npm install -g http-server
cd frontend
http-server -p 80
```

### Opção 4: Docker
```dockerfile
FROM nginx:alpine
COPY . /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

## 🔐 CORS em Produção

Atualizar `backend/main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 📊 Integração com Backend

| Funcionalidade | Endpoint | Método |
|---|---|---|
| Listar agendamentos | `/api/appointments` | GET |
| Criar agendamento | `/api/appointments` | POST |
| Listar pacientes | `/api/patients` | GET |
| Criar paciente | `/api/patients` | POST |
| Listar salas | `/api/rooms` | GET |
| Criar sala | `/api/rooms` | POST |
| Listar usuários | `/api/users` | GET |
| Criar usuário | `/api/users` | POST |

## 🐛 Troubleshooting

### Erro: "Cannot reach backend"
- Verificar se backend está rodando em `http://localhost:8000`
- Verificar CORS no backend

### Erro: "CORS error"
- Confirmar que frontend está em `http://localhost:3000`
- Reiniciar servidor backend

### Dados não carregam
- Abrir DevTools (F12) → Console
- Verificar requisições na aba Network
- Confirmar resposta do backend

## 💡 Dicas

- Frontend auto-refresh: Edit `app.js` linha ~50 para mudar intervalo
- Adicionar logs: Abrir Console (F12) para ver requisições
- Testar API diretamente: Usar http://localhost:8000/docs
