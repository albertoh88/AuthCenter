from fastapi import APIRouter, Depends, HTTPException, Header, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from database import DatabaseHandle
from userservice import UserService
import jwt


router = APIRouter()
db_handler = DatabaseHandle()
userservices = UserService()
security = HTTPBearer()

class RegisterRequestSchema(BaseModel):
    email: str
    username: str
    password: str
    role: int

# Ruta para registrar un usuario
@router.post('/register')
def register_user(request: RegisterRequestSchema):
    # Llamada a la función register_user de DatabaseHandle
    result = db_handler.register_user(request.email, request.username, request.password, request.role)

    if not result['success']:
        # Si hay un error, devolver un 400 con el mensaje de error
        raise HTTPException(status_code=400, detail=result['message'])

    # Devolviendo una respuesta exitosa
    return {'message':result['message']}

class LoginRequestSchema(BaseModel):
    username: str
    password: str

# Ruta para logear un usuario
@router.post('/login')
def login_user(request: LoginRequestSchema):
    # Aquí deberías implementar la lógica para verificar el login
    # Por ejemplo, llamando a un método en `DatabaseHandle` que valide las credenciales

    result = db_handler.login_user(request.username, request.password)

    if not result['success']:
        # Si las credenciales no son válidas, devolver un error
        raise HTTPException(status_code=401, detail=result['message'])

    # Si el login es exitoso, devolver el token generado
    return {'message': result['message'], 'token': result['token']}

@router.get('/protected-route', dependencies=[Depends(security)])
def token_protected_route(payload=Depends(userservices.token_user_decoded)):#authorization: str = Header(..., alias='Authorization')):
    # print(authorization)
    # if not isinstance(authorization, str) or not authorization.startswith('Bearer '):
    #     raise HTTPException(status_code=401, detail='El token no fue proporcionado correctamente.')
    #
    # token = authorization.split(' ')[1] # Extraer el token después de 'Bearer'
    print(payload)

    # Llamar a la función de validación del token
    try:
        validation_result = db_handler.verify_and_validate_token(payload)

        # Si la validación falla, manejar el error
        if not validation_result['success']:
            raise HTTPException(status_code=401, detail=validation_result['message'])

        # Si está bien, retornar un mensaje de éxito con los datos del usuario
        return {
            'success': True,
            'message': 'Acceso permitido. Token válido',
            'username': validation_result['username'],
            'token': payload
        }

    except Exception as e:
        # Manejar cualquier error inesperado
        raise HTTPException(status_code=500, detail=f'Error interno: {str(e)}')

class ResetPasswordSchema(BaseModel):
    email: str

# Ruta para recuperar la contraseña
@router.post('/reset-password')
def reset_password(request: ResetPasswordSchema, http_request: Request):
    try:
        autorization = http_request.headers.get('Authorization')
        if not autorization:
            raise HTTPException(status_code=401, detail='El token no fue proporcionado correctamente')

        result = token_protected_route(autorization)

        if not result['success']:
            raise HTTPException(status_code=401, detail=result['message'])

        username = result['username']
        token = userservices.generate_reset_token(request.email, username)

        send_result = userservices.send_token('to@example.com', 'password Reset Token', str(token))

        return send_result
    except Exception as e:
        # Manejar cualquier error inesperado
        print(f'error inesperado: {str(e)}')
        if 'result' in locals():
            message = result['message']
        else:
            message = 'Error desconocido al procesar la solicitud'
        raise HTTPException(status_code=500, detail=result['message'])

class ResetPasswordConfirmSchema(BaseModel):
    new_password: str

@router.post('/reset-password-confirm')
def reset_password_confirm(request: ResetPasswordConfirmSchema, http_request: Request):
    try:
        autorization = http_request.headers.get('Authorization')
        if not autorization:
            raise HTTPException(status_code=401, detail='El token no fue proporcionado correctamente')
        # Llamamos a la función para validar el token
        result = token_protected_route(autorization)

        # Verrificamos si la validación del token fue exitosa
        if not result['success']:
            raise HTTPException(status_code=401, detail=result['message'])

        # Extraemos el token validado
        token = result['token']

        # llamamos a la función de resetear la contraseña
        reset = db_handler.reset_password(token, request.new_password)

        if not reset['success']:
            # Si las credenciales no son válidas, devolver un error
            raise HTTPException(status_code=500, detail=result['message'])

        # Si es exitoso, devolver el token generado
        return {'message': result['message'], 'token': result['token']}
    except Exception as e:
        # Manejar cualquier error inesperado
        print(f'error inesperado: {str(e)}')
        if 'result' in locals():
            message = result['message']
        else:
            message = 'Error desconocido al procesar la solicitud'
        raise HTTPException(status_code=500, detail=result['message'])
