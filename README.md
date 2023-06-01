# Automatizador de Leitura de Emails e Integração no Notion e TodoIst

# Objetivo
- Ler os emails de uma caixa de entrada
- Filtrar os emails por remetente
- Criar uma tarefa no TodoIst
- Criar uma página no Notion

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

# Exemplo do arquivo credentials

```json
{
	"installed": {
		"client_id": "ClientID do OAuth2",
		"project_id": "Nome do Projeto",
		"auth_uri": "https://accounts.google.com/o/oauth2/auth",
		"token_uri": "https://oauth2.googleapis.com/token",
		"auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
		"client_secret": "ClientSecret do OAuth2",
		"redirect_uris": ["http://localhost"]
	}
}
```

# Arquivo de .env

Crie um arquivo .env na raiz do projeto com as seguintes variáveis:

```
EMAIL=Email que será filtrado na caixa de entrada
ASSINATURA=Assinatura que será removida do corpo do email
```