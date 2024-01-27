# FastAPI-Keycloak
## Bibliotecas

pip install fastapi_keycloak<br/>
pip install pydantic==1.10.9<br/>
pip install PyJWT<br/>
pip install python_jose<br/>
pip install python-multipart

## Introdução

Primeiramente, execute o 'docker-compose up -d'<br/>
Isso irá permitir o acesso ao keycloak na url definida: localhost:8085/auth<br/>
O usuário e senha de administrador também estão definidos do docker-compose: keycloakuser, keycloakpassword<br/>
Em seguida, configure o Keycloak com base no tutorial em: 'https://fastapi-keycloak.code-specialist.com/keycloak_configuration/'<br/>
Os nomes que estão por padrão são: Realm = Test, Client = test-client. Caso crie os recursos com outros nomes, altere na API.<br/>

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

Alem disso, deve-se copiar a public key do algoritmo RS256 contida em Realm Settings > Keys<br/>
SECRET_KEY = b'-----BEGIN PUBLIC KEY-----\n{Insira a chave aqui}\n-----END PUBLIC KEY-----'<br/>
Após isso, basta executar a API: uvicorn main:app<br/>
