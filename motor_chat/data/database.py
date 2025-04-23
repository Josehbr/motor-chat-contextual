import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("Variável de ambiente DATABASE_URL não definida.")

if DATABASE_URL.startswith("mysql://"):
    DATABASE_URL = DATABASE_URL.replace("mysql://", "mysql+mysqlconnector://", 1)
elif not DATABASE_URL.startswith("mysql+"):
     print(f"Atenção: DATABASE_URL não parece ser uma URL MySQL padrão SQLAlchemy: {DATABASE_URL}")

print(f"Usando DATABASE_URL: {DATABASE_URL}")

try:
    engine = create_engine(DATABASE_URL, pool_recycle=3600)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base = declarative_base()
    print("Motor SQLAlchemy criado e SessionLocal configurada.")

    with engine.connect() as connection:
        print("Conexão com o banco de dados estabelecida com sucesso.")

except Exception as e:
    print(f"Erro ao configurar ou conectar ao banco de dados: {e}")
    raise e

def get_db():
    """
    Função de dependência para obter uma sessão do banco de dados.
    Garante que a sessão seja fechada após o uso.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()