# automatizador_email_notion_todoist
Automatizador de Leitura de Emails e Integração no Notion e TodoIst

# Instalar

- pip install python-dotenv
- pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib

# Configurar API GMAIL

- Entrar em https://console.cloud.google.com/
- Criar um Projeto caso não exista
- Entrar no projeto
- Ir em APIs e Serviços(https://console.cloud.google.com/apis/library)
- Ativar a API do Gmail
- Ir em Credenciais(https://console.cloud.google.com/apis/credentials)
- Criar Credenciais de OAuth2, para computador
- Adicionar scope de APIS do GmailAPI
- Gravar arquivo de Credenciais no formato JSON

# Arquivo de .env

Crie um arquivo .env na raiz do projeto com as seguintes variáveis:

```
EMAIL=Email que será filtrado na caixa de entrada
ASSINATURA=Assinatura que será removida do corpo do email
```