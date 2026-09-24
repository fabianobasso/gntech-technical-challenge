# GnTech Technical Challenge

API REST desenvolvida em Python com Django REST Framework para o desafio técnico da GnTech.

A aplicação consulta dados meteorológicos atuais através da OpenWeather, armazena os resultados em PostgreSQL e disponibiliza os registros através de uma API REST documentada com Swagger/OpenAPI.

## Tecnologias

- Python 3.12
- Django
- Django REST Framework
- PostgreSQL
- Docker
- Docker Compose
- OpenWeather API
- drf-spectacular / OpenAPI
- Swagger UI

## Arquitetura

O fluxo principal da aplicação é:

```text
Cliente
   |
   v
Django REST API
   |
   +------> WeatherService ------> OpenWeather API
   |
   v
PostgreSQL
```

A integração com o serviço externo foi isolada em uma camada de serviço, evitando que a lógica de comunicação com a OpenWeather fique acoplada às views da API.

Os dados retornados pela API externa são normalizados e armazenados localmente antes de serem disponibilizados pelos endpoints de consulta.

## Funcionalidades

A aplicação permite:

- consultar o clima atual de uma cidade através da OpenWeather;
- armazenar os dados meteorológicos no PostgreSQL;
- listar os registros armazenados;
- consultar um registro específico;
- documentar e testar os endpoints através do Swagger UI;
- executar a aplicação e o banco de dados através do Docker Compose;
- executar automaticamente as migrations durante a inicialização do container da API.

## Configuração

Clone o repositório:

```bash
git clone git@github.com:fabianobasso/gntech-technical-challenge.git
cd gntech-technical-challenge
```

Crie o arquivo de configuração a partir do exemplo:

```bash
cp .env.example .env
```

Configure no `.env` a sua chave da OpenWeather:

```env
WEATHER_API_KEY=sua_chave_aqui
```

Uma chave pode ser obtida no serviço OpenWeather.

Para execução local do desafio, as demais variáveis já possuem valores padrão funcionais e não precisam ser alteradas. Em um ambiente de produção, valores sensíveis como DJANGO_SECRET_KEY e POSTGRES_PASSWORD devem ser substituídos por credenciais seguras.

> O arquivo `.env` não é versionado e não deve ser enviado ao repositório.

## Executando com Docker

Com Docker e Docker Compose instalados, execute:

```bash
docker compose up --build
```

O Docker Compose irá:

1. iniciar o PostgreSQL;
2. aguardar o banco ficar disponível;
3. iniciar o container da aplicação;
4. executar automaticamente as migrations;
5. iniciar o servidor Django.

A API ficará disponível em:

```text
http://127.0.0.1:8000
```

A documentação Swagger estará disponível em:

```text
http://127.0.0.1:8000/api/docs/
```

Para encerrar:

```bash
docker compose down
```

Para encerrar e remover também o volume do banco:

```bash
docker compose down -v
```

## Executando localmente

Crie o ambiente virtual:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Instale as dependências:

```bash
pip install -r requirements.txt
```

Para utilizar o PostgreSQL através do Docker:

```bash
docker compose up -d db
```

Execute as migrations:

```bash
python manage.py migrate
```

Inicie a aplicação:

```bash
python manage.py runserver
```

## Endpoints

### Coletar e armazenar dados meteorológicos

```http
POST /api/weather/fetch/
```

Exemplo de requisição:

```json
{
  "city": "Florianopolis,BR"
}
```

A cidade é enviada dinamicamente para a OpenWeather. A aplicação utiliza a API key configurada no ambiente para autenticar a chamada externa.

Exemplo de resposta:

```json
{
  "id": 1,
  "city": "Florianópolis",
  "country": "BR",
  "temperature": "18.38",
  "feels_like": "18.28",
  "humidity": 77,
  "pressure": 1017,
  "weather": "céu limpo",
  "collected_at": "2026-09-24T21:36:00Z",
  "created_at": "2026-09-24T21:37:32Z"
}
```

### Listar registros

```http
GET /api/weather/
```

Retorna os registros meteorológicos armazenados no banco, ordenados pela data da coleta.

### Consultar um registro

```http
GET /api/weather/{id}/
```

Exemplo:

```http
GET /api/weather/1/
```

## Swagger / OpenAPI

A documentação interativa está disponível em:

```text
http://127.0.0.1:8000/api/docs/
```

O schema OpenAPI também pode ser acessado em:

```text
http://127.0.0.1:8000/api/schema/
```

Os endpoints podem ser executados diretamente pela interface do Swagger.

## Banco de dados

Os dados meteorológicos são armazenados na tabela `weather_weatherrecord`.

Os principais campos são:

| Campo | Descrição |
| --- | --- |
| `id` | Identificador do registro |
| `city` | Cidade retornada pela OpenWeather |
| `country` | Código do país |
| `temperature` | Temperatura em Celsius |
| `feels_like` | Sensação térmica |
| `humidity` | Umidade |
| `pressure` | Pressão atmosférica |
| `weather` | Descrição das condições meteorológicas |
| `collected_at` | Data/hora da observação na fonte |
| `created_at` | Data/hora de persistência na aplicação |

A separação entre `collected_at` e `created_at` permite distinguir o momento da observação fornecida pela fonte externa do momento em que o dado foi armazenado pela aplicação.

## Testes

Os testes automatizados podem ser executados com:

```bash
python manage.py test weather
```

Com a aplicação Docker em execução:

```bash
docker compose exec api python manage.py test weather
```

A suíte cobre os principais comportamentos da aplicação, incluindo:

- comunicação com o serviço meteorológico;
- persistência dos dados;
- coleta através do endpoint REST;
- validação de requisições;
- tratamento de cidade não encontrada;
- consulta dos registros armazenados.

As chamadas à API externa são simuladas durante os testes, evitando dependência de internet ou consumo da API da OpenWeather.

## Decisões técnicas

### Django REST Framework

Foi utilizado para estruturar os endpoints REST, serialização e validação dos dados.

### PostgreSQL

Foi escolhido como banco relacional para persistência dos registros meteorológicos.

### Camada de serviço

A comunicação com a OpenWeather foi isolada no `WeatherService`, mantendo separadas a integração externa e a camada HTTP da aplicação.

### Docker Compose

A aplicação e o PostgreSQL podem ser executados de forma reproduzível através do Docker Compose.

O banco possui healthcheck e a aplicação aguarda sua disponibilidade antes da inicialização. As migrations são aplicadas automaticamente pelo entrypoint da aplicação.

### Swagger / OpenAPI

A documentação é gerada com `drf-spectacular`, permitindo consultar o contrato da API e executar requisições diretamente pelo navegador.

## Estrutura principal

```text
.
├── config/
│   ├── settings.py
│   └── urls.py
├── weather/
│   ├── migrations/
│   ├── services/
│   │   └── weather_service.py
│   ├── models.py
│   ├── serializers.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
├── .env.example
├── .gitignore
├── docker-compose.yml
├── Dockerfile
├── entrypoint.sh
├── manage.py
├── requirements.txt
└── schema.yml
```

## Autor

Fabiano Basso Antonio