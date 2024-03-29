from typing import Annotated
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError
import jwt
import requests
import uvicorn
from starlette import status
from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import RedirectResponse
from fastapi_keycloak import FastAPIKeycloak, OIDCUser, UsernamePassword, KeycloakUser
from pydantic import BaseModel, SecretStr
import urllib


app = FastAPI()

idp = FastAPIKeycloak(
    server_url="http://localhost:8085/",
    client_id="client-id",
    client_secret="client_secret",
    admin_client_secret="admin_client_secret",
    realm="realm_name",
    callback_uri="http://localhost:8081/callback"
)
idp.add_swagger_config(app)

SECRET_KEY = b'-----BEGIN PUBLIC KEY-----\ninsert_public_key\n-----END PUBLIC KEY-----'
ALGORITHM = 'RS256'                  

oauth2_bearer = OAuth2PasswordBearer(tokenUrl='/token',
                                     scheme_name="direct_oauth2_schema")

# Classes auxiliares
class CreateUserRequest(BaseModel):
    username: str
    email: str
    first_name: str
    last_name: str
    password: str


# Endpoints
@app.post("/token", tags=["auth-flow"])
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):

    token_aux = idp.user_login(username=form_data.username, password=form_data.password)

    return token_aux


@app.get("/admin", tags=["auth-flow"])  # Requires the admin role
def company_admin(user: OIDCUser = Depends(idp.get_current_user(required_roles=["admin"]))):
    return f'Hi admin {user}'


@app.get("/callback", tags=["auth-flow"])
def callback(session_state: str, code: str):
    return idp.exchange_authorization_code(session_state=session_state, code=code)  # This will return an access token


@app.post("/logout", tags=["auth-flow"])
def logout(access_token, refresh_token):
    try:
        token_url = f'http://localhost:8085/realms/{idp.realm}/protocol/openid-connect/token'
        url = f'http://localhost:8085/realms/{idp.realm}/protocol/openid-connect/logout'

        payload = jwt.decode(access_token, SECRET_KEY, audience="account", algorithms=[ALGORITHM])
        username: str = payload.get('name')
        if username is None:
             raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                 detail='Could not validate user.')
        
        user_id = payload.get('id')

        # Get token hint info
        token_data = dict(grant_type='client_credentials', client_id=idp.client_id, client_secret=idp.client_secret, scope='openid')

        token_resp = requests.post(url=token_url, json=token_data)

        id_token = token_resp.json().get("id_token")

        # Logout info 
        data = dict(client_id=user_id, refresh_token=refresh_token)
        body = dict(id_token_hint=id_token)

        resp = requests.post(url=url, params=data, json=body)

        if resp.is_redirect:
            redirect_url = resp.headers["Location"]
            return RedirectResponse(url=redirect_url)
        
        return resp.content
    
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Could not validate user.')


# Menagement Endpoints
@app.get("/user", tags=["user-management"])  # Requires logged in
async def get_current_user(token:Annotated[str, Depends(oauth2_bearer)]):
#async def get_current_user(token:str):
    try:
        payload = jwt.decode(token, SECRET_KEY, audience="account", algorithms=[ALGORITHM])
        username: str = payload.get('name')
        if username is None:
             raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                 detail='Could not validate user.')
        return{'username': username}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Could not validate user.')
    

@app.post("/users", tags=["user-management"])
async def create_user(model: CreateUserRequest):   
    idp.create_user(model.first_name, model.last_name, model.username, model.email, model.password, True, None, False, None)
    try:
        user = idp.get_user(query=f'username={model.username}')
        return user
    except:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail='Could not validate user.')

@app.put("/user", tags=["user-management"])
def update_user(first_name:str, last_name:str, email:str,#user: KeycloakUser,
                token:Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, audience="account", algorithms=[ALGORITHM])
        username: str = payload.get('preferred_username')

        if username is None:
             raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                 detail='Could not validate user.')
        
        #user_id: str = payload.get('sub')
        user_aux = idp.get_user(query=f'username={username}')
        user_aux.firstName = first_name
        user_aux.lastName = last_name
        user_aux.email = email

        return idp.update_user(user=user_aux)
        
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Could not validate user.')
    


@app.put("/user/{user_id}/change-password", tags=["user-management"])
def change_password(user_id: str, new_password: SecretStr,
                    token:Annotated[str, Depends(oauth2_bearer)]):
    return idp.change_password(user_id=user_id, new_password=new_password)


@app.put("/user/{user_id}/send-email-verification", tags=["user-management"])
def send_email_verification(user_id: str,
                            token:Annotated[str, Depends(oauth2_bearer)]):
    return idp.send_email_verification(user_id=user_id)



if __name__ == '__main__':
    uvicorn.run('app:app', host="127.0.0.1", port=8081)