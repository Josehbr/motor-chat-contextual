# tests/test_database.py
import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError
import os
from dotenv import load_dotenv

# Carrega variáveis de ambiente para o teste
load_dotenv()

# Importa a configuração do banco de dados da sua aplicação
# Ajuste o caminho conforme a estrutura do seu projeto
try:
    from motor_chat.data.database import DATABASE_URL, engine as app_engine, SessionLocal as AppSessionLocal, get_db, Base
except ImportError:
    pytest.fail("Não foi possível importar de motor_chat.data.database. Verifique o caminho e a estrutura do projeto.")

# Pega a URL do banco de dados do ambiente, essencial para o teste
TEST_DATABASE_URL = os.getenv("DATABASE_URL")

@pytest.fixture(scope="session")
def test_engine():
    """Fixture para criar um engine de teste (escopo de sessão)."""
    if not TEST_DATABASE_URL:
        pytest.skip("DATABASE_URL não está definida no ambiente, pulando testes de banco de dados.")

    try:
        # Tenta criar o engine com a URL fornecida
        _engine = create_engine(TEST_DATABASE_URL, echo=False) # echo=True para debug
        # Tenta conectar para validar a URL e credenciais
        with _engine.connect() as connection:
            connection.execute(text("SELECT 1")) # Comando SQL simples para testar a conexão
        print("\nEngine de teste criado e conexão validada.")
        return _engine
    except OperationalError as e:
        pytest.fail(f"Falha ao conectar ao banco de dados de teste ({TEST_DATABASE_URL}): {e}")
    except Exception as e:
        pytest.fail(f"Erro inesperado ao criar engine de teste: {e}")

@pytest.fixture(scope="function")
def db_session(test_engine):
    """
    Fixture para criar uma sessão de banco de dados para cada teste (escopo de função).
    Usa uma transação que será revertida após o teste.
    """
    connection = test_engine.connect()
    # Inicia uma transação aninhada ou principal
    trans = connection.begin()
    # Cria uma sessão vinculada à conexão e transação
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=connection)
    session = TestingSessionLocal()
    print("\nSessão de teste criada dentro de uma transação.")

    try:
        yield session # Fornece a sessão para o teste
    finally:
        # Fecha a sessão
        session.close()
        # Faz rollback da transação para limpar quaisquer alterações feitas durante o teste
        trans.rollback()
        # Fecha a conexão
        connection.close()
        print("\nTransação revertida e conexão fechada.")

# --- Testes --- #

def test_database_url_configured():
    """Testa se a DATABASE_URL está configurada no módulo database."""
    assert DATABASE_URL is not None, "DATABASE_URL não foi carregada do .env ou ambiente no módulo database."
    print(f"DATABASE_URL encontrada no módulo: {DATABASE_URL}")
    assert TEST_DATABASE_URL is not None, "DATABASE_URL não foi carregada para os testes."
    print(f"TEST_DATABASE_URL encontrada para testes: {TEST_DATABASE_URL}")
    # Opcional: verificar se são iguais se esperado
    # assert DATABASE_URL == TEST_DATABASE_URL

def test_app_engine_exists():
    """Testa se o engine da aplicação foi criado."""
    assert app_engine is not None, "O engine da aplicação (app_engine) não foi criado em database.py."
    print("Engine da aplicação existe.")

def test_connection_fixture(test_engine):
    """Testa se a fixture test_engine estabelece uma conexão válida."""
    assert test_engine is not None, "Fixture test_engine falhou em retornar um engine."
    try:
        # Tenta obter uma conexão do engine de teste
        connection = test_engine.connect()
        # Executa uma consulta simples para verificar a conexão
        result = connection.execute(text("SELECT 1"))
        assert result.scalar_one() == 1, "A consulta de teste 'SELECT 1' falhou."
        print("Conexão com o banco de dados (via test_engine) verificada com sucesso.")
        connection.close()
    except OperationalError as e:
        pytest.fail(f"Não foi possível conectar ao banco de dados usando test_engine: {e}")
    except Exception as e:
        pytest.fail(f"Erro inesperado durante o teste de conexão com test_engine: {e}")

def test_get_db_fixture(db_session):
    """Testa a fixture db_session que simula o uso de get_db."""
    assert db_session is not None, "A sessão do banco de dados (db_session) não foi criada pela fixture."
    # Verifica se a sessão está ativa
    assert db_session.is_active, "A sessão do banco de dados (db_session) não está ativa."
    print("Sessão do banco de dados obtida com sucesso via fixture db_session.")

    # Simula uma operação simples dentro da sessão de teste
    try:
        result = db_session.execute(text("SELECT 'test_value'"))
        assert result.scalar_one() == 'test_value', "Falha ao executar consulta na sessão de teste."
        print("Consulta executada com sucesso na sessão de teste (db_session).")
    except Exception as e:
        pytest.fail(f"Erro ao executar consulta na sessão de teste (db_session): {e}")