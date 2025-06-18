# AutoSender

Sistema de automação para envio de mensagens em massa via WhatsApp Web usando **ASP.NET Core** e **Python**.

---

## Tecnologias

- **ASP.NET Core 8.0 MVC**
- **PostgreSQL**
- **Python + Selenium**
- **Entity Framework Core**

---

## Pré-requisitos

- [.NET 8.0 SDK](https://dotnet.microsoft.com/en-us/download/dotnet/8.0)
- [PostgreSQL](https://www.postgresql.org/download/)
- [Python 3.8+](https://www.python.org/downloads/)
- [Google Chrome](https://www.google.com/chrome/)

---

## Instalação

1. **Clone o repositório**
    ```bash
    git clone https://github.com/1nicolasj/AutoSender.git
    cd AutoSender
    ```

2. **Configure o banco PostgreSQL no `appsettings.json`**

3. **Execute as migrations**
    ```bash
    dotnet ef database update
    ```

4. **Configure o ambiente Python**
    ```bash
    cd WhatsAppService
    python -m venv venv
    venv\Scripts\activate   # (Windows)
    # Ou no Linux/Mac:
    # source venv/bin/activate
    pip install psycopg2-binary python-dotenv selenium webdriver-manager
    ```

5. **Crie o arquivo `.env` em `WhatsAppService/`**
    ```
    DB_HOST=localhost
    DB_NAME=AutoSenderDb
    DB_USER=postgres
    DB_PASSWORD=sua_senha
    DB_PORT=5432
    ```

6. **Execute o projeto**
    ```bash
    dotnet run
    ```

---

## Como Usar

1. Acesse [https://localhost:5126](https://localhost:5126)
2. Adicione contatos
3. Configure suas mensagens
4. Execute a automação
5. Escaneie o QR Code do WhatsApp
6. Acompanhe o progresso do envio

---

## Estrutura do Projeto

```
AutoSender/
├── Controllers/         # Controllers
├── Models/              # Models (entidades)
├── Views/               # Paginas Web
├── WhatsAppService/     # Automacao Python 
│   └── whatsapp_sender.py
└── wwwroot/             
```

---

## Funcionalidades

- Interface web para gestão de contatos
- Envio automático via WhatsApp Web
- Mensagens personalizadas por contato
- Sistema de retry automático

---