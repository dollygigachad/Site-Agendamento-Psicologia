Guia de deploy — Site de Agendamento (frontend + backend)

Resumo rápido
- Frontend (estático): pode ser publicado no GitHub Pages diretamente a partir da pasta `frontend/`.
- Backend (FastAPI): publicar em qualquer serviço que rode Docker, por exemplo Render, Railway, ou em um container num provedor cloud.

O que já foi feito
- Workflow GitHub Actions adicionado para publicar `frontend/` em GitHub Pages (`.github/workflows/gh-pages.yml`).
- `backend/Dockerfile` adicionado para facilitar deploy do backend.

Publicar frontend (GitHub Pages)
1. O workflow `.github/workflows/gh-pages.yml` publica automaticamente a pasta `frontend/` quando houver push para a `main`.
2. Ative o GitHub Pages nas configurações do repositório: Settings → Pages → Branch: `gh-pages` (o action criará a branch `gh-pages`).

Publicar backend (opções)

A) Render (recomendado pela simplicidade)
1. Acesse https://render.com e crie uma conta.
2. New → Web Service → Connect to GitHub → selecione este repositório.
3. Configure:
   - Environment: Docker
   - Dockerfile Path: `backend/Dockerfile`
   - Port: `8000`
   - (Opcional) Environment variables: `DEBUG=false`, outras vars necessárias do `backend/config.py`.
4. Deploy automático será acionado a cada push na `main`.

B) Railway
1. Acesse https://railway.app e conecte ao GitHub.
2. Crie um novo projeto e escolha "Deploy from GitHub".
3. Configure para usar `backend/Dockerfile` ou escolha "Python" e defina o comando de start:
   `uvicorn backend.main:app --host 0.0.0.0 --port 8000`
4. Defina variáveis de ambiente necessárias.

C) Heroku (se preferir)
1. Crie um `Procfile` com: `web: uvicorn backend.main:app --host 0.0.0.0 --port $PORT`.
2. Faça deploy via Heroku Git ou GitHub integration. Note: Heroku não tem mais plano gratuito.

D) GitHub Actions + GitHub Container Registry (para serviços que puxam imagens)
1. Crie workflow que builda a imagem e faz push para `ghcr.io/OWNER/REPO:tag`.
2. Configure secrets `CR_PAT` (Personal Access Token) com permissão `write:packages`.
3. Em seguida configure o serviço de hosting para puxar essa imagem.

Variáveis de ambiente importantes
- `DATABASE_URL` (se usar DB externo)
- `SECRET_KEY` (se necessário)
- `DEBUG` (true/false)

Comandos locais úteis
- Build imagem Docker (local):

```powershell
cd C:\Users\HBK\Downloads\agendamentotcc
docker build -f backend/Dockerfile -t agendamento-backend:latest .
docker run -p 8000:8000 agendamento-backend:latest
```

Próximos passos que posso executar para você
- Criar workflow para buildar e publicar imagem Docker no GitHub Container Registry (requer token secreto).
- Ajudar a conectar e configurar Render/Railway (preciso que você forneça as credenciais/autorize o GitHub/Render).
- Ajustar variáveis de ambiente usadas pelo `backend/config.py` e adicionar instruções no repo.

Quer que eu:
- 1) Crie o workflow de build/push da imagem Docker para o GitHub Container Registry agora?
- 2) Ou preferiria que eu apenas confirme a publicação do frontend no GitHub Pages primeiro?
