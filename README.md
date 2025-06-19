# AutoSender

Sistema para envio automático de mensagens no WhatsApp Web. Feito com ASP.NET Core para gerenciar contatos e Python para automação.

## O que você precisa ter instalado

- [.NET 8.0](https://dotnet.microsoft.com/en-us/download/dotnet/8.0)
- [Python 3.8+](https://www.python.org/downloads/)
- [Google Chrome](https://www.google.com/chrome/) atualizado

## Como rodar

### 1. Baixe o projeto
```bash
git clone https://github.com/1nicolasj/AutoSender.git
cd AutoSender
```

### 2. Configure a aplicação web
```bash
cd AutoSender
dotnet ef database update
dotnet run
```

Agora você pode acessar http://localhost:5126 para cadastrar seus contatos.

### 3. Configure o Python
```bash
cd WhatsAppService
python -m venv .venv

# No Windows:
.\.venv\Scripts\Activate.ps1

pip install -r requirements.txt
```

## Como usar

1. **Cadastre contatos**: Abra http://localhost:5126 e adicione um nome, telefone e mensagem de cada pessoa
2. **Execute a automação**: No botao de automacao, o app vai rodar o script `python whatsapp_sender.py`
3. **Primeira vez**: Vai abrir o Chrome e pedir para escanear o QR Code do WhatsApp
4. **Próximas vezes**: Vai conectar automaticamente e enviar as mensagens

## O que faz

- Interface web simples para gerenciar contatos
- Salva tudo num banco SQLite
- Abre o WhatsApp Web automaticamente
- Envia mensagens com intervalos para nao ser bloqueado
- Lembra da sua sessao (nao precisa escanear QR toda vez)
- Mostra relatorio do que foi enviado

## Estrutura das pastas

```
AutoSender/
├── AutoSender/                 # Site para cadastrar contatos
├── WhatsAppService/           # Script que envia as mensagens
│   ├── whatsapp_sender.py     # Arquivo principal
│   └── requirements.txt       # Dependências do Python
```

## Funcionalidades

### Interface Web
- CRUD completo de contatos
- Interface com Bootstrap simples
- Banco SQLite integrado

### Automação Python
- Sessao persistente do WhatsApp (nao precisa escanear QR sempre)
- Intervalos entre mensagens
- Retry automatico em falhas
- Formataçao automatica de numeros brasileiros
- Relatorios de envio
- Detecçao de WhatsApp nao conectado

## Dependências Python

```txt
selenium==4.15.2
webdriver-manager==4.0.1
```

O `webdriver-manager` baixa automaticamente o ChromeDriver compatível.

## Solução de Problemas

### Erro de ativação do venv:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
.\.venv\Scripts\Activate.ps1
```

### WhatsApp não conecta:
- Feche o Chrome completamente
- Delete as pastas `chrome_user_data` e `whatsapp_session` se existirem
- Rode novamente

### Não encontra os contatos:
Certifique-se de que você rodou a aplicação web primeiro (`dotnet run`) para criar o banco de dados.