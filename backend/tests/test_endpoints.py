"""Testes de endpoints da API."""
import pytest
from fastapi.testclient import TestClient
from sqlmodel import create_engine, SQLModel, Session
from backend.main import app
from backend.database import get_session
from backend.models import User
from backend.security import hash_password
from backend.enums import UserRole

# Engine em memória
from sqlalchemy.pool import StaticPool

TEST_DB_URL = "sqlite:///:memory:"
# Use StaticPool so the in-memory DB is shared across threads/connections used by TestClient
test_engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False}, poolclass=StaticPool)

@pytest.fixture(scope="function")
def session():
    """Fixture de sessão para testes."""
    SQLModel.metadata.create_all(test_engine)
    with Session(test_engine) as session:
        # Criar usuário de teste
        admin = User(
            name="Admin Teste",
            email="admin@test.com",
            hashed_password=hash_password("senha123"),
            role=UserRole.ADMIN,
            is_active=True
        )
        session.add(admin)
        session.commit()
        yield session
    SQLModel.metadata.drop_all(test_engine)

@pytest.fixture
def client(session):
    """Fixture do client HTTP para testes."""
    def override_get_session():
        return session
    
    app.dependency_overrides[get_session] = override_get_session
    yield TestClient(app)
    app.dependency_overrides.clear()

def test_health_check(client):
    """Testa health check."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_root_endpoint(client):
    """Testa endpoint raiz."""
    response = client.get("/")
    assert response.status_code == 200
    assert "API de Agendamento" in response.json()["message"]

def test_register_user(client):
    """Testa registro de novo usuário."""
    response = client.post("/api/auth/register", json={
        "name": "Novo Usuário",
        "email": "novo@test.com",
        "password": "senha123",
        "role": "student"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "novo@test.com"
    assert data["role"] == "student"

def test_register_duplicate_email(client):
    """Testa registro com email duplicado."""
    client.post("/api/auth/register", json={
        "name": "User 1",
        "email": "duplicate@test.com",
        "password": "senha123",
        "role": "student"
    })
    
    response = client.post("/api/auth/register", json={
        "name": "User 2",
        "email": "duplicate@test.com",
        "password": "senha123",
        "role": "student"
    })
    
    assert response.status_code == 400
    body = response.json()
    assert ("já cadastrado" in body.get("detail", "")) or ("já cadastrado" in body.get("message", ""))

def test_login(client):
    """Testa login."""
    # Registrar usuário
    client.post("/api/auth/register", json={
        "name": "Login Test",
        "email": "login@test.com",
        "password": "senha123",
        "role": "student"
    })
    
    # Fazer login
    response = client.post("/api/auth/login", json={
        "email": "login@test.com",
        "password": "senha123"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_invalid_password(client):
    """Testa login com senha inválida."""
    client.post("/api/auth/register", json={
        "name": "Login Test",
        "email": "login2@test.com",
        "password": "senha123",
        "role": "student"
    })
    
    response = client.post("/api/auth/login", json={
        "email": "login2@test.com",
        "password": "senhaerrada"
    })
    
    assert response.status_code == 401
    body = response.json()
    assert ("incorretos" in body.get("detail", "")) or ("incorretos" in body.get("message", ""))

def test_create_room(client):
    """Testa criação de sala."""
    response = client.post("/api/rooms", json={
        "name": "Sala A",
        "description": "Sala de atendimento A",
        "capacity": 2
    })
    
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Sala A"
    assert data["active"] is True

def test_list_rooms(client):
    """Testa listagem de salas."""
    client.post("/api/rooms", json={
        "name": "Sala 1",
        "description": "Sala 1",
        "capacity": 1
    })
    
    response = client.get("/api/rooms")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[0]["name"] == "Sala 1"

def test_create_patient(client):
    """Testa criação de paciente."""
    response = client.post("/api/patients", json={
        "name": "Paciente Teste",
        "email": "paciente@test.com",
        "is_child": False
    })
    
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Paciente Teste"
    assert data["active"] is True


