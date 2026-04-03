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

# Principais campeonatos do dia (use nomes reais da API)
PRINCIPAIS_CAMPEONATOS = [
    "English Premier League", "La Liga", "Serie A", "Bundesliga", "Ligue 1", "Champions League"
]

# ================= TELEGRAM =================
def enviar(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    try:
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg})
    except:
        pass

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
    hoje_utc = datetime.datetime.utcnow().strftime("%Y-%m-%d")
    if live:
        url = "https://v3.football.api-sports.io/fixtures?live=all"
    else:
        url = f"https://v3.football.api-sports.io/fixtures?date={hoje_utc}"
    headers = {"x-apisports-key": API_KEY}
    try:
        res = requests.get(url, headers=headers, timeout=10).json()
        return res.get("response", [])
    except:
        return []

def filtrar_principais(jogos, campeonatos):
    return [j for j in jogos if j.get('league', {}).get('name') in campeonatos]

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

# ================= APP =================
st.title("💰 ROBÔ TOP 1% - JOGOS DO DIA & MERCADOS")

# Input do usuário
banca = st.number_input("💰 Sua banca", value=1000)
modo = st.selectbox("Escolha o modo:", ["PRÉ-JOGO", "AO VIVO", "TODOS"])
campeonatos = st.multiselect("Filtrar campeonatos:", PRINCIPAIS_CAMPEONATOS, default=PRINCIPAIS_CAMPEONATOS)

# Buscar jogos
if modo in ["PRÉ-JOGO", "TODOS"]:
    jogos_pre = filtrar_principais(buscar_jogos_hoje(live=False), campeonatos)
else:
    jogos_pre = []

if modo in ["AO VIVO", "TODOS"]:
    jogos_vivo = filtrar_principais(buscar_jogos_hoje(live=True), campeonatos)
else:
    jogos_vivo = []

# ================= FUNÇÃO PARA MOSTRAR MERCADOS =================
def mostrar_mercados(jogos, banca, ao_vivo=False):
    dados = []
    for j in jogos:
        try:
            casa = j.get('teams', {}).get('home', {}).get('name', 'Desconhecido')
            fora = j.get('teams', {}).get('away', {}).get('name', 'Desconhecido')
            tempo = j.get('fixture', {}).get('status', {}).get('elapsed') or 0
            g1 = j.get('goals', {}).get('home') or 0
            g2 = j.get('goals', {}).get('away') or 0
            total = g1 + g2

            mercados = []

            # Over 2.5
            odd_over = round(random.uniform(1.65, 1.9), 2)
            if ao_vivo:
                prob_over = calcular_probabilidade_ao_vivo(total, tempo)
            else:
                prob_over = calcular_probabilidade_pre_jogo(odd_over)
            ev_over = calcular_ev(prob_over, odd_over)
            stake_over = kelly(prob_over, odd_over, banca)
            mercados.append(("Over 2.5", odd_over, round(prob_over,2), round(ev_over,2), stake_over))

            # Ambas Marcam
            odd_btts = round(random.uniform(1.7, 1.95),2)
            if ao_vivo:
                prob_btts = calcular_probabilidade_ao_vivo(total, tempo)
            else:
                prob_btts = calcular_probabilidade_pre_jogo(odd_btts)
            ev_btts = calcular_ev(prob_btts, odd_btts)
            stake_btts = kelly(prob_btts, odd_btts, banca)
            mercados.append(("Ambas Marcam", odd_btts, round(prob_btts,2), round(ev_btts,2), stake_btts))

            for m in mercados:
                # alertas para EV > 0.1
                if (ao_vivo and f"AO-{casa}-{fora}-{m[0]}" not in alertas) or (not ao_vivo and f"PRE-{casa}-{fora}-{m[0]}" not in alertas):
                    if m[3] >= 0.1:
                        msg_tipo = "AO VIVO" if ao_vivo else "PRÉ-JOGO"
                        msg = f"""💰 VALUE BET {msg_tipo}

{casa} x {fora}
Mercado: {m[0]}
📊 Prob: {m[2]}
🎯 Odd: {m[1]}
💸 EV: {m[3]}
💰 Stake: R${m[4]}
"""
                        enviar(msg)
                        alertas.add(f"{'AO' if ao_vivo else 'PRE'}-{casa}-{fora}-{m[0]}")

            dados.append([casa, fora, tempo if ao_vivo else "-", *[item for sub in mercados for item in sub]])
        except:
            continue
    return dados

# ================= MOSTRAR TABELA =================
if jogos_vivo:
    st.subheader("⚡ AO VIVO")
    df_vivo = pd.DataFrame(mostrar_mercados(jogos_vivo, banca, ao_vivo=True),
                           columns=["Casa","Fora","Min",
                                    "Mercado1","Odd1","Prob1","EV1","Stake1",
                                    "Mercado2","Odd2","Prob2","EV2","Stake2"])
    st.dataframe(df_vivo)

if jogos_pre:
    st.subheader("🕒 PRÉ-JOGO")
    df_pre = pd.DataFrame(mostrar_mercados(jogos_pre, banca, ao_vivo=False),
                          columns=["Casa","Fora","Min",
                                   "Mercado1","Odd1","Prob1","EV1","Stake1",
                                   "Mercado2","Odd2","Prob2","EV2","Stake2"])
    st.dataframe(df_pre)
