from fastapi import FastAPI
from routes.predict import router as pr_router
from routes.moderation_result import router as mo_router
from contextlib import asynccontextmanager
from model import load_or_train_model
from client.kafka import get_kafka_producer

def create_app():

    @asynccontextmanager # on_event deprecated
    async def lifespan(app: FastAPI):
        app.state.model = load_or_train_model()
        producer = get_kafka_producer()
        await producer.start()
        app.state.producer = producer
        yield
        await producer.stop()

    app = FastAPI(lifespan=lifespan)

    @app.get('/')
    async def root():
        return {'message': 'Hello World'}

    app.include_router(pr_router)
    app.include_router(mo_router)
    return app

app = create_app()