# FastAPI-Keycloak

## Installing Libraries

```
pip install fastapi_keycloak
```

```
pip install pydantic==1.10.9
```

```
pip install PyJWT
```

```
pip install python_jose
```

```
pip install python-multipart
```

```
pip install cryptography
```


## Introdução

Primeiramente, execute o 

```
docker-compose up -d
```

Isso irá permitir o acesso ao keycloak na url definida: localhost:8085/auth<br/>
O usuário e senha de administrador também estão definidos do docker-compose: keycloakuser, keycloakpassword<br/>
Em seguida, configure o Keycloak com base no tutorial em: 'https://fastapi-keycloak.code-specialist.com/keycloak_configuration/'<br/>
Os nomes que estão por padrão são: Realm = Test, Client = test-client. Caso crie os recursos com outros nomes, altere na API.<br/>

## Configuração da API

A configuração da API consiste em passar os devidos valores do parâmetro idp.


```
idp = FastAPIKeycloak(
        server_url="http://localhost:8085/auth",
        client_id="Nome do Client criado",
        client_secret="Client Secret na seção Credentials do cliente que foi criado",
        admin_client_secret="Admin Client Secret na seção Credentials do cliente admin-cli",
        realm="Nome do Realm",
        callback_uri="Url de callback"
)
```

Alem disso, deve-se copiar a public key do algoritmo RS256 contida em Realm Settings > Keys

```
SECRET_KEY = b'-----BEGIN PUBLIC KEY-----\n{Insira a chave aqui}\n-----END PUBLIC KEY-----'
```

Após isso, basta executar a API: 

```
uvicorn main:app
```

A documentação do Swagger está em:

http://localhost:8000/docs
