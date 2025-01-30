from fastapi import FastAPI
from routes import user # Importamos las rutas de usuarios
import uvicorn

app = FastAPI()


# Definimos las rutas
app.include_router(user.router)

@app.get('/')
def read_root():
    return {'menssge': 'Hola, este es mi primer endpoint!!!'}


if __name__ == '__main__':
    uvicorn.run(app, host='127.0.0.1', port=8000)