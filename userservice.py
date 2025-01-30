from decouple import config
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import jwt
import datetime
import bcrypt
import smtplib
import re


class UserService:
    def __init__(self):
        pass

    # Función para cifrar el password
    def hash_password(self, password):
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

    def check_password(self, plain_password, stored_password):
        try:
            # Compara la contraseña ingresada con la almacenada
            return bcrypt.checkpw(plain_password.encode('utf-8'), stored_password.encode('utf-8'))
        except Exception as e:
            return False

    def validate_username(self, username: str):
        if len(username) < 3:
            raise ValueError('El nombre de usuaruo debe tener al menos 3 caracteres.')
        if len(username) > 20:
            raise ValueError('El nombre de usuario no debe exceder los 20 caracteres.')
        if not username.isalnum():
            raise ValueError('El nombre de usuario solo puede contener letras y números')

    def validate_password(self, password: str):
        if len(password) < 6:
            raise ValueError("La contraseña debe tener al menos 6 caracteres.")
        if not any(char.isupper() for char in password):
            raise ValueError("La contraseña debe contener al menos una letra mayúscula.")
        if not any(char.islower() for char in password):
            raise ValueError("La contraseña debe contener al menos una letra minúscula.")
        if not any(char.isdigit() for char in password):
            raise ValueError("La contraseña debe contener al menos un número.")
        if not any(char in "!@#$%^&*()_-+=" for char in password):
            raise ValueError("La contraseña debe contener al menos un carácter especial (!@#$%^&*()_-+=).")

    def validate_email(self, email):
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return False
        return True

    def token_user_encode(self, email, username, expiration_hours=1):
        try:
            token = jwt.encode(
                {
                    'email': email,
                    'username': username,
                    'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
                },
                config('SECRET_KEY'),
                algorithm='HS256'
            )
            return token
        except Exception as e:
            raise ValueError(f'Error al generar el token: {str(e)}')

    def generate_reset_token(self, email, username):
        try:
            reset_token = jwt.encode(
                {
                    'email': email,
                    'username': username,
                    'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
                },
                config('SECRET_KEY'),
                algorithm='HS256'
            )
            return reset_token
        except Exception as e:
            raise ValueError(f'Error al generar el token: {str(e)}')

    def send_token(self, to_email, subject, body):
        try:
            # validar parámetros de entrada
            if not to_email or not subject or not body:
                return {'success': False, 'message': 'El destinatario, asunto y cuerpo no pueden estar vacíos.'}

            # Validar formato del correo electrónico
            if not self.validate_email(to_email):
                return {'success': False, 'message': 'La dirección de correo electrónico no es válida.'}

            # Información del servidor de correo (Mailtrap como ejemplo)
            sender_email = 'from@example.com' # Cambiar esto por tu dirección de correo
            sender_user = config('MAILTRAP_USER')
            sender_password = config('MAILTRAP_PASSWORD') # Usar un token de aplicación si usas 2FA

            # Crear el mensaje
            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = to_email
            msg['Subject'] = subject

            # Adjuntar el cuerpo del mensaje
            msg.attach(MIMEText(body, 'plain'))

            # Conectarse al servidor SMTP de Gmail
            with smtplib.SMTP('sandbox.smtp.mailtrap.io', 587) as server:
                server.starttls() # Iniciar TLS (encriptación)
                server.login(sender_user, sender_password) # Autenticarse en el servidor SMTP

                # enviar el mensaje
                server.sendmail(sender_email, to_email, msg.as_string())

            return {'success': True, 'message': f'Correo enviado a {to_email}'}

        except smtplib.SMTPAuthenticationError:
            return {'success': False, 'message': 'Error de autenticación SMTP. Verificar las credenciales.'}
        except smtplib.SMTPConnectError:
            return {'success': False, 'message': 'Error de conexión al servidor SMTP.'}
        except Exception as e:
            return {'success': False, 'message': f'Error al envial el correo {str(e)}'}

    def token_user_decoded(self, token):
        try:
            decoded = jwt.decode(token, config('SECRET_KEY'), algorithms=['HS256'])
            return decoded
        except jwt.ExpiredSignatureError:
            raise ValueError('El token ha expirado. Genera un nuevo token.')
        except jwt.InvalidTokenError as e:
            raise ValueError(f'El token no es válido: {str(e)}')
        except Exception as e:
            raise ValueError(f'Error inesperado al decodificar el token: {str(e)}')
