import logging
from .config import get_settings

# Obter configurações via import relativo (funciona quando pacote é importado)
settings = get_settings()

# Configurar logging
logging.basicConfig(
    level=settings.LOG_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

