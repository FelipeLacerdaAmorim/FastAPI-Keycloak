from typing import Annotated
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError
import jwt
import uvicorn
from starlette import status
from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import RedirectResponse
from fastapi_keycloak import FastAPIKeycloak, OIDCUser, UsernamePassword
from pydantic import BaseModel

app = FastAPI()

idp = FastAPIKeycloak(
    server_url="http://localhost:8085/auth",
    client_id="test-client",
    client_secret="cW7fH0sry0sh8lHYbLljrta2q6Nkyv3P",
    admin_client_secret="blYLTpfAVyz3vuSQ45i5b2yBUSqrnrLa",
    realm="Test",
    callback_uri="http://localhost:8081/callback"
)
idp.add_swagger_config(app)

SECRET_KEY = b'-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAyLn0tfv9rxx3P5TWWjHKee/eQB3U8C88YWS7K8XoTYKsVTnUDkakMXCINeJ0u86NY866A/yzffkdm2A8XumMftT0f7/pt82vDYRrKxpc/KQaAdKTmFNkTZkXl6hjqtLH45Zgp0KuuYXMxfrpXxRN30KcLp5HwZ/aAMyb+Meh0TaU5YifDD5KxHyURE/yXUrRKbpPxzoA7VpF/JSvDNhWuOXZ/sTfeixpp9W72A0FOGErGjue5oMXxRk338ujmGT4VTqxvOezJmxnsrLVyscUTuY/JH3hNZjTsB8GMkuxoeL/FjAdCVPHQoTa0fl0tf/cDoa8DQBoOA0aahcnYsulNwIDAQAB\n-----END PUBLIC KEY-----'
ALGORITHM = 'RS256'

oauth2_bearer = OAuth2PasswordBearer(tokenUrl='/token',
                                     scheme_name="direct_oauth2_schema")


# @app.get("/user")  # Requires logged in
# def current_users(user: OIDCUser = Depends(idp.get_current_user())):
#     return user.name


@app.get("/user-test")  # Requires logged in
async def get_current_user(token:Annotated[str, Depends(oauth2_bearer)]):
#async def get_current_user(token:str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get('name')
        if username is None or username is None:
             raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                 detail='Could not validate user.')
        return {'username': username}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Could not validate user.')


@app.post("/token")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    token_aux = idp.user_login(username=form_data.username, password=form_data.password)
    token = token_aux.access_token
    return {'access_token': token, 'token_type': 'bearer'}

@app.get("/admin")  # Requires the admin role
def company_admin(user: OIDCUser = Depends(idp.get_current_user(required_roles=["admin"]))):
    return f'Hi admin {user}'


# @app.get("/login")
# def login_redirect():
#     return RedirectResponse(idp.login_uri)

# @app.get("/auto-login")
# def login(user: UsernamePassword = Depends()):
#     return idp.user_login(username=user.username, password=user.password.get_secret_value())


@app.get("/callback")
def callback(session_state: str, code: str):
    return idp.exchange_authorization_code(session_state=session_state, code=code)  # This will return an access token

# @app.get("/auto-callback", response_model=Callback)
# def callback():
#     await 
#     return idp.exchange_authorization_code(session_state=session_state, code=code)  # This will return an access token


if __name__ == '__main__':
    uvicorn.run('app:app', host="127.0.0.1", port=8081)