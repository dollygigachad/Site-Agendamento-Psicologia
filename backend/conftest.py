"""Configuração de testes - suprimir warnings seguros de bibliotecas."""
import warnings


def pytest_configure(config):
    """Configurar pytest para suprimir warnings conhecidos de bibliotecas."""
    # SQLModel usa datetime.utcnow() internamente - isso é um bug da biblioteca
    # não do nosso código, então podemos suprimir com segurança
    warnings.filterwarnings(
        "ignore",
        category=DeprecationWarning,
        module=".*sqlmodel.*"
    )

