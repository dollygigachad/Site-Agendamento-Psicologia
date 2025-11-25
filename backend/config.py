"""Configurações centralizadas da aplicação."""
from functools import lru_cache
from pydantic import Field, field_validator, ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Configurações da aplicação com validações."""
    
    # Banco de dados
    DATABASE_URL: str = Field(
        default="sqlite:///./agendamentotcc.db",
        description="URL de conexão do banco de dados"
    )
    
    # Segurança
    SECRET_KEY: str = Field(
        default="sua-chave-secreta-super-segura-aqui-mude-em-producao",
        description="Chave secreta para JWT (mude em produção)"
    )
    ALGORITHM: str = Field(
        default="HS256",
        description="Algoritmo de criptografia JWT"
    )
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=30,
        ge=1,
        description="Tempo de expiração do token em minutos"
    )
    
    # Aplicação
    DEBUG: bool = Field(
        default=True,
        description="Modo debug ativado"
    )
    LOG_LEVEL: str = Field(
        default="INFO",
        description="Nível de logging (DEBUG, INFO, WARNING, ERROR)"
    )
    
    # Regras de negócio
    MAX_STUDENT_HOURS_PER_DAY: int = Field(
        default=4,
        ge=1,
        le=24,
        description="Máximo de horas de atendimento por estagiário por dia"
    )
    MAX_APPOINTMENT_DURATION_MINUTES: int = Field(
        default=120,
        ge=30,
        description="Duração máxima de um agendamento em minutos"
    )
    MIN_APPOINTMENT_DURATION_MINUTES: int = Field(
        default=30,
        ge=15,
        description="Duração mínima de um agendamento em minutos"
    )

    model_config = ConfigDict(env_file=".env", case_sensitive=True)

    @field_validator("LOG_LEVEL")
    def validate_log_level(cls, v):
        """Valida se o LOG_LEVEL é válido."""
        valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        if v.upper() not in valid_levels:
            raise ValueError(f"LOG_LEVEL deve ser um de {valid_levels}")
        return v.upper()

    @field_validator("DATABASE_URL")
    def validate_database_url(cls, v):
        """Valida se a URL do banco está no formato correto."""
        if not v:
            raise ValueError("DATABASE_URL não pode estar vazio")
        return v


@lru_cache()
def get_settings() -> Settings:
    """Retorna instância em cache das configurações."""
    return Settings()

