# FastAPI-Keycloak

## Introdução

Primeiramente, execute o 'docker-compose up -d'

Isso irá permitir o acesso ao keycloak na url definida: localhost:8085/auth

O usuário e senha de administrador também estão definidos do docker-compose: keycloakuser, keycloakpassword

Em seguida, configure o Keycloak com base no tutorial em: 'https://fastapi-keycloak.code-specialist.com/keycloak_configuration/'

Os nomes que estão por padrão são: Realm = Test, Client = test-client. Caso crie os recursos com outros nomes, altere na API.


## Configuração da API

A configuração da API consiste em passar os devidos valores do parâmetro idp.

idp = FastAPIKeycloak(
        server_url="http://localhost:8085/auth",<br/>
        client_id="test-client",<br/>
        client_secret="Client Secret na seção Credentials do cliente que foi criado",<br/>
        admin_client_secret="Admin Client Secret na seção Credentials do cliente admin-cli",<br/>
        realm="Test",<br/>
        callback_uri="http://localhost:8081/callback"<br/>
)

Alem disso, deve-se copiar a public key do algoritmo RS256 contida em Realm Settings > Keys

SECRET_KEY = b'-----BEGIN PUBLIC KEY-----\n{Insira a chave aqui}\n-----END PUBLIC KEY-----'

Após isso, basta executar a API: uvicorn main:app
