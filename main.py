from fastapi import FastAPI
import logging,os

from app.core.origin import create_middleware, init_routers

def create_app()->FastAPI:
    app_=FastAPI(middleware=create_middleware(),title="Azure AI services",
                 version="V1.0")
    filepath=os.path.join("Utils","Basic.logs")
    logging.basicConfig(level=logging.DEBUG,
                        filename=filepath,
                        format="%(asctime)s || %(levelname)s || %(message)s",
                        datefmt="%Y-%m-%d %H:%M:%S")
    init_routers(app_=app_)
    return app_

app= create_app()


