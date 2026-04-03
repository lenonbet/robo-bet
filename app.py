import streamlit as st
import requests
import pandas as pd
import datetime
import time

# ================= CONFIG =================
API_KEY = "f465d2868695fccca02d7204db0eaba"
TOKEN = "8794081951:AAHriFzY5yj68sacN_JD4iuoZ4h8H3Su6TY"
CHAT_ID = "6661035382"

LIGAS_IDS = [
    71,   # Brasileirão
    39,   # Premier League
    140,  # La Liga
    135,  # Serie A Itália
    78,   # Bundesliga
    61,   # Ligue 1
    94,   # Liga Portugal
    2     # Champions League
]

# ================= TELEGRAM =================
def enviar(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    try:
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg})
    except:
        pass

# ================= CÁLCULOS =================
def calcular_ev(prob, odd):
    return (prob * odd) - 1

def kelly(prob, odd, banca):
    b = odd - 1
    q = 1 - prob
    stake = (b * prob - q) / b
    return max(0, round(stake * banca, 2))

# ================= BUSCAR JOGOS =================
def buscar_jogos(data):
    headers = {"x-apisports-key": API_KEY}
    jogos_total = []

    for liga in LIGAS_IDS:
        try:
            url = f"https://v3.football.api-sports.io/fixtures?date={data}&league={liga}"
            res = requests.get(url, headers=headers, timeout=10).json()
            jogos_total += res.get("response", [])
        except:
            continue

    return jogos_total

# ================= MODELO INTELIGENTE =================
def prob_model(mercado):
    if "Over 2.5" in mercado:
        return 0.58
    elif "Ambas" in mercado:
        return 0.55
    elif "Resultado 1" in mercado:
        return 0.40
    elif "Resultado X" in mercado:
        return 0.28
    elif "Resultado 2" in mercado:
        return 0.32
    elif "Escanteios" in mercado:
        return 0.59
    elif "Cartões" in mercado:
        return 0.62
    return 0.5

# ================= ODDS =================
def odds_model(mercado):
    odds = {
        "Over 2.5 Gols": 1.90,
        "Ambas Marcam": 1.85,
        "Resultado 1": 2.20,
        "Resultado X": 3.10,
        "Resultado 2": 3.00,
        "Over 9.5 Escanteios": 1.95,
        "Over 2.5 Cartões": 1.90
    }
    return odds.get(mercado, 1.80)

# ================= APP =================
st.title("💰 ROBÔ PROFISSIONAL - ANÁLISE COMPLETA DE JOGOS")

banca = st.number_input("💰 Sua banca", value=1000)
dias = st.slider("Dias para analisar", 0, 3, 0)
modo_teste = st.checkbox("Modo Teste (ver tudo)")

mercados = st.multiselect(
    "Mercados para análise",
    [
        "Over 2.5 Gols",
        "Ambas Marcam",
        "Resultado 1",
        "Resultado X",
        "Resultado 2",
        "Over 9.5 Escanteios",
        "Over 2.5 Cartões"
    ],
    default=[
        "Over 2.5 Gols",
        "Ambas Marcam",
        "Over 9.5 Escanteios",
        "Over 2.5 Cartões"
    ]
)

status = st.empty()

# ================= LOOP =================
while True:
    status.warning("🔄 Analisando jogos...")

    dados = []

    datas = [
        (datetime.datetime.utcnow() + datetime.timedelta(days=i)).strftime("%Y-%m-%d")
        for i in range(dias + 1)
    ]

    for data in datas:
        jogos = buscar_jogos(data)

        for j in jogos:
            try:
                casa = j['teams']['home']['name']
                fora = j['teams']['away']['name']
                liga = j['league']['name']

                for mercado in mercados:
                    prob = prob_model(mercado)
                    odd = odds_model(mercado)
                    ev = calcular_ev(prob, odd)
                    stake = kelly(prob, odd, banca)

                    filtro = -1 if modo_teste else 0.05

                    if ev >= filtro:
                        dados.append([
                            liga,
                            f"{casa} x {fora}",
                            mercado,
                            round(prob, 2),
                            odd,
                            round(ev, 2),
                            stake
                        ])

                        # ALERTA TELEGRAM
                        if ev >= 0.08:
                            enviar(
                                f"💰 VALUE BET\n"
                                f"{casa} x {fora}\n"
                                f"{liga}\n"
                                f"Mercado: {mercado}\n"
                                f"Prob: {round(prob,2)}\n"
                                f"Odd: {odd}\n"
                                f"EV: {round(ev,2)}\n"
                                f"Stake: R${stake}"
                            )
            except:
                continue

    if dados:
        df = pd.DataFrame(dados, columns=[
            "Liga", "Jogo", "Mercado", "Prob", "Odd", "EV", "Stake"
        ])

        df = df.sort_values(by="EV", ascending=False)
        st.dataframe(df)
    else:
        st.info("Nenhuma oportunidade encontrada")

    time.sleep(120)

