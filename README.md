# Motor de Chat Contextual Inteligente v1.0 (MVP)

Este projeto implementa um backend para um chatbot inteligente que utiliza técnicas de Geração Aumentada por Recuperação (RAG) e Geração Aumentada por Contexto (CAG). Ele fornece uma API para interagir com o chatbot, que responde a perguntas com base em uma base de conhecimento configurável.

## Funcionalidades Principais

- API RESTful para interagir com o chatbot (`POST /api/v1/chat`)
- Uso de embeddings para buscar contexto relevante em uma base de conhecimento
- Geração de respostas usando modelos de linguagem da OpenAI
- Cache para otimizar chamadas repetitivas à API da OpenAI
- Registro do histórico de conversas em um banco de dados MySQL

## Arquitetura e Stack Tecnológico

- **Estilo Arquitetural:** Monolítico Simplificado
- **Framework Web/API:** Flask (Python)
- **Orquestração RAG/CAG:** LangChain (Python)
- **Banco Vetorial:** ChromaDB
- **Banco Relacional:** MySQL
- **Cache:** Redis
- **Modelos de IA:** OpenAI API (embeddings e LLM)
- **Containerização:** Docker
- **Orquestração Local:** Docker Compose

## Como Rodar Localmente

1. Clone o repositório:
   ```
   git clone https://github.com/seu-usuario/seu-repositorio.git
   cd seu-repositorio
   ```

2. Configure as variáveis de ambiente (ex: chaves da API da OpenAI) em um arquivo `.env`.

3. Inicie os serviços com Docker Compose:
   ```
   docker-compose up --build
   ```

4. A API estará disponível em `http://localhost:5000/api/v1/chat`

## Uso da API

Para interagir com o chatbot, envie uma requisição POST para `/api/v1/chat` com o seguinte corpo:

```json
{
    "session_id": "sua-sessao-unica",
    "message": "Sua pergunta aqui"
}
```

Exemplo de resposta:

```json
{
    "response": "Resposta gerada pelo chatbot",
    "session_id": "sua-sessao-unica"
}
```

Em caso de erro:

```json
{
    "error": "Mensagem de erro"
}
```

## Status do Projeto

Este é um MVP (Produto Mínimo Viável) focado em validar a lógica central do chatbot. Funcionalidades adicionais, como interfaces de usuário e gerenciamento avançado de contexto, serão implementadas em versões futuras.