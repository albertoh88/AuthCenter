import datetime
import jwt
import mysql.connector
from conection import get_connection
from userservice import UserService

class DatabaseHandle:
    def __init__(self):
        self.userservice = UserService()

    def register_user(self, email, username, password, role):
        try:
            # Validar nombre de usuario y contraseña
            self.userservice.validate_email(email)
            self.userservice.validate_username(username)
            self.userservice.validate_password(password)

            # Establecer conexión con la base de datos
            conn = get_connection()
            cursor = conn.cursor()

            # Lógica para verificar si el usuario ya existe
            query = 'SELECT user_exists(%s);' # Aquí invocamos la función
            cursor.execute(query, (username,))
            result = cursor.fetchone()
            if result[0]:

                return {'success': False, 'message': 'El usuario ya existe'}
            else:

                # Lógica de cifrado
                hashed_password = self.userservice.hash_password(password)

                # Llamar al procedimiento
                cursor.callproc('register_user', [email, username, hashed_password, role])

                # Confirmar cambios
                conn.commit()
                return {'success': True, 'message': f"Usuario' {username}' registrado exitosamente"}

        except mysql.connector.Error as err:
            # Manejo de errores de base de datos
            return {'success': False, 'message': f"Error al registrar el usuario: {err}"}

        except ValueError as val_err:
            # Manejo de errores de validación
            return {'success': False, 'message': f'Error de validación: {val_err}'}

        except Exception as e:
            # Manejo de errores inesperados
            return {'success': False, 'message': f'Error inesperado: {e}'}

        finally:
            # Cerrar el cursor y la conexión si están abiertos
            if 'cursor' in locals() and cursor:
                cursor.close()
            if 'conn' in locals() and conn:
                conn.close()

    def login_user(self, username, password):
        try:
            # Validar nombre de usuario
            self.userservice.validate_username(username)

            # Establecer conexión con la base de datos
            conn = get_connection()
            cursor = conn.cursor()

            # Llamando al procedimiento almacenado
            query = 'CALL login_user(%s, %s, @p_email, @login_success, @message);'
            cursor.execute(query, (username, password))

            # Recuperando las variables de salidas
            cursor.execute('SELECT @p_email, @login_success, @message;')
            result = cursor.fetchone()

            email = result[2]
            login_success = result[0]
            message = result[1]

            # Si el usuario existe, procedemos a verificar la contraseña
            if login_success == 1:
                # Obtener la contraseña cifrada almacenada desde la base de datos
                query = 'SELECT get_encrypted_password(%s);'
                cursor.execute(query, (username,))
                result = cursor.fetchone()

                if result and result[0]:
                    stored_password = result[0]

                    # Comparar contrseñas
                    if self.userservice.check_password(password, stored_password):
                        token = self.userservice.token_user_encode(email, username)
                        return {'success': True, 'message': 'Inicio de sesión exitoso.', 'token': token}
                    else:
                        return {'success': False, 'message': 'Contraseña incorrecta.'}
                else:
                    # Error al obtener la contraseña cifrada
                    return {'success': False, 'message': ' Error al recuperar la contraseña del usuario.'}

            else:
                # Mensaje devuelto por el procedimiento almacenada
                return {'success': False, 'message': message}

        except mysql.connector.Error as err:
            # Manejo de errores de base de datos
            return {'success': False, 'message': f"Error en el inicio de sesión: {err}"}

        except Exception as e:
            # Manejo de errores inesperados
            return {'success': False, 'message': f'Error inesperado: {e}'}

        finally:
            # Cerrar el cursor y la conexión si están abiertos
            if 'cursor' in locals() and cursor:
                cursor.close()
            if 'conn' in locals() and conn:
                conn.close()

    def verify_and_validate_token(self, token):
        try:
            # Decodificar el token
            decoded = self.userservice.token_user_decoded(token)
            username = decoded.get('username')
            email = decoded.get('email')

            if not email:
                raise ValueError('El token no contiene un email válido.')
            if not username:
                raise ValueError('El token no contiene un nombre de usuario válido.')

            # Validar si el token expiró
            if 'exp' in decoded:
                # Convertir el timestamp a fecha
                exp = datetime.datetime.utcfromtimestamp(decoded['exp'])
                if exp < datetime.datetime.utcnow():
                    raise ValueError('El token ha expirado.')

            # Validar contra la base de datos
            with get_connection() as conn:
                with conn.cursor() as cursor:

                    # Consulta a la función almacenada
                    query = 'SELECT user_exists_by_email(%s);'  # Aquí invocamos la función
                    cursor.execute(query, (email,))
                    result = cursor.fetchone()

                    # Verificamos si el resultado es válido
                    if not result or result[0] != 1: # Cambia según lo que devuelva la función
                        raise ValueError('El usuario no existe o no es válido en la base de datos.')

            # Si es válido, devuelve información del usuario
            return {
                'success': True,
                'message': 'Token válido y usuario verificado.',
                'username': username
            }

        except jwt.ExpiredSignatureError:
            return {'success': False, 'message': 'El token ha expirado.'}
        except jwt.InvalidTokenError:
            return {'success': False, 'message': 'El token no es válido.'}
        except Exception as e:
            return {'success': False, 'message': f'Error inesperado: {str(e)}'}

    def reset_password(self, token, new_password):
        try:
            decoded = self.userservice.token_user_decoded(token)
            email = decoded['email']
            username = decoded['username']

            # Verificar si el token ha expirado
            if datetime.datetime.utcnow() > datetime.datetime.utcfromtimestamp(decoded['exp']):
                raise ValueError('El token ha expirado.')
            else:

                conn = get_connection()
                cursor = conn.cursor()

                # Verificar si el correo electrónico es valido
                query = 'SELECT user_exists_by_email(%s);'  # Aquí invocamos la función
                cursor.execute(query, (email,))
                result = cursor.fetchone()

                # verificando el resultado
                if result and result[0]: # Si el usuario existe
                    # Verifcar si la nueva contraseña cumple con los requisitos
                    self.userservice.validate_password(new_password)

                    # Hashear la nueva contraseña
                    hashed_password = self.userservice.hash_password(new_password)

                    # Actualizar la contraseña en la base de datos
                    cursor.callproc('update_password', [email, hashed_password])
                    conn.commit()

                    token = self.userservice.token_user_encode(email, username)
                    return {'success': True, 'message': 'Contraseña actualizada exitosamente.', 'token': token}
                else:
                    return {'success': False, 'message': 'El correo electónico no existe'}

        except jwt.ExpiredSignatureError:
            return {'success': False, 'message': 'El token ha expirado.'}
        except jwt.InvalidTokenError:
            return {'success': False, 'message': 'El token no es válido.'}
        except Exception as e:
            return {'success': False, 'message': f'Error inesperado: {str(e)}'}
        finally:
            # Cerrar la conexión a la base de datos
            if 'cursor' in locals() and cursor:
                cursor.close()
            if 'conn' in locals() and conn:
                conn.close()