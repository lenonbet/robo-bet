import streamlit as st
import requests
import pandas as pd
import time

API_KEY = "f465d2868695fccca02d7204db0eaba"
TOKEN = "8794081951:AAHriFzY5yj68sacN_JD4iuoZ4h8H3Su6TY"
CHAT_ID = "6661035382"

alertas = set()

# ================= TELEGRAM =================
def enviar(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    try:
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg})
    except:
        pass

# ================= MATEMÁTICA PROFISSIONAL =================

def prob_implicita(odd):
    return 1 / odd

def calcular_ev(prob, odd):
    return (prob * odd) - 1

def kelly(prob, odd, banca):
    b = odd - 1
    q = 1 - prob
    stake = (b * prob - q) / b
    return max(0, round(stake * banca, 2))

# ================= DADOS AO VIVO =================

def buscar_jogos():
    url = "https://v3.football.api-sports.io/fixtures?live=all"
    headers = {"x-apisports-key": API_KEY}
    res = requests.get(url, headers=headers).json()
    return res.get("response", [])

# ================= MODELO INTELIGENTE =================

def calcular_probabilidade(gols, tempo):
    # ritmo de jogo
    ritmo = gols / max(tempo, 1)

    # modelo melhorado
    base = 0.48
    ajuste = ritmo * 2.2

    prob = base + ajuste

    return min(max(prob, 0.05), 0.92)

# ================= ANÁLISE =================

def analisar(banca):
    jogos = buscar_jogos()
    dados = []

    for j in jogos:
        try:
            casa = j['teams']['home']['name']
            fora = j['teams']['away']['name']
            tempo = j['fixture']['status']['elapsed'] or 1

            g1 = j['goals']['home'] or 0
            g2 = j['goals']['away'] or 0
            total = g1 + g2

            # 🔴 FILTRO PROFISSIONAL
            if tempo < 20:
                continue

            prob = calcular_probabilidade(total, tempo)

            # 🎯 simulação de odd de mercado
            odd = 1.75

            ev = calcular_ev(prob, odd)

            # 🔥 SÓ ENTRADA FORTE
            if ev < 0.15:
                continue

            stake_valor = kelly(prob, odd, banca)

            jogo_id = f"{casa}-{fora}"

            if jogo_id not in alertas:
                msg = f"""💰 VALUE BET FORTE

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

            dados.append([
                f"{casa} x {fora}",
                tempo,
                total,
                prob,
                odd,
                ev,
                stake_valor
            ])

        except:
            continue

    return dados

# ================= APP =================

st.title("💰 ROBÔ TOP 1% - VALUE BET PROFISSIONAL")

banca = st.number_input("💰 Sua banca", value=1000)

status = st.empty()

while True:
    status.warning("🔄 Analisando jogos AO VIVO...")

    dados = analisar(banca)

    if dados:
        df = pd.DataFrame(dados, columns=[
            "Jogo", "Min", "Gols", "Prob", "Odd", "EV", "Stake"
        ])

        st.dataframe(df.sort_values(by="EV", ascending=False))
    else:
        st.info("Nenhuma entrada forte agora")

    time.sleep(180)
