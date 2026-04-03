import streamlit as st
import pandas as pd
import datetime

from utils import buscar_jogos_por_data
from model import *
from telegram import enviar

st.set_page_config(layout="wide")
st.title("🤖 ROBÔ IA PROFISSIONAL - BET365 STYLE")

# ================= DATA =================
col1, col2 = st.columns(2)

with col1:
    data_inicio = st.date_input("📅 Data inicial", datetime.date.today())

with col2:
    dias = st.slider("📆 Próximos dias", 1, 5, 2)

# ================= BUSCAR JOGOS =================
jogos_por_liga = {}

for i in range(dias):
    data = data_inicio + datetime.timedelta(days=i)
    data_str = data.strftime("%Y-%m-%d")

    dados = buscar_jogos_por_data(data_str)

    for liga, jogos in dados.items():
        if liga not in jogos_por_liga:
            jogos_por_liga[liga] = []
        jogos_por_liga[liga].extend(jogos)

if not jogos_por_liga:
    st.error("❌ Nenhum jogo encontrado")
    st.stop()

# ================= ESCOLHAS =================
liga = st.selectbox("🏆 Campeonato", list(jogos_por_liga.keys()))
jogos = jogos_por_liga[liga]

jogo_nome = st.selectbox("⚽ Jogo", [j["nome"] for j in jogos])

modo_auto = st.checkbox("🤖 Modo automático (só valor alto)")

# ================= ANALISAR =================
if st.button("🔍 Analisar Jogo"):

    jogo = next(j for j in jogos if j["nome"] == jogo_nome)

    casa = jogo["casa"]
    fora = jogo["fora"]

    xg_home, xg_away = calcular_xg()
    xg_total = xg_home + xg_away

    mercados = [
        ("Over 2.5 Gols", prob_over(xg_total, 3)),
        ("Over 1.5 Gols", prob_over(xg_total, 2)),
        ("Ambas Marcam", prob_btts(xg_home, xg_away)),
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
            sinal = "🟢 ENTRAR"
        elif ev > 0:
            sinal = "🟡 MÉDIO"
        else:
            sinal = "🔴 EV-"

        # TELEGRAM
        if ev > 0.12:
            enviar(f"🔥 APOSTA DE VALOR\n{casa} x {fora}\n{nome}\nOdd: {odd_bet}\nEV: {round(ev,2)}")

        tabela.append([
            nome,
            f"{round(prob*100,1)}%",
            odd_real,
            odd_bet,
            round(ev,2),
            sinal
        ])

    df = pd.DataFrame(tabela, columns=[
        "Mercado","Probabilidade","Odd Justa","Odd Mercado","EV","Sinal"
    ])

    st.subheader(f"📊 {casa} x {fora}")
    st.write(f"xG: {round(xg_home,2)} x {round(xg_away,2)}")
    st.dataframe(df)

# ================= SCANNER =================
if st.button("🚀 SCANNER DO DIA"):

    sinais = []

    for liga, jogos in jogos_por_liga.items():
        for j in jogos:

            xg_home, xg_away = calcular_xg()
            xg_total = xg_home + xg_away

            prob = prob_over(xg_total, 3)
            odd = odd_mercado(prob)
            ev = calcular_ev(prob, odd)

            if ev > 0.12:
                sinais.append([
                    liga,
                    j["nome"],
                    round(ev,2)
                ])

    if sinais:
        df = pd.DataFrame(sinais, columns=["Liga","Jogo","EV"])
        st.dataframe(df.sort_values(by="EV", ascending=False))
    else:
        st.info("Nenhuma entrada forte encontrada")

st.success("🔥 Robô rodando estilo profissional")
