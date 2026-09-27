"""
PRÁTICA 04
OpenF1 Data Explorer

Módulo responsável pela conexão e consultas ao MongoDB.
"""

import os

from dotenv import load_dotenv
from pymongo import MongoClient


load_dotenv()

DATABASE_NAME = "openf1_data"
MONGO_URI = os.getenv("MONGO_URI")


def conectar_mongodb():
    """
    Conecta ao banco MongoDB openf1_data.
    """

    if not MONGO_URI:
        raise ValueError("A variável MONGO_URI não foi encontrada.")

    client = MongoClient(MONGO_URI)

    return client[DATABASE_NAME]


def buscar_anos(db):
    """
    Retorna os anos disponíveis na coleção sessions.
    """

    anos = db.sessions.distinct("year")

    return sorted(anos)


def buscar_sessoes_por_ano(db, ano):
    """
    Retorna as sessões disponíveis para o ano selecionado.
    """

    sessoes = list(
        db.sessions.find(
            {"year": ano}
        )
    )

    return sessoes


def buscar_pilotos_da_sessao(db, session_key):
    """
    Retorna os pilotos participantes de uma sessão.
    """

    pilotos = list(
        db.drivers.find(
            {"session_key": session_key}
        )
    )

    return pilotos


def buscar_voltas(db, session_key, pilotos):
    """
    Retorna as voltas dos pilotos selecionados.
    """

    voltas = list(
        db.laps.find(
            {
                "session_key": session_key,
                "driver_number": {"$in": pilotos}
            }
        )
    )

    return voltas
