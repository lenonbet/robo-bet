import streamlit as st

# ================= CONFIGURAÇÃO =================
TOKEN = "SEU_TOKEN"
CHAT_ID = "SEU_CHAT_ID"

# ================= TELEGRAM =================
def enviar(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    try:
        import requests
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

# ================= PROBABILIDADES SIMULADAS =================
def prob_pre_gols():
    return 0.55  # Over 2.5

def prob_ambas_marcam():
    return 0.5

def prob_resultado():
    return 0.35  # qualquer resultado individual

def prob_escanteios():
    return 0.6  # Over 9.5 escanteios

def prob_cartoes():
    return 0.55  # Over 2.5 cartões

# ================= STREAMLIT =================
st.title("💰 SIMULAÇÃO PRÉ-LIVE - São Paulo x Cruzeiro 04/04/2026")

banca = st.number_input("💰 Sua banca", value=1000)

# Seleção de mercados
mercados = st.multiselect(
    "Selecione mercados",
    ["Over 2.5 Gols","Ambas Marcam","Resultado 1","Resultado X","Resultado 2",
     "Over 9.5 Escanteios","Over 2.5 Cartões"],
    default=["Over 2.5 Gols","Ambas Marcam","Resultado 1","Resultado X","Resultado 2",
             "Over 9.5 Escanteios","Over 2.5 Cartões"]
)

time_casa = "São Paulo"
time_fora = "Cruzeiro"

tabela = []
for mercado in mercados:
    if mercado == "Over 2.5 Gols":
        prob = prob_pre_gols()
        odd = 1.8
    elif mercado == "Ambas Marcam":
        prob = prob_ambas_marcam()
        odd = 1.85
    elif mercado.startswith("Resultado"):
        prob = prob_resultado()
        odd = 2.5
    elif mercado == "Over 9.5 Escanteios":
        prob = prob_escanteios()
        odd = 1.9
    elif mercado == "Over 2.5 Cartões":
        prob = prob_cartoes()
        odd = 1.95
    else:
        prob = 0.5
        odd = 1.8

    ev = calcular_ev(prob, odd)
    stake = kelly(prob, odd, banca)

    tabela.append([mercado, round(prob,2), odd, round(ev,2), stake])

    # Alerta Telegram para EV >= 0.15
    if ev >= 0.15:
        enviar(f"💰 SIMULAÇÃO PRÉ-LIVE\n{time_casa} x {time_fora}\nMercado: {mercado}\nProb: {round(prob,2)}\nOdd: {odd}\nEV: {round(ev,2)}\nStake: R${stake}")

st.subheader(f"{time_casa} x {time_fora} - Mercados Pré-Live Simulados")
import pandas as pd
df = pd.DataFrame(tabela, columns=["Mercado","Prob","Odd","EV","Stake"])
st.dataframe(df)
