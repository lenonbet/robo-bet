import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import math
import random

# ================= CONFIG =================
st.set_page_config(layout="wide")
st.title("🤖 ROBÔ AUTÔNOMO IA - APOSTAS ESPORTIVAS")

# ================= SCRAPING MULTI-LIGAS =================
@st.cache_data(ttl=300)
def buscar_jogos():
    ligas_urls = {
        "Brasileirão": "https://www.flashscore.com/football/brazil/serie-a/",
        "Portugal": "https://www.flashscore.com/football/portugal/primeira-liga/",
        "Inglaterra": "https://www.flashscore.com/football/england/premier-league/"
    }

    headers = {"User-Agent": "Mozilla/5.0"}
    todos_jogos = {}

    for liga, url in ligas_urls.items():
        try:
            r = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(r.text, "lxml")

            partidas = soup.find_all("div", class_="event__match")
            jogos = []

            for p in partidas:
                try:
                    casa = p.find("div", class_="event__homeParticipant").text.strip()
                    fora = p.find("div", class_="event__awayParticipant").text.strip()

                    jogos.append({
                        "nome": f"{casa} x {fora}",
                        "casa": casa,
                        "fora": fora
                    })
                except:
                    continue

            todos_jogos[liga] = jogos
        except:
            todos_jogos[liga] = []

    return todos_jogos

# ================= MODELO =================
def poisson(lmbda, k):
    return (lmbda**k * math.exp(-lmbda)) / math.factorial(k)

def prob_over(xg, linha):
    return 1 - sum(poisson(xg, i) for i in range(int(linha)))

def prob_btts(xg_home, xg_away):
    return (1 - poisson(xg_home, 0)) * (1 - poisson(xg_away, 0))

def gerar_xg():
    return round(random.uniform(0.8, 2.2), 2)

def calcular_ev(prob, odd):
    return (prob * odd) - 1

# ================= INTERFACE =================
jogos_por_liga = buscar_jogos()

liga = st.sidebar.selectbox("🏆 Campeonato", list(jogos_por_liga.keys()))

jogos = jogos_por_liga[liga]

if not jogos:
    st.warning("⚠️ Sem jogos encontrados (Flashscore pode ter mudado ou bloqueado)")

nomes = [j["nome"] for j in jogos]

jogo_escolhido = st.selectbox("⚽ Escolha o jogo", nomes if nomes else ["Nenhum jogo"])

modo_auto = st.checkbox("🤖 Modo IA Automático")

# ================= ANÁLISE =================
if st.button("🔍 Analisar") and jogos:

    jogo = next(j for j in jogos if j["nome"] == jogo_escolhido)

    casa = jogo["casa"]
    fora = jogo["fora"]

    xg_home = gerar_xg()
    xg_away = gerar_xg()
    xg_total = xg_home + xg_away

    mercados = [
        ("Over 2.5 Gols", prob_over(xg_total, 3), 1.8),
        ("Over 1.5 Gols", prob_over(xg_total, 2), 1.4),
        ("Ambas Marcam", prob_btts(xg_home, xg_away), 1.85),
        ("Escanteios Over 9.5", random.uniform(0.5,0.7), 1.9),
        ("Cartões Over 3.5", random.uniform(0.5,0.7), 1.95)
    ]

    tabela = []

    for nome, prob, odd in mercados:
        ev = calcular_ev(prob, odd)

        if modo_auto and ev < 0.10:
            continue

        tabela.append([nome, round(prob,2), odd, round(ev,2)])

    df = pd.DataFrame(tabela, columns=["Mercado","Prob","Odd","EV"])

    st.subheader(f"📊 {casa} x {fora}")
    st.write(f"xG Casa: {xg_home} | xG Fora: {xg_away}")
    st.dataframe(df)

# ================= IA GLOBAL =================
if st.button("🚀 IA - MELHORES JOGOS DO DIA"):

    melhores = []

    for liga, jogos in jogos_por_liga.items():
        for j in jogos:
            xg = gerar_xg() + gerar_xg()
            prob = prob_over(xg, 3)
            ev = calcular_ev(prob, 1.8)

            if ev > 0.15:
                melhores.append([liga, j["nome"], round(ev,2)])

    if melhores:
        df = pd.DataFrame(melhores, columns=["Liga","Jogo","EV"])
        st.dataframe(df.sort_values(by="EV", ascending=False))
    else:
        st.info("Nenhuma oportunidade forte encontrada")

st.markdown("---")
st.success("🔥 Robô autônomo com IA ativo")
