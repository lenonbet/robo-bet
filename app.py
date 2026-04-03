import streamlit as st
import requests
import pandas as pd
import time
import datetime
import random

# ================= CONFIGURAÇÃO =================
API_KEY = "f465d2868695fccca02d7204db0eaba"
TOKEN = "8794081951:AAHriFzY5yj68sacN_JD4iuoZ4h8H3Su6TY"
CHAT_ID = "6661035382"
alertas = set()

# Principais campeonatos do dia
PRINCIPAIS_CAMPEONATOS = [
    "Premier League", "La Liga", "Serie A", "Bundesliga", "Ligue 1", "Champions League"
]

# ================= TELEGRAM =================
def enviar(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    try:
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg})
    except Exception as e:
        st.error(f"Erro ao enviar Telegram: {e}")

# ================= MATEMÁTICA =================
def prob_implicita(odd):
    return 1 / odd

def calcular_ev(prob, odd):
    return (prob * odd) - 1

def kelly(prob, odd, banca):
    b = odd - 1
    q = 1 - prob
    stake = (b * prob - q) / b
    return max(0, round(stake * banca, 2))

# ================= BUSCAR JOGOS =================
def buscar_jogos_hoje(live=False):
    hoje = datetime.datetime.now().strftime("%Y-%m-%d")
    url = f"https://v3.football.api-sports.io/fixtures?date={hoje}"
    if live:
        url += "&live=all"
    headers = {"x-apisports-key": API_KEY}
    try:
        res = requests.get(url, headers=headers, timeout=10).json()
        return res.get("response", [])
    except:
        return []

def filtrar_principais(jogos):
    return [j for j in jogos if j['league']['name'] in PRINCIPAIS_CAMPEONATOS]

# ================= MODELO =================
def calcular_probabilidade_ao_vivo(gols, tempo):
    ritmo = gols / max(tempo,1)
    base = 0.50
    ajuste = ritmo * 2.5
    prob = base + ajuste
    return min(max(prob, 0.05), 0.92)

def calcular_probabilidade_pre_jogo(odd):
    prob = 1 / odd
    return min(max(prob, 0.05), 0.95)

# ================= ANÁLISE AO VIVO =================
def analisar_ao_vivo(banca, ev_min=0.05, tempo_min=10):
    jogos = filtrar_principais(buscar_jogos_hoje(live=True))
    dados = []

    for j in jogos:
        try:
            casa = j['teams']['home']['name']
            fora = j['teams']['away']['name']
            tempo = j['fixture']['status']['elapsed'] or 1
            g1 = j['goals']['home'] or 0
            g2 = j['goals']['away'] or 0
            total = g1 + g2

            if tempo < tempo_min:
                continue

            prob = calcular_probabilidade_ao_vivo(total, tempo)
            # odds simuladas realistas
            odd = round(random.uniform(1.65, 1.9), 2)
            ev = calcular_ev(prob, odd)
            if ev < ev_min:
                continue

            stake_valor = kelly(prob, odd, banca)
            jogo_id = f"AO-{casa}-{fora}"

            if jogo_id not in alertas:
                msg = f"""💰 VALUE BET AO VIVO

{casa} x {fora}
⏱ {tempo} min

⚽ Over 2.5
📊 Prob: {round(prob,2)}
🎯 Odd: {odd}
💸 EV: {round(ev,2)}
💰 Stake: R${stake_valor}
"""
                enviar(msg)
                alertas.add(jogo_id)

            dados.append([f"{casa} x {fora}", tempo, total, round(prob,2), odd, round(ev,2), stake_valor])
        except:
            continue
    return dados

# ================= ANÁLISE PRÉ-JOGO =================
def analisar_pre_jogos(banca, ev_min=0.05):
    jogos = filtrar_principais(buscar_jogos_hoje(live=False))
    dados = []

    for j in jogos:
        try:
            casa = j['teams']['home']['name']
            fora = j['teams']['away']['name']
            # odds simuladas realistas
            odd = round(random.uniform(1.65, 1.9), 2)
            prob = calcular_probabilidade_pre_jogo(odd)
            ev = calcular_ev(prob, odd)
            if ev < ev_min:
                continue

            stake_valor = kelly(prob, odd, banca)
            jogo_id = f"PRE-{casa}-{fora}"

            if jogo_id not in alertas:
                msg = f"""💰 VALUE BET PRÉ-JOGO

{casa} x {fora}

📊 Prob: {round(prob,2)}
🎯 Odd: {odd}
💸 EV: {round(ev,2)}
💰 Stake: R${stake_valor}
"""
                enviar(msg)
                alertas.add(jogo_id)

            dados.append([f"{casa} x {fora}", round(prob,2), odd, round(ev,2), stake_valor])
        except:
            continue
    return dados

# ================= APP =================
st.title("💰 ROBÔ TOP 1% - VALUE BET AO VIVO & PRÉ-JOGO")
banca = st.number_input("💰 Sua banca", value=1000)
status = st.empty()

while True:
    status.warning("🔄 Analisando jogos AO VIVO e PRÉ-JOGO...")

    dados_ao_vivo = analisar_ao_vivo(banca)
    dados_pre_jogo = analisar_pre_jogos(banca)

    if dados_ao_vivo:
        df_vivo = pd.DataFrame(dados_ao_vivo, columns=["Jogo","Min","Gols","Prob","Odd","EV","Stake"])
        st.subheader("⚡ AO VIVO")
        st.dataframe(df_vivo.sort_values(by="EV", ascending=False))
    else:
        st.info("Nenhuma entrada forte AO VIVO agora")

    if dados_pre_jogo:
        df_pre = pd.DataFrame(dados_pre_jogo, columns=["Jogo","Prob","Odd","EV","Stake"])
        st.subheader("🕒 PRÉ-JOGO")
        st.dataframe(df_pre.sort_values(by="EV", ascending=False))
    else:
        st.info("Nenhuma entrada forte PRÉ-JOGO agora")

    time.sleep(180)
