import streamlit as st
import pandas as pd

from data import buscar_jogos
from model import *
from stats import gerar_stats
from telegram import enviar

st.set_page_config(layout="wide")
st.title("🤖 ROBÔ IA ULTRA - BET365 STYLE")

# ================= JOGOS =================
jogos_por_liga = buscar_jogos()

if not jogos_por_liga:
    st.error("❌ Nenhum jogo encontrado")
    st.stop()

liga = st.selectbox("🏆 Campeonato", list(jogos_por_liga.keys()))
jogos = jogos_por_liga[liga]

jogo_nome = st.selectbox("⚽ Jogo", [j["nome"] for j in jogos])

modo_auto = st.checkbox("🤖 Modo IA automático")

# ================= ANALISE =================
if st.button("🔍 Analisar Jogo"):

    jogo = next(j for j in jogos if j["nome"] == jogo_nome)

    casa = jogo["casa"]
    fora = jogo["fora"]

    xg_home, xg_away = calcular_xg()
    xg_total = xg_home + xg_away

    stats = gerar_stats(xg_home, xg_away)

    mercados = [
        ("Over 2.5 Gols", prob_over(xg_total, 3)),
        ("Over 1.5 Gols", prob_over(xg_total, 2)),
        ("Ambas Marcam", prob_btts(xg_home, xg_away)),
        ("Escanteios Over 9.5", prob_escanteios(stats)),
        ("Cartões Over 3.5", prob_cartoes(stats)),
        ("Casa vence", xg_home / xg_total),
        ("Fora vence", xg_away / xg_total),
    ]

    tabela = []

    for nome, prob in mercados:

        odd_real = odd_justa(prob)
        odd_bet = odd_mercado(prob)
        ev = calcular_ev(prob, odd_bet)

        if modo_auto and ev < 0.05:
            continue

        if ev > 0.10:
            sinal = "🟢 FORTE"
        elif ev > 0:
            sinal = "🟡 MÉDIO"
        else:
            sinal = "🔴 RISCO"

        if ev > 0.12:
            enviar(f"""🔥 ENTRADA FORTE

{casa} x {fora}
{nome}
Prob: {round(prob*100,1)}%
Odd: {odd_bet}
EV: {round(ev,2)}""")

        tabela.append([
            nome,
            f"{round(prob*100,1)}%",
            odd_real,
            odd_bet,
            round(ev,2),
            sinal
        ])

    df = pd.DataFrame(tabela, columns=[
        "Mercado","Probabilidade","Odd Justa","Odd Bet365","EV","Sinal"
    ])

    st.subheader(f"{casa} x {fora}")
    st.write("📊 Estatísticas simuladas:", stats)
    st.dataframe(df)

# ================= SCANNER =================
if st.button("🚀 SCANNER ULTRA"):

    sinais = []

    for liga, jogos in jogos_por_liga.items():
        for j in jogos:

            xg_home, xg_away = calcular_xg()
            xg_total = xg_home + xg_away

            prob = prob_over(xg_total, 3)
            odd = odd_mercado(prob)
            ev = calcular_ev(prob, odd)

            if ev > 0.12:
                sinais.append([liga, j["nome"], round(ev,2)])

    if sinais:
        df = pd.DataFrame(sinais, columns=["Liga","Jogo","EV"])
        st.dataframe(df.sort_values(by="EV", ascending=False))
    else:
        st.info("Sem entradas fortes")

st.success("🔥 ROBÔ ULTRA ATIVO")
