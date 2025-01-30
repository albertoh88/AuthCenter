# API Sistema de Gestión de Usuarios

Este es un proyecto para gestionar usuarios a través de una API construida con FastAPI. El sistema permite la creación, 
actualización, eliminación y consulta de usuarios, almacenados en una base de datos MySQL. Esta API está diseñada para ser utilizada de manera eficiente 
y segura en aplicaciones web o móviles.

# Tecnologías utilizadas
FastAPI: Framework para la creación de la API.
MySQL: Base de datos utilizada para almacenar la información de los usuarios.
Pydantic: Validación de datos de entrada.
Uvicorn: Servidor ASGI para ejecutar la aplicación.
Python 3.11: Lenguaje de programación utilizado.
Instalación
Requisitos previos
Python 3.11.
Base de datos MySQL.
Gestor de dependencias pip para instalar los paquetes requeridos.

1. Clona el repositorio
git clone https://github.com/tu_usuario/tu_repositorio.git

2. Crea y activa un entorno virtual
python -m venv venv
.\Scripts\activate

3. Instala las dependencias
pip install -r requirements.txt

Actualiza el archivo .env con tus credenciales de base de datos
Abre el archivo .env y asegúrate de ingresar tus datos de conexión a la base de datos
Reemplaza el host, puerto, nombre de la bd, usuario y contraseña con tus credenciales de MySQL, 
asegúrate de que el nombre de la base de datos (sistema_gestion_usuarios) coincida con la base de datos que hayas creado.
Tambien coloca una clave secreta para generar el token y modifica el usuario y contraseña de Mailtrap para el envio de el token a la hora de para cambiar la contraseña del usuario

Para ejecutar la aplicación es el app.py y La API estará disponible en http://127.0.0.1:8000.

# EndPoints
La API proporciona los siguientes puntos de acceso:

POST /login
Descripción: Inicia sesión en el sistema con las credenciales del usuario.
Cuerpo de la solicitud (JSON):
json
{
  "email": "usuario@example.com",
  "password": "contraseña_secreta"
}
Respuesta: Retorna un token JWT para la autenticación de futuras solicitudes.
Código de respuesta: 200 OK
Ejemplo de respuesta:
json
{
  "access_token": "tu_token_jwt",
  "token_type": "bearer"
}

POST /register
Descripción: Registra un nuevo usuario en el sistema.
Cuerpo de la solicitud (JSON):
json
{
  "email": "nuevo_usuario@example.com",
  "name": "Juan Pérez"
  "password": "contraseña_secreta",
  "role": 1
}
Respuesta: Retorna un mensaje confirmando que el usuario fue registrado exitosamente.
Código de respuesta: 201 Created
Ejemplo de respuesta:
json
{
  "message": "Usuario registrado exitosamente"
}

GET /protected-route
Descripción: Ruta protegida que requiere autenticación mediante token JWT. Solo accesible para usuarios autenticados.
Encabezados:
Authorization: Bearer {tu_token_jwt}
Respuesta: Retorna un mensaje de acceso exitoso.
Código de respuesta: 200 OK
Ejemplo de respuesta:
json
{
  "message": "Acceso concedido a la ruta protegida"
}

POST /reset-password
Descripción: Inicia el proceso de restablecimiento de contraseña enviando un correo con un enlace para restablecer la contraseña.
Cuerpo de la solicitud (JSON):
json
{
  "email": "usuario@example.com"
}
Respuesta: Retorna un mensaje confirmando que se ha enviado un correo para restablecer la contraseña.
Código de respuesta: 200 OK
Ejemplo de respuesta:
json
{
  "message": "Correo de restablecimiento enviado"
}

POST /reset-password-confirm
Descripción: Confirma el restablecimiento de la contraseña con un token temporal.
Cuerpo de la solicitud (JSON):
json
{
  "token": "token_temporal",
  "new_password": "nueva_contraseña"
}
Respuesta: Retorna un mensaje indicando si el restablecimiento fue exitoso.
Código de respuesta: 200 OK
Ejemplo de respuesta:
json
{
  "message": "Contraseña restablecida exitosamente"
}

Licencia
Este proyecto está licenciado bajo la MIT License - consulta el archivo LICENSE para más detalles.

Notas adicionales
Documentación de OpenAPI: FastAPI genera automáticamente una interfaz de documentación interactiva de la API accesible en http://127.0.0.1:8000/docs.
