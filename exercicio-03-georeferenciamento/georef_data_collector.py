"""
EXERCÍCIO 03
Georeferenciamento com MongoDB e GeoJSON
"""

import os
import requests
import pandas as pd
import geopandas as gpd

from io import StringIO
from dotenv import load_dotenv
from pymongo import MongoClient, GEOSPHERE


load_dotenv()

DATABASE_NAME = "georeferenciamento_db"
COLLECTION_NAME = "unidades_basicas_saude"

DATA_URL = os.getenv("DATA_URL")
MONGO_URI = os.getenv("MONGO_URI")


def conectar_mongodb():
    """
    Conecta ao MongoDB usando a variável MONGO_URI do arquivo .env.
    """

    if not MONGO_URI:
        raise ValueError("A variável MONGO_URI não foi encontrada.")

    client = MongoClient(MONGO_URI)

    return client[DATABASE_NAME]


def buscar_dados():
    """
    Busca os dados georreferenciados a partir da URL configurada.
    """

    if not DATA_URL:
        raise ValueError("A variável DATA_URL não foi encontrada.")

    try:
        response = requests.get(DATA_URL, timeout=30)
        response.raise_for_status()

        return response.text

    except requests.RequestException as error:
        print(f"Erro ao buscar os dados: {error}")
        return None


def transformar_para_geojson(conteudo_csv):
    """
    Converte os dados CSV em registros no formato GeoJSON.
    """

    dataframe = pd.read_csv(StringIO(conteudo_csv))

    if "latitude" not in dataframe.columns or "longitude" not in dataframe.columns:
        raise ValueError(
            "O arquivo deve possuir as colunas latitude e longitude."
        )

    geodataframe = gpd.GeoDataFrame(
        dataframe,
        geometry=gpd.points_from_xy(
            dataframe["longitude"],
            dataframe["latitude"]
        ),
        crs="EPSG:4326"
    )

    registros = []

    for _, linha in geodataframe.iterrows():
        documento = linha.drop(labels=["geometry"]).to_dict()

        documento["localizacao"] = {
            "type": "Point",
            "coordinates": [
                linha.geometry.x,
                linha.geometry.y
            ]
        }

        registros.append(documento)

    return registros


def salvar_no_mongodb(db, registros):
    """
    Salva os registros no MongoDB
    e cria um índice geoespacial no campo localizacao.
    """

    collection = db[COLLECTION_NAME]

    collection.delete_many({})

    if registros:
        collection.insert_many(registros)

    collection.create_index(
        [("localizacao", GEOSPHERE)]
    )


if __name__ == "__main__":
    print("Conectando ao MongoDB...")

    db = conectar_mongodb()

    print("Buscando dados georreferenciados...")

    conteudo_csv = buscar_dados()

    if conteudo_csv:
        print("Transformando dados para GeoJSON...")

        registros = transformar_para_geojson(conteudo_csv)

        print("Salvando dados no MongoDB...")

        salvar_no_mongodb(db, registros)

        print("Exercício 03 finalizado com sucesso.")
    else:
        print("Não foi possível obter os dados.")
