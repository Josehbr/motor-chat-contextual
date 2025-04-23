import os
import pytest
import logging
import numpy as np
from motor_chat.data.vector_store import VectorStore

# Configura logging para mostrar mais detalhes durante o teste
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Verifica se o ChromaDB está configurado para testes
CHROMA_DB_PATH = os.getenv('CHROMA_DB_PATH')

@pytest.fixture
def vector_store():
    """Fixture para criar uma instância de VectorStore para testes."""
    store = VectorStore()
    
    # Log adicional para debug
    if store.client:
        logger.debug(f"ChromaDB Client inicializado em: {CHROMA_DB_PATH}")
    else:
        logger.error("Falha na inicialização do ChromaDB Client")
    
    return store

def test_chroma_connection(vector_store):
    """Testa a conexão básica com o ChromaDB."""
    if not CHROMA_DB_PATH:
        pytest.skip("CHROMA_DB_PATH não configurado. Pulando testes de ChromaDB.")
    
    assert vector_store.client is not None, "Conexão com ChromaDB não estabelecida"

def test_create_collection(vector_store):
    """Testa a criação de uma coleção."""
    if not CHROMA_DB_PATH:
        pytest.skip("CHROMA_DB_PATH não configurado. Pulando testes de ChromaDB.")
    
    # Gera um nome de coleção único para evitar conflitos
    import uuid
    collection_name = f"test_collection_{uuid.uuid4().hex}"
    
    # Cria a coleção com metadata obrigatório
    metadata = {"description": f"Test collection {collection_name}"}
    collection = vector_store.create_collection(collection_name, metadata=metadata)
    
    assert collection is not None, "Falha ao criar coleção"
    assert collection.name == collection_name, "Nome da coleção não corresponde"

def test_create_duplicate_collection(vector_store):
    """Testa a criação de uma coleção com nome duplicado."""
    if not CHROMA_DB_PATH:
        pytest.skip("CHROMA_DB_PATH não configurado. Pulando testes de ChromaDB.")
    
    collection_name = "duplicate_test_collection"
    metadata = {"description": "Test duplicate collection"}
    
    # Primeira criação
    collection1 = vector_store.create_collection(collection_name, metadata=metadata)
    assert collection1 is not None, "Falha na primeira criação da coleção"
    
    # Segunda criação (deve retornar a mesma coleção)
    collection2 = vector_store.create_collection(collection_name, metadata=metadata)
    assert collection2 is not None, "Falha na segunda criação da coleção"
    
    # Verifica se são a mesma coleção
    assert collection1.name == collection2.name, "Coleções com nomes diferentes"

def test_get_or_create_collection(vector_store):
    """Testa obter ou criar uma coleção."""
    if not CHROMA_DB_PATH:
        pytest.skip("CHROMA_DB_PATH não configurado. Pulando testes de ChromaDB.")
    
    collection_name = "test_get_or_create_collection"
    metadata = {"description": "Test get or create collection"}
    
    # Primeira chamada deve criar
    collection1 = vector_store.get_or_create_collection(collection_name, metadata=metadata)
    assert collection1 is not None, "Falha ao criar coleção na primeira chamada"
    
    # Segunda chamada deve retornar a mesma coleção
    collection2 = vector_store.get_or_create_collection(collection_name, metadata=metadata)
    assert collection2 is not None, "Falha ao obter coleção existente"
    
    # Verifica se são a mesma coleção
    assert collection1.name == collection2.name, "Coleções diferentes retornadas"

def test_add_and_query_embeddings(vector_store):
    """Testa adicionar e consultar embeddings."""
    if not CHROMA_DB_PATH:
        pytest.skip("CHROMA_DB_PATH não configurado. Pulando testes de ChromaDB.")
    
    collection_name = "test_embeddings_collection"
    metadata = {"description": "Test embeddings collection"}
    collection = vector_store.get_or_create_collection(collection_name, metadata=metadata)
    assert collection is not None, "Falha ao criar coleção para embeddings"
    
    # Gera embeddings de exemplo
    ids = ["id1", "id2", "id3"]
    embeddings = [
        [0.1, 0.2, 0.3],
        [0.4, 0.5, 0.6],
        [0.7, 0.8, 0.9]
    ]
    metadatas = [
        {"source": "doc1"},
        {"source": "doc2"},
        {"source": "doc3"}
    ]
    documents = ["First document", "Second document", "Third document"]
    
    # Adiciona embeddings
    result_add = vector_store.add_embeddings(
        collection_name,
        ids,
        embeddings,
        metadatas,
        documents
    )
    assert result_add is True, "Falha ao adicionar embeddings"
    
    # Consulta embeddings
    query_embedding = [[0.2, 0.3, 0.4]]
    results = vector_store.query_embeddings(collection_name, query_embedding)
    
    assert results is not None, "Falha ao consultar embeddings"
    assert "ids" in results, "Resultados não contêm IDs"
    assert "distances" in results, "Resultados não contêm distâncias"

def test_delete_collection(vector_store):
    """Testa a exclusão de uma coleção."""
    if not CHROMA_DB_PATH:
        pytest.skip("CHROMA_DB_PATH não configurado. Pulando testes de ChromaDB.")
    
    collection_name = "test_delete_collection"
    metadata = {"description": "Test delete collection"}
    
    # Cria a coleção
    collection = vector_store.create_collection(collection_name, metadata=metadata)
    assert collection is not None, "Falha ao criar coleção para exclusão"
    
    # Exclui a coleção
    result_delete = vector_store.delete_collection(collection_name)
    assert result_delete is True, "Falha ao excluir coleção"
    
    # Tenta criar novamente para confirmar que foi excluída
    new_collection = vector_store.create_collection(collection_name, metadata=metadata)
    assert new_collection is not None, "Falha ao recriar coleção após exclusão"