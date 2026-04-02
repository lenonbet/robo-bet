import streamlit as st
import requests
import pandas as pd
import numpy as np

API_KEY = "af465d2868695fccca02d7204db0eaba"

def calcular_ev(prob, odd):
    return (prob * odd) - 1

def stake(banca, ev):
    return round(banca * (0.02 + ev), 2)

def buscar_jogos():
    url = "https://v3.football.api-sports.io/fixtures?live=all"
    headers = {"x-apisports-key": API_KEY}
    res = requests.get(url, headers=headers).json()
    return res.get("response", [])

def analisar():
    jogos = buscar_jogos()
    dados = []

    for j in jogos[:10]:
        casa = j['teams']['home']['name']
        fora = j['teams']['away']['name']
        g1 = j['goals']['home'] or 0
        g2 = j['goals']['away'] or 0

        total = g1 + g2
        prob = min(0.55 + total*0.1, 0.85)
        odd = 1.90
        ev = calcular_ev(prob, odd)

        if ev > 0.1:
            dados.append({
                "Jogo": f"{casa} x {fora}",
                "Mercado": "Over 2.5",
                "Prob": round(prob,2),
                "Odd": odd,
                "EV": round(ev,2)
            })

    return dados

st.title("🚀 Robô com Dados Reais")

banca = st.number_input("Banca", value=1000)

if st.button("Buscar Entradas"):
    dados = analisar()
    if dados:
        df = pd.DataFrame(dados)
        df['Stake'] = df['EV'].apply(lambda x: stake(banca, x))
        st.dataframe(df)
    else:
        st.warning("Sem jogos ao vivo agora")
