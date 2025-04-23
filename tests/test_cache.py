import os
import pytest
from motor_chat.data.cache import RedisCache

# Verifica se o Redis está configurado para testes
REDIS_URL = os.getenv('REDIS_URL')

@pytest.fixture
def redis_cache():
    """Fixture para criar uma instância de RedisCache para testes."""
    return RedisCache()

def test_redis_connection(redis_cache):
    """Testa a conexão básica com o Redis."""
    if not REDIS_URL:
        pytest.skip("REDIS_URL não configurada. Pulando testes de Redis.")
    
    assert redis_cache.client is not None, "Conexão com Redis não estabelecida"

def test_redis_set_and_get(redis_cache):
    """Testa definir e recuperar um valor no cache."""
    if not REDIS_URL:
        pytest.skip("REDIS_URL não configurada. Pulando testes de Redis.")
    
    # Testa com diferentes tipos de dados
    test_cases = [
        "test_string",
        42,
        {"key": "value"},
        [1, 2, 3],
        None
    ]
    
    for value in test_cases:
        key = f"test_key_{type(value).__name__}"
        
        # Define o valor
        result_set = redis_cache.set(key, value)
        assert result_set is True, f"Falha ao definir valor {value}"
        
        # Recupera o valor
        retrieved_value = redis_cache.get(key)
        assert retrieved_value == value, f"Valor recuperado não corresponde para {value}"

def test_redis_delete(redis_cache):
    """Testa a exclusão de uma chave do cache."""
    if not REDIS_URL:
        pytest.skip("REDIS_URL não configurada. Pulando testes de Redis.")
    
    key = "test_delete_key"
    value = "test_value"
    
    # Define o valor
    redis_cache.set(key, value)
    
    # Exclui a chave
    result_delete = redis_cache.delete(key)
    assert result_delete is True, "Falha ao excluir chave"
    
    # Verifica se o valor foi realmente excluído
    retrieved_value = redis_cache.get(key)
    assert retrieved_value is None, "Valor não foi excluído corretamente"

def test_redis_expiration(redis_cache):
    """Testa a expiração de chaves no cache."""
    if not REDIS_URL:
        pytest.skip("REDIS_URL não configurada. Pulando testes de Redis.")
    
    key = "test_expiration_key"
    value = "test_value"
    
    # Define o valor com expiração de 1 segundo
    redis_cache.set(key, value, expire=1)
    
    # Valor deve existir imediatamente
    retrieved_value = redis_cache.get(key)
    assert retrieved_value == value, "Valor não definido corretamente"
    
    # Espera 2 segundos para garantir a expiração
    import time
    time.sleep(2)
    
    # Valor deve ter expirado
    retrieved_value = redis_cache.get(key)
    assert retrieved_value is None, "Valor não expirou como esperado"

def test_redis_clear(redis_cache):
    """Testa a limpeza completa do cache."""
    if not REDIS_URL:
        pytest.skip("REDIS_URL não configurada. Pulando testes de Redis.")
    
    # Define alguns valores
    redis_cache.set("key1", "value1")
    redis_cache.set("key2", "value2")
    
    # Limpa o cache
    result_clear = redis_cache.clear()
    assert result_clear is True, "Falha ao limpar o cache"
    
    # Verifica se as chaves foram removidas
    assert redis_cache.get("key1") is None, "Chave1 não foi removida"
    assert redis_cache.get("key2") is None, "Chave2 não foi removida"