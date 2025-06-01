# RAG OpenSearch - Exemplo Completo com AWS Lambda, OpenAI e React

## Propósito do Projeto

Este projeto demonstra uma arquitetura completa de RAG (Retrieval Augmented Generation) utilizando AWS Lambda, OpenSearch, OpenAI e um front-end moderno inspirado no ChatGPT. O objetivo é servir como referência para desenvolvedores que desejam criar aplicações serverless de busca semântica e geração de respostas com integração de IA generativa.

![demonstração](/readme-images/Funcionamento.png)

- **Backend:** API Python FastAPI, empacotada como Lambda, indexa PDFs e responde perguntas usando embeddings e OpenAI.
- **Frontend:** React responsivo, interface tipo ChatGPT, upload de PDFs e consumo da API.
- **Infraestrutura:** Deploy automatizado via AWS SAM/CloudFormation e hospedagem do front-end no AWS Amplify.

![image](/readme-images/RAG%20OpenSearch.png)

## Serviços Utilizados
- **AWS Lambda** (Python 3.10)
- **AWS API Gateway** (com suporte a BinaryMediaTypes)
- **AWS OpenSearch** (Elasticsearch)
- **AWS Amplify** (hospedagem do front-end)
- **OpenAI API** (para geração de respostas)
- **FastAPI** (backend)
- **React + Vite** (frontend)

## Requisitos
- Conta AWS com permissões para Lambda, API Gateway, OpenSearch e Amplify
- Conta OpenAI com chave de API
- Node.js 18+ e npm
- Python 3.10+
- AWS CLI e AWS SAM CLI

## Como rodar localmente

### 1. Clone o repositório
```sh
git clone https://github.com/seu-usuario/rag-opensearch.git
cd rag-opensearch
```

### 2. Configure as variáveis de ambiente
- Copie os arquivos de exemplo:
  - `cp rag-opensearch-dev-eus/.env.example rag-opensearch-dev-eus/.env`
  - `cp rag-opensearch-dev-eus/.env.json.example rag-opensearch-dev-eus/.env.json`
  - `cp rag-opensearch-dev-eus/.template.yaml.example rag-opensearch-dev-eus/template.yaml`
  - `cp rag-opensearch-react/.amplify.yml.example rag-opensearch-react/amplify.yml`
- Preencha os valores reais das variáveis:
  - `OPENAI_API_KEY`, `elasticsearch_url`, `elasticsearch_apikey`, `index_name`, `AMPLIFY_URL`

### 3. Backend (FastAPI/Lambda)
- Instale dependências:
  ```sh
  cd rag-opensearch-dev-eus/rag-opensearch
  python -m venv .venv
  source .venv/bin/activate  # ou .venv\Scripts\activate no Windows
  pip install -r requirements.txt
  ```
- Para rodar localmente:
  ```sh
  uvicorn app:app --reload
  ```
- Para deploy na AWS:
  ```sh
  cd ..
  sam build
  sam deploy --guided
  ```

### 4. Frontend (React)
- Instale dependências:
  ```sh
  cd ../../rag-opensearch-react
  npm install
  ```
- Para rodar localmente:
  ```sh
  npm run dev
  ```
- Para deploy no Amplify:
  - Suba o projeto para um repositório GitHub
  - No console do Amplify, conecte o repositório e configure as variáveis de ambiente:
    - `VITE_API_URL` com o endpoint da API gerado pelo SAM

## Estrutura dos Endpoints
- `POST /index-pdf` — Upload de PDF para indexação semântica
- `POST /ask-model` — Pergunta para o modelo (RAG)

## Variáveis de Ambiente do OpenSearch

### O que é o OpenSearch?
OpenSearch é uma plataforma de busca, análise e visualização de dados open source, derivada do Elasticsearch 7.10 e Kibana 7.10, criada pela Amazon após a mudança de licenciamento do Elasticsearch. Ele permite indexar, buscar e analisar grandes volumes de dados em tempo real, sendo muito usado para logs, analytics, busca textual e aplicações de IA generativa (RAG, chatbots, etc).

