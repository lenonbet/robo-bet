import streamlit as st
import pandas as pd
import math
import random
import datetime
from utils import buscar_jogos_por_data

st.set_page_config(layout="wide")
st.title("🤖 ROBÔ IA PROFISSIONAL - APOSTAS")

# ================= MODELO =================
def poisson(lmbda, k):
    return (lmbda**k * math.exp(-lmbda)) / math.factorial(k)

def prob_over(xg, linha):
    return 1 - sum(poisson(xg, i) for i in range(int(linha)))

def prob_btts(xg_home, xg_away):
    return (1 - poisson(xg_home, 0)) * (1 - poisson(xg_away, 0))

def gerar_xg():
    return random.uniform(0.8, 2.5)

def calcular_ev(prob, odd):
    return (prob * odd) - 1

# ================= DATA =================
data = st.date_input("📅 Escolha a data", datetime.date.today())
data_str = data.strftime("%Y-%m-%d")

# ================= BUSCAR JOGOS =================
jogos_por_liga = buscar_jogos_por_data(data_str)

if not jogos_por_liga:
    st.warning("⚠️ Nenhum jogo encontrado nessa data")

# ================= ESCOLHER LIGA =================
liga = st.selectbox("🏆 Campeonato", list(jogos_por_liga.keys()))

jogos = jogos_por_liga[liga]

nomes = [j["nome"] for j in jogos]
mapa = {j["nome"]: j for j in jogos}

jogo_escolhido = st.selectbox("⚽ Jogos", nomes)

modo_auto = st.checkbox("🤖 IA automática (filtrar EV)")

# ================= ANÁLISE =================
if st.button("🔍 Analisar jogo"):

    jogo = mapa[jogo_escolhido]

    casa = jogo["casa"]
    fora = jogo["fora"]

    xg_home = gerar_xg()
    xg_away = gerar_xg()
    xg_total = xg_home + xg_away

    mercados = [
        ("Over 2.5 Gols", prob_over(xg_total, 3), 1.80),
        ("Over 1.5 Gols", prob_over(xg_total, 2), 1.45),
        ("Ambas Marcam", prob_btts(xg_home, xg_away), 1.85),
        ("Escanteios Over 9.5", random.uniform(0.55,0.75), 1.9),
        ("Cartões Over 3.5", random.uniform(0.55,0.75), 1.95)
    ]

    tabela = []

    for nome, prob, odd in mercados:
        ev = calcular_ev(prob, odd)

        if modo_auto and ev < 0.10:
            continue

        tabela.append([
            nome,
            round(prob,2),
            odd,
            round(ev,2)
        ])

    df = pd.DataFrame(tabela, columns=["Mercado","Prob","Odd","EV"])

    st.subheader(f"📊 {casa} x {fora}")
    st.write(f"xG Casa: {round(xg_home,2)} | xG Fora: {round(xg_away,2)}")
    st.dataframe(df)

# ================= IA GLOBAL =================
if st.button("🚀 MELHORES JOGOS DO DIA"):

    melhores = []

    for liga_nome, jogos in jogos_por_liga.items():
        for j in jogos:
            xg = gerar_xg() + gerar_xg()
            prob = prob_over(xg, 3)
            ev = calcular_ev(prob, 1.8)

            if ev > 0.15:
                melhores.append([
                    liga_nome,
                    j["nome"],
                    round(ev,2)
                ])

    if melhores:
        df = pd.DataFrame(melhores, columns=["Liga","Jogo","EV"])
        st.dataframe(df.sort_values(by="EV", ascending=False))
    else:
        st.info("Nenhuma entrada forte hoje")

st.success("🔥 Robô rodando com IA + jogos reais")
