import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

def testar_api_openai():
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("ERRO: OPENAI_API_KEY não encontrada nas variáveis de ambiente.")
        return

    client = OpenAI(api_key=api_key)

    try:
        modelos = client.models.list()
        print("A API da OpenAI está funcionando corretamente. Modelos disponíveis:")
        for modelo in modelos:
            print(f"- {modelo.id}")
    except Exception as e:
        print(f"Ocorreu um erro: {e}")

if __name__ == "__main__":
    testar_api_openai()