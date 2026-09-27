"""
EXERCÍCIO 02
Coletar e Armazenar Dados do Cartola FC
"""

import os
import requests

from datetime import datetime
from dotenv import load_dotenv
from pymongo import MongoClient, UpdateOne


load_dotenv()

API_URL = "https://api.cartola.globo.com/atletas/mercado"
DATABASE_NAME = "cartola_fc_db"


def conectar_mongodb():
    """
    Conecta ao MongoDB usando a variável MONGO_URI
    armazenada no arquivo .env.
    """

    mongo_uri = os.getenv("MONGO_URI")

    if not mongo_uri:
        raise ValueError("A variável MONGO_URI não foi encontrada.")

    client = MongoClient(mongo_uri)

    return client[DATABASE_NAME]


def conectar_mongodb():
    """
    Conecta ao MongoDB usando a variável MONGO_URI
    armazenada no arquivo .env.
    """

    mongo_uri = os.getenv("MONGO_URI")

    if not mongo_uri:
        raise ValueError("A variável MONGO_URI não foi encontrada.")

    client = MongoClient(mongo_uri)

    return client[DATABASE_NAME]


def buscar_dados_mercado():
    """
    Busca os dados de mercado da API do Cartola FC.
    """

    try:
        response = requests.get(API_URL, timeout=30)
        response.raise_for_status()

        return response.json()

    except requests.RequestException as error:
        print(f"Erro ao buscar dados da API: {error}")
        return None


def processar_e_gravar_dados(db, dados_mercado):
    """
    Processa os dados recebidos da API
    e grava cada grupo em sua coleção correspondente.
    """

    timestamp_coleta = datetime.utcnow().isoformat()

    # Dados dos clubes
    print("Gravando dados dos clubes...")

    clubes = dados_mercado.get("clubes", {})

    operacoes_clubes = []

    for clube_id, clube in clubes.items():
        documento_clube = {
            "_id": int(clube_id),
            "nome": clube.get("nome"),
            "abreviacao": clube.get("abreviacao"),
            "escudos": clube.get("escudos"),
            "nome_fantasia": clube.get("nome_fantasia")
        }

        operacoes_clubes.append(
            UpdateOne(
                {"_id": int(clube_id)},
                {"$set": documento_clube},
                upsert=True
            )
        )

    if operacoes_clubes:
        db.clubes_rodada_atual.bulk_write(operacoes_clubes)

    # Dados dos atletas
    print("Gravando dados dos atletas...")

    atletas = dados_mercado.get("atletas", [])

    for atleta in atletas:
        atleta["timestamp_coleta"] = timestamp_coleta

    db.atletas_rodada_atual.delete_many({})

    if atletas:
        db.atletas_rodada_atual.insert_many(atletas)

    # Status do mercado
    print("Gravando status do mercado...")

    status = dados_mercado.get("status", {})

    if status:
        status["timestamp_coleta"] = timestamp_coleta

        db.mercado_rodada_atual.delete_many({})
        db.mercado_rodada_atual.insert_one(status)


if __name__ == "__main__":
    print("Conectando ao MongoDB...")

    db = conectar_mongodb()

    print("Buscando dados na API...")

    dados_mercado = buscar_dados_mercado()

    if dados_mercado:
        processar_e_gravar_dados(db, dados_mercado)
        print("Finalizado com sucesso.")
    else:
        print("Não foi possível obter os dados da API.")