### Diferença entre OpenSearch e Elasticsearch
- **Elasticsearch**: Projeto original, mantido pela Elastic, mas desde a versão 7.11 não é mais open source (mudou para SSPL).
- **OpenSearch**: Fork open source do Elasticsearch 7.10, mantido pela comunidade e AWS, com licenças Apache 2.0. Possui compatibilidade de API e recursos similares, mas evolui de forma independente.

### OpenSearch na AWS vs OpenSearch Open Source
- **OpenSearch AWS (Amazon OpenSearch Service):**
  - Serviço gerenciado, provisionado e escalado pela AWS.
  - Integração nativa com IAM, VPC, CloudWatch, snapshots automáticos, etc.
  - Billing por uso/hora, alta disponibilidade, upgrades automáticos.
  - URLs e autenticação gerenciadas pela AWS.
- **OpenSearch Open Source (https://opensearch.org/):**
  - Você mesmo instala, configura e gerencia o cluster (on-premises, VM, Docker, Kubernetes, etc).
  - Total controle sobre a infraestrutura, upgrades e plugins.
  - URLs, autenticação e segurança são de sua responsabilidade.
  - Sem custos de serviço, apenas infraestrutura.

### No seu projeto
Você está usando um cluster OpenSearch criado manualmente via https://opensearch.org/ (open source puro, não gerenciado pela AWS). Isso significa que:
- O endpoint (`elasticsearch_url`) é o endereço do seu cluster OpenSearch (pode ser um IP, domínio, etc).
- A autenticação (`elasticsearch_apikey`) é definida por você (API Key, Basic Auth, etc), não por IAM.
- Você é responsável por backups, upgrades, segurança e monitoramento.

### Variáveis de ambiente usadas
- **elasticsearch_url**: URL base do seu cluster OpenSearch (ex: `https://meu-cluster-opensearch:9200`)
- **elasticsearch_apikey**: Chave de API ou token de autenticação para acessar o cluster (se configurado)
- **index_name**: Nome do índice onde os dados (embeddings, textos) serão armazenados e buscados

> **Importante:**
> - Se usar OpenSearch na AWS, a autenticação e o endpoint mudam (IAM, VPC, etc).
> - Se usar OpenSearch open source, você tem total controle, mas também total responsabilidade pela segurança e disponibilidade.

Para mais detalhes, consulte: [OpenSearch.org](https://opensearch.org/) e [Documentação AWS OpenSearch](https://docs.aws.amazon.com/opensearch-service/latest/developerguide/what-is.html)

## Criação do Índice e Mapeamento no OpenSearch

O código abaixo é responsável por criar o índice e o mapeamento necessário para armazenar textos e embeddings vetoriais no OpenSearch:

```python
def creating_map(self):
    self.client.indices.create(
        index=self.index_name,
        mappings={
            "properties": {
                "titulo": { "type": "text" },
                "conteudo": { "type": "text" },
                "embedding": {
                    "type": "dense_vector",
                    "dims": 1536,
                    "index": True,
                    "similarity": "cosine"
                }
            }
        }
    )
```

- **O que faz:** Cria um índice no OpenSearch com três campos:
  - `titulo`: texto do título do documento
  - `conteudo`: texto do conteúdo do documento
  - `embedding`: vetor denso de 1536 dimensões (compatível com embeddings do OpenAI), indexado para busca vetorial (KNN) usando similaridade cosseno
- **Quando usar:**
  - Este método **não é chamado automaticamente pela API**. Ele só precisa ser executado uma vez, antes de indexar qualquer documento, para criar o índice e o mapeamento correto no OpenSearch.
  - Se for a primeira vez rodando o projeto, execute manualmente o arquivo onde está esse método (por exemplo, rode `python src/OpenSearch/configuration.py`) para criar o índice.
- **Importante:**
  - Se o índice já existir, não é necessário rodar novamente.
  - Se mudar a estrutura do embedding (ex: tamanho do vetor), será necessário recriar o índice.

> **Dica:** Sempre verifique se o índice existe antes de tentar indexar documentos, para evitar erros de mapeamento.

## Observações de Segurança
- **Nunca suba arquivos reais de ambiente ou template com segredos.**
- Use apenas arquivos `.example` para versionamento.
- O projeto já está com `.gitignore` seguro para ambientes públicos.

---

Desenvolvido por [Antonny](https://www.linkedin.com/in/antonnymendonca/).
