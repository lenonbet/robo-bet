import streamlit as st
import requests
import pandas as pd
def enviar_telegram(msg):
    TOKEN = "8794081951:AAHriFzY5yj68sacN_JD4iuoZ4h8H3Su6TY"
    CHAT_ID = "6661035382"

    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})
API_KEY = "f465d2868695fccca02d7204db0eaba"

def calcular_ev(prob, odd):
    return (prob * odd) - 1

def stake(banca, ev):
    return round(banca * (0.02 + ev), 2)

# ================= FUTEBOL =================

def buscar_futebol():
    url = "https://v3.football.api-sports.io/fixtures?date=2026-04-02"
    headers = {"x-apisports-key": API_KEY}
    res = requests.get(url, headers=headers).json()
    return res.get("response", [])

def analisar_futebol():
    jogos = buscar_futebol()
    dados = []

    for j in jogos[:30]:
        casa = j['teams']['home']['name']
        fora = j['teams']['away']['name']
        g1 = j['goals']['home'] or 0
        g2 = j['goals']['away'] or 0

        total = g1 + g2

        prob_over = min(0.55 + total * 0.1, 0.85)
        prob_btts = min(0.50 + (g1+g2)*0.08, 0.80)
        prob_ht = min(0.45 + total * 0.08, 0.75)

        odd = 1.90

        if calcular_ev(prob_over, odd) > 0.12:
    msg = f"🔥 ENTRADA\n{casa} x {fora}\nOver 2.5\nEV: {round(calcular_ev(prob_over, odd),2)}"
    enviar_telegram(msg)
        if calcular_ev(prob_btts, odd) > 0.12:
            dados.append([f"{casa} x {fora}", "BTTS", prob_btts, odd])

        if calcular_ev(prob_ht, odd) > 0.12:
            dados.append([f"{casa} x {fora}", "Over HT", prob_ht, odd])

    return dados

# ================= NBA =================

def buscar_nba():
    url = "https://v1.basketball.api-sports.io/games?date=2026-04-02"
    headers = {"x-apisports-key": API_KEY}
    res = requests.get(url, headers=headers).json()
    return res.get("response", [])

def analisar_nba():
    jogos = buscar_nba()
    dados = []

    for j in jogos[:15]:
        casa = j['teams']['home']['name']
        fora = j['teams']['away']['name']

        pontos_casa = j['scores']['home']['points'] or 0
        pontos_fora = j['scores']['away']['points'] or 0

        total = pontos_casa + pontos_fora

        # modelo simples de over pontos
        prob_over = min(0.55 + total * 0.002, 0.80)
        odd = 1.90
        ev = calcular_ev(prob_over, odd)

        if ev > 0.10:
            dados.append([f"{casa} x {fora}", "Over Pontos", prob_over, odd])

    return dados

# ================= APP =================

st.title("🔥 ROBÔ ELITE (FUTEBOL + NBA)")

banca = st.number_input("💰 Sua banca", value=1000)

if st.button("🚀 Buscar Entradas ELITE"):

    dados_fut = analisar_futebol()
    dados_nba = analisar_nba()

    dados_total = dados_fut + dados_nba

    if dados_total:
        df = pd.DataFrame(dados_total, columns=["Jogo", "Mercado", "Prob", "Odd"])
        df["EV"] = df.apply(lambda x: calcular_ev(x["Prob"], x["Odd"]), axis=1)
        df["Stake"] = df["EV"].apply(lambda x: stake(banca, x))

        st.dataframe(df.sort_values(by="EV", ascending=False))
    else:
        st.warning("Sem boas entradas agora")
