import os
import logging
import chromadb
from dotenv import load_dotenv
from typing import List, Dict, Optional, Any

# Configuração de logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Carrega variáveis de ambiente
load_dotenv()

class VectorStore:
    """
    Serviço de armazenamento de vetores usando ChromaDB.
    Suporta operações básicas de gerenciamento de coleções e embeddings.
    """
    _instance = None

    def __new__(cls):
        """
        Implementação de Singleton para garantir uma única instância do ChromaDB.
        """
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """
        Inicializa o cliente ChromaDB usando o caminho do .env.
        """
        if hasattr(self, 'initialized'):
            return
        
        chroma_path = os.getenv('CHROMA_DB_PATH')
        if not chroma_path:
            logger.warning("CHROMA_DB_PATH não configurado. O vector store será desativado.")
            self.client = None
            self.initialized = True
            return

        try:
            # Cria o diretório se não existir
            os.makedirs(chroma_path, exist_ok=True)
            
            # Inicializa o cliente ChromaDB
            self.client = chromadb.PersistentClient(path=chroma_path)
            logger.info(f"ChromaDB inicializado em: {chroma_path}")
            
            self.initialized = True
        except Exception as e:
            logger.error(f"Erro ao inicializar ChromaDB: {e}")
            self.client = None
            self.initialized = True

    def create_collection(self, name: str, metadata: Optional[Dict[str, str]] = None) -> Optional[Any]:
        """
        Cria uma nova coleção no ChromaDB.
        
        :param name: Nome da coleção
        :param metadata: Metadados opcionais para a coleção
        :return: Objeto da coleção ou None em caso de erro
        """
        if not self.client:
            logger.error("Cliente ChromaDB não inicializado.")
            return None
        
        try:
            # Verifica se a coleção já existe
            try:
                existing_collection = self.client.get_collection(name=name)
                logger.info(f"Coleção '{name}' já existe. Retornando a coleção existente.")
                return existing_collection
            except Exception:
                # Se a coleção não existe, continua com a criação
                pass
            
            # Garante que metadata não seja vazio (requisito do ChromaDB)
            if metadata is None:
                metadata = {"description": f"Collection {name}"}
            
            # Tenta criar a coleção
            collection = self.client.create_collection(
                name=name,
                metadata=metadata
            )
            
            logger.info(f"Coleção '{name}' criada com sucesso.")
            return collection
        except Exception as e:
            logger.error(f"Erro ao criar coleção {name}: {e}")
            logger.error(f"Tipo de erro: {type(e).__name__}")
            return None

    def get_or_create_collection(self, name: str, metadata: Optional[Dict[str, str]] = None) -> Optional[Any]:
        """
        Obtém uma coleção existente ou cria uma nova se não existir.
        
        :param name: Nome da coleção
        :param metadata: Metadados opcionais para a coleção
        :return: Objeto da coleção ou None em caso de erro
        """
        if not self.client:
            return None
        
        try:
            # Garante que metadata não seja vazio
            if metadata is None:
                metadata = {"description": f"Collection {name}"}
            
            collection = self.client.get_or_create_collection(
                name=name,
                metadata=metadata
            )
            logger.info(f"Coleção '{name}' obtida ou criada com sucesso.")
            return collection
        except Exception as e:
            logger.error(f"Erro ao obter/criar coleção {name}: {e}")
            return None

    def add_embeddings(self, 
                       collection_name: str, 
                       ids: List[str], 
                       embeddings: List[List[float]], 
                       metadatas: Optional[List[Dict[str, Any]]] = None, 
                       documents: Optional[List[str]] = None) -> bool:
        """
        Adiciona embeddings a uma coleção.
        
        :param collection_name: Nome da coleção
        :param ids: Lista de IDs únicos
        :param embeddings: Lista de embeddings
        :param metadatas: Metadados opcionais para cada embedding
        :param documents: Documentos de texto opcionais
        :return: Sucesso da operação
        """
        if not self.client:
            return False
        
        try:
            collection = self.client.get_collection(name=collection_name)
            collection.add(
                ids=ids,
                embeddings=embeddings,
                metadatas=metadatas or [{}] * len(ids),
                documents=documents
            )
            logger.info(f"Embeddings adicionados à coleção '{collection_name}'.")
            return True
        except Exception as e:
            logger.error(f"Erro ao adicionar embeddings à coleção {collection_name}: {e}")
            return False

    def query_embeddings(self, 
                         collection_name: str, 
                         query_embeddings: List[List[float]], 
                         n_results: int = 5) -> Optional[Dict[str, Any]]:
        """
        Consulta embeddings em uma coleção.
        
        :param collection_name: Nome da coleção
        :param query_embeddings: Lista de embeddings de consulta
        :param n_results: Número de resultados a retornar
        :return: Resultados da consulta ou None em caso de erro
        """
        if not self.client:
            return None
        
        try:
            collection = self.client.get_collection(name=collection_name)
            results = collection.query(
                query_embeddings=query_embeddings,
                n_results=n_results
            )
            return results
        except Exception as e:
            logger.error(f"Erro ao consultar embeddings na coleção {collection_name}: {e}")
            return None

    def delete_collection(self, name: str) -> bool:
        """
        Exclui uma coleção.
        
        :param name: Nome da coleção
        :return: Sucesso da operação
        """
        if not self.client:
            return False
        
        try:
            self.client.delete_collection(name=name)
            logger.info(f"Coleção '{name}' excluída com sucesso.")
            return True
        except Exception as e:
            logger.error(f"Erro ao excluir coleção {name}: {e}")
            return False

# Instância global para uso simples
vector_store = VectorStore()