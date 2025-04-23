import os
import json
import logging
import redis
from dotenv import load_dotenv
from typing import Any, Optional

# Configuração de logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Carrega variáveis de ambiente
load_dotenv()

class RedisCache:
    """
    Serviço de cache usando Redis com suporte a diferentes tipos de operações.
    """
    _instance = None

    def __new__(cls):
        """
        Implementação de Singleton para garantir uma única instância do Redis.
        """
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """
        Inicializa a conexão com o Redis usando a URL do .env.
        Suporta configurações de conexão flexíveis.
        """
        if hasattr(self, 'initialized'):
            return
        
        redis_url = os.getenv('REDIS_URL')
        if not redis_url:
            logger.warning("REDIS_URL não configurada. O cache será desativado.")
            self.client = None
            self.initialized = True
            return

        try:
            # Configurações padrão com possibilidade de override via URL
            self.client = redis.from_url(
                redis_url, 
                decode_responses=True,  # Converte automaticamente para string
                socket_timeout=5,        # Timeout de 5 segundos
                socket_connect_timeout=5 # Timeout de conexão de 5 segundos
            )
            
            # Testa a conexão
            self.client.ping()
            logger.info("Conexão com Redis estabelecida com sucesso.")
            
            self.initialized = True
        except Exception as e:
            logger.error(f"Erro ao conectar com Redis: {e}")
            self.client = None
            self.initialized = True

    def set(self, key: str, value: Any, expire: Optional[int] = None) -> bool:
        """
        Define um valor no cache.
        
        :param key: Chave para armazenar
        :param value: Valor a ser armazenado (será serializado para JSON)
        :param expire: Tempo de expiração em segundos (opcional)
        :return: Sucesso da operação
        """
        if not self.client:
            return False
        
        try:
            # Serializa o valor para JSON para suportar diferentes tipos
            serialized_value = json.dumps(value)
            
            if expire:
                result = self.client.setex(key, expire, serialized_value)
            else:
                result = self.client.set(key, serialized_value)
            
            return result
        except Exception as e:
            logger.error(f"Erro ao definir valor no cache: {e}")
            return False

    def get(self, key: str) -> Optional[Any]:
        """
        Recupera um valor do cache.
        
        :param key: Chave para buscar
        :return: Valor desserializado ou None
        """
        if not self.client:
            return None
        
        try:
            value = self.client.get(key)
            return json.loads(value) if value else None
        except Exception as e:
            logger.error(f"Erro ao recuperar valor do cache: {e}")
            return None

    def delete(self, key: str) -> bool:
        """
        Remove uma chave do cache.
        
        :param key: Chave a ser removida
        :return: Sucesso da operação
        """
        if not self.client:
            return False
        
        try:
            result = self.client.delete(key)
            return result > 0
        except Exception as e:
            logger.error(f"Erro ao deletar chave do cache: {e}")
            return False

    def clear(self) -> bool:
        """
        Limpa todo o cache.
        
        :return: Sucesso da operação
        """
        if not self.client:
            return False
        
        try:
            self.client.flushdb()
            return True
        except Exception as e:
            logger.error(f"Erro ao limpar o cache: {e}")
            return False

# Instância global para uso simples
redis_cache = RedisCache()