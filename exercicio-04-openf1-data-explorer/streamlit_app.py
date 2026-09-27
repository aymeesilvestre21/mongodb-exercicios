"""
PRÁTICA 04
OpenF1 Data Explorer

Aplicação Streamlit para visualizar os dados da OpenF1
armazenados no MongoDB.
"""

import pandas as pd
import streamlit as st

from db_utils import (
    conectar_mongodb,
    buscar_anos,
    buscar_sessoes_por_ano,
    buscar_pilotos_da_sessao,
    buscar_voltas
)


st.set_page_config(
    page_title="OpenF1 Data Explorer",
    layout="wide"
)

st.title("OpenF1 Data Explorer")

db = conectar_mongodb()


anos = buscar_anos(db)

ano_selecionado = st.sidebar.selectbox(
    "Selecione o ano",
    anos
)

sessoes = buscar_sessoes_por_ano(
    db,
    ano_selecionado
)


opcoes_sessoes = {
    f"{sessao.get('meeting_name', 'Sessão')} - {sessao.get('session_name', '')}": sessao
    for sessao in sessoes
}

sessao_selecionada_nome = st.sidebar.selectbox(
    "Selecione a corrida",
    list(opcoes_sessoes.keys())
)

sessao_selecionada = opcoes_sessoes[
    sessao_selecionada_nome
]

session_key = sessao_selecionada["session_key"]


st.subheader("Detalhes da sessão")

col1, col2, col3 = st.columns(3)

col1.metric(
    "País",
    sessao_selecionada.get("country_name", "-")
)

col2.metric(
    "Circuito",
    sessao_selecionada.get("circuit_short_name", "-")
)

col3.metric(
    "Data",
    sessao_selecionada.get("date_start", "-")
)


pilotos = buscar_pilotos_da_sessao(
    db,
    session_key
)

opcoes_pilotos = {
    f"{piloto.get('full_name', 'Piloto')} - #{piloto.get('driver_number')}":
    piloto.get("driver_number")
    for piloto in pilotos
}

pilotos_selecionados = st.multiselect(
    "Selecione os pilotos",
    list(opcoes_pilotos.keys())
)


numeros_pilotos = [
    opcoes_pilotos[nome]
    for nome in pilotos_selecionados
]

if numeros_pilotos:
    voltas = buscar_voltas(
        db,
        session_key,
        numeros_pilotos
    )

    dataframe_voltas = pd.DataFrame(voltas)


if numeros_pilotos:
    voltas = buscar_voltas(
        db,
        session_key,
        numeros_pilotos
    )

    dataframe_voltas = pd.DataFrame(voltas)

    if not dataframe_voltas.empty:
        st.subheader("Comparação de desempenho")

        dataframe_grafico = dataframe_voltas[
            [
                "lap_number",
                "lap_duration",
                "driver_number"
            ]
        ].dropna()

        grafico = dataframe_grafico.pivot(
            index="lap_number",
            columns="driver_number",
            values="lap_duration"
        )

        st.line_chart(grafico)

        with st.expander("Ver tabela de dados"):
            st.dataframe(
                dataframe_voltas,
                use_container_width=True
            )
    else:
        st.warning(
            "Não foram encontradas voltas para os pilotos selecionados."
        )
