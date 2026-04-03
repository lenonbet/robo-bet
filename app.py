import streamlit as st
import requests
import pandas as pd
import time
import math
import os

# ================= CONFIG =================
API_KEY = "f465d2868695fccca02d7204db0eaba"
TOKEN = "8794081951:AAHriFzY5yj68sacN_JD4iuoZ4h8H3Su6TY"
CHAT_ID = "6661035382"

ODD_PADRAO = 1.80
EV_MINIMO = 0.05
KELLY_FRACAO = 0.25

ARQUIVO = "historico.csv"

headers = {"x-apisports-key": API_KEY}

# ================= TELEGRAM =================
def enviar(msg):
    try:
        requests.post(
            f"https://api.telegram.org/bot{TOKEN}/sendMessage",
            data={"chat_id": CHAT_ID, "text": msg}
        )
    except:
        pass

# ================= MATEMÁTICA =================
def poisson(lmbda, k):
    return (lmbda**k * math.exp(-lmbda)) / math.factorial(k)

def prob_over_25(xg):
    return 1 - sum(poisson(xg, i) for i in range(3))

def prob_btts(xg_home, xg_away):
    return (1 - poisson(xg_home, 0)) * (1 - poisson(xg_away, 0))

def calcular_ev(prob, odd):
    return (prob * odd) - 1

def kelly(prob, odd, banca):
    b = odd - 1
    q = 1 - prob
    k = (b * prob - q) / b
    return max(0, round(k * banca * KELLY_FRACAO, 2))

# ================= DADOS =================
def jogos_hoje():
    url = "https://v3.football.api-sports.io/fixtures?next=30"
    return requests.get(url, headers=headers).json().get("response", [])

def jogos_ao_vivo():
    url = "https://v3.football.api-sports.io/fixtures?live=all"
    return requests.get(url, headers=headers).json().get("response", [])

def ultimos_jogos(team_id):
    url = f"https://v3.football.api-sports.io/fixtures?team={team_id}&last=5"
    return requests.get(url, headers=headers).json().get("response", [])

# ================= IA SIMPLES =================
def salvar(dados):
    df = pd.DataFrame([dados])

    if os.path.exists(ARQUIVO):
        df.to_csv(ARQUIVO, mode='a', header=False, index=False)
    else:
        df.to_csv(ARQUIVO, index=False)

def roi():
    if not os.path.exists(ARQUIVO):
        return 0

    df = pd.read_csv(ARQUIVO)

    if df.empty:
        return 0

    lucro = df["lucro"].sum()
    stake = df["stake"].sum()

    return round((lucro / stake) * 100, 2) if stake > 0 else 0

# ================= ANÁLISE =================
def media_gols(jogos, tipo):
    gols = []
    for j in jogos:
        if tipo == "home":
            gols.append(j['goals']['home'] or 0)
        else:
            gols.append(j['goals']['away'] or 0)
    return sum(gols)/len(gols) if gols else 1.2

def analisar_jogo(jogo, ult_casa, ult_fora, banca):

    casa = jogo['teams']['home']['name']
    fora = jogo['teams']['away']['name']

    xg_home = media_gols(ult_casa, "home")
    xg_away = media_gols(ult_fora, "away")

    xg_total = xg_home + xg_away

    mercados = {
        "Over 2.5": prob_over_25(xg_total),
        "BTTS": prob_btts(xg_home, xg_away),
    }

    resultados = []

    for nome, prob in mercados.items():
        odd_justa = round(1 / prob, 2) if prob > 0 else 0
        odd_mercado = ODD_PADRAO

        ev = calcular_ev(prob, odd_mercado)

        if ev >= EV_MINIMO:
            stake = kelly(prob, odd_mercado, banca)

            resultados.append({
                "Jogo": f"{casa} x {fora}",
                "Mercado": nome,
                "Prob": round(prob, 2),
                "Odd Justa": odd_justa,
                "Odd Mercado": odd_mercado,
                "EV": round(ev, 2),
                "Stake": stake
            })

    return resultados

# ================= STREAMLIT =================
st.set_page_config(layout="wide")
st.title("💰 ROBÔ PROFISSIONAL DE APOSTAS (NÍVEL CASA)")

banca = st.sidebar.number_input("💰 Banca", value=1000)

modo = st.sidebar.selectbox("Modo", ["Pré-live", "Ao vivo"])

st.sidebar.metric("ROI", f"{roi()}%")

status = st.empty()
tabela = st.empty()

alertados = set()

while True:

    status.warning("🔄 Analisando jogos...")

    jogos = jogos_hoje() if modo == "Pré-live" else jogos_ao_vivo()

    entradas = []

    for j in jogos:
        try:
            home_id = j['teams']['home']['id']
            away_id = j['teams']['away']['id']

            ult_casa = ultimos_jogos(home_id)
            ult_fora = ultimos_jogos(away_id)

            analises = analisar_jogo(j, ult_casa, ult_fora, banca)

            for a in analises:
                entradas.append(a)

                chave = a["Jogo"] + a["Mercado"]

                if chave not in alertados:
                    msg = f"""
🔥 VALUE BET

{a['Jogo']}
🎯 {a['Mercado']}

📊 Prob: {a['Prob']}
💰 Odd: {a['Odd Mercado']}
📈 EV: {a['EV']}
💸 Stake: R${a['Stake']}
"""
                    enviar(msg)

                    salvar({
                        "jogo": a["Jogo"],
                        "mercado": a["Mercado"],
                        "stake": a["Stake"],
                        "lucro": 0
                    })

                    alertados.add(chave)

        except:
            continue

    if entradas:
        df = pd.DataFrame(entradas)
        tabela.dataframe(df.sort_values(by="EV", ascending=False))
    else:
        tabela.info("Nenhuma oportunidade agora")

    time.sleep(120)
