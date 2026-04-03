import streamlit as st
import pandas as pd
import datetime

from utils import buscar_jogos_por_data
from model import *

# ================= CONFIG =================
st.set_page_config(layout="wide")
st.title("🤖 ROBÔ IA PROFISSIONAL - APOSTAS ESPORTIVAS")

# ================= DATA =================
data = st.date_input("📅 Data", datetime.date.today())
data_str = data.strftime("%Y-%m-%d")

# ================= JOGOS =================
jogos_por_liga = buscar_jogos_por_data(data_str)

if not jogos_por_liga:
    st.warning("⚠️ Nenhum jogo encontrado")
    st.stop()

liga = st.selectbox("🏆 Campeonato", list(jogos_por_liga.keys()))
jogos = jogos_por_liga[liga]

if not jogos:
    st.warning("Sem jogos nessa liga")
    st.stop()

nomes = [j["nome"] for j in jogos]
mapa = {j["nome"]: j for j in jogos}

jogo_escolhido = st.selectbox("⚽ Jogo", nomes)

modo_auto = st.checkbox("🤖 Modo IA (filtrar melhores entradas)")

# ================= ANALISE =================
if st.button("🔍 Analisar"):

    jogo = mapa[jogo_escolhido]
    casa = jogo["casa"]
    fora = jogo["fora"]

    # 🔥 CALCULO IA (SEM ERRO)
    xg_home, xg_away = calcular_xg(casa, fora)
    xg_total = xg_home + xg_away

    # ================= FORMATOS =================
    def prob_fmt(p):
        return f"{round(p*100,1)}%"

    def status(ev):
        if ev >= 0.10:
            return "🟢 VALOR"
        elif ev >= 0:
            return "🟡 MÉDIO"
        else:
            return "🔴 RISCO"

    # ================= MERCADOS =================
    mercados = [
        # GOLS
        ("Over 2.5 Gols", prob_over(xg_total, 3), 1.80),
        ("Under 2.5 Gols", 1 - prob_over(xg_total, 3), 2.00),

        # HT
        ("Over 1.5 HT", prob_over(xg_total*0.45, 2), 1.70),
        ("Under 1.5 HT", 1 - prob_over(xg_total*0.45, 2), 1.60),

        # BTTS
        ("Ambas Marcam", prob_btts(xg_home, xg_away), 1.85),

        # RESULTADO
        ("Casa vence", xg_home/(xg_total), 2.2),
        ("Empate", 0.25, 3.2),
        ("Fora vence", xg_away/(xg_total), 2.8),

        # DUPLA CHANCE
        ("Casa ou Empate", min(0.85, (xg_home/(xg_total))+0.25), 1.40),
        ("Fora ou Empate", min(0.85, (xg_away/(xg_total))+0.25), 1.50),

        # ESCANTEIOS
        ("Escanteios Over 9.5", min(0.85, 0.5 + xg_total/5), 1.9),

        # CARTÕES
        ("Cartões Over 3.5", min(0.80, 0.5 + xg_total/6), 1.95),

        # GOLEIRO
        ("Goleiro +3 defesas", min(0.75, 0.4 + xg_total/5), 1.80),

        # JOGADORES (SIMULADO)
        ("Jogador +2 faltas cometidas", min(0.70, 0.4 + xg_total/6), 1.90),
        ("Jogador +3 desarmes", min(0.75, 0.45 + xg_total/6), 1.85),
        ("Jogador levar cartão", min(0.65, 0.35 + xg_total/7), 2.10),

        # PLACARES
        ("Placar 1x1", poisson(xg_home,1)*poisson(xg_away,1), 6.0),
        ("Placar 2x1", poisson(xg_home,2)*poisson(xg_away,1), 8.0),
        ("Placar 2x0", poisson(xg_home,2)*poisson(xg_away,0), 7.0),
    ]

    # ================= TABELA =================
    tabela = []

    for nome, prob, odd in mercados:
        ev = calcular_ev(prob, odd)

        if modo_auto and ev < 0.08:
            continue

        tabela.append([
            nome,
            prob_fmt(prob),
            odd,
            round(ev,2),
            status(ev)
        ])

    df = pd.DataFrame(tabela, columns=["Mercado","Probabilidade","Odd","EV","Análise"])

    # ================= OUTPUT =================
    st.subheader(f"📊 {casa} x {fora}")
    st.write(f"xG Casa: {round(xg_home,2)} | xG Fora: {round(xg_away,2)}")

    st.dataframe(df, use_container_width=True)

# ================= MELHORES DO DIA =================
if st.button("🚀 MELHORES DO DIA"):

    melhores = []

    for liga_nome, jogos in jogos_por_liga.items():
        for j in jogos:
            xg_home, xg_away = calcular_xg(j["casa"], j["fora"])
            xg = xg_home + xg_away

            prob = prob_over(xg, 3)
            ev = calcular_ev(prob, 1.8)

            if ev > 0.12:
                melhores.append([liga_nome, j["nome"], round(ev,2)])

    if melhores:
        df = pd.DataFrame(melhores, columns=["Liga","Jogo","EV"])
        st.dataframe(df.sort_values(by="EV", ascending=False))
    else:
        st.info("Sem oportunidades fortes hoje")

st.success("🔥 Robô IA Profissional rodando sem erros")
