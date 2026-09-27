"""
EXERCÍCIO PRÁTICO 01
Coletor de Dados da OpenF1 para MongoDB
"""

import os
import requests

from dotenv import load_dotenv
from pymongo import MongoClient

# Configurações do Exercício Prático 01

load_dotenv()

BASE_URL = "https://api.openf1.org/v1"
DATABASE_NAME = "openf1_data"

SESSION_KEY = 9159
MEETING_KEY = 1219]


def connect_mongodb():
    """
    Realiza a conexão com o MongoDB
    usando a variável MONGO_URI do arquivo .env.
    """

    mongo_uri = os.getenv("MONGO_URI")

    if not mongo_uri:
        raise ValueError("A variável MONGO_URI não foi encontrada.")

    client = MongoClient(mongo_uri)

    return client[DATABASE_NAME]


def fetch_data(endpoint: str, params: dict) -> list:
    """
    Faz uma requisição GET para a API OpenF1
    e retorna os dados em formato de lista.
    """

    url = f"{BASE_URL}/{endpoint}"

    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()

        return response.json()

    except requests.RequestException as error:
        print(f"Erro ao buscar dados em {endpoint}: {error}")
        return []


def save_to_collection(data: list, collection_name: str, unique_keys: list):
    """
    Salva ou atualiza os dados no MongoDB
    utilizando chaves únicas para evitar duplicações.
    """

    db = connect_mongodb()
    collection = db[collection_name]

    for item in data:
        filter_query = {
            key: item.get(key)
            for key in unique_keys
        }

        collection.update_one(
            filter_query,
            {"$set": item},
            upsert=True
        )


def main():
    """
    Executa o fluxo principal do Exercício Prático 01.
    """

    print("Iniciando Exercício Prático 01...")

    # Buscar dados da sessão
    sessions = fetch_data(
        "sessions",
        {
            "session_key": SESSION_KEY,
            "meeting_key": MEETING_KEY
        }
    )

    save_to_collection(
        sessions,
        "sessions",
        ["session_key"]
    )

    # Buscar pilotos da sessão
    drivers = fetch_data(
        "drivers",
        {
            "session_key": SESSION_KEY
        }
    )

    save_to_collection(
        drivers,
        "drivers",
        ["session_key", "driver_number"]
    )

    # Buscar voltas da sessão
    laps = fetch_data(
        "laps",
        {
            "session_key": SESSION_KEY
        }
    )

    save_to_collection(
        laps,
        "laps",
        ["session_key", "driver_number", "lap_number"]
    )

    print("Exercício Prático 01 finalizado.")


if __name__ == "__main__":
    main()
