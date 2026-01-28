from fastapi import FastAPI
from routes.predict import router
from contextlib import asynccontextmanager
from model import load_or_train_model

def create_app():
    @asynccontextmanager # on_event deprecated
    async def lifespan(app: FastAPI):
        app.state.model = load_or_train_model()
        yield

    app = FastAPI(lifespan=lifespan)

    @app.get('/')
    async def root():
        return {'message': 'Hello World'}

    app.include_router(router)
    return app

app = create_app()