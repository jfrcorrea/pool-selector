"""Módulo principal da API REST para seleção de pools de instâncias."""

from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def read_root() -> dict:
    return {"status": "ok"}
