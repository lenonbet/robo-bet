import streamlit as st
import requests
import datetime

# ================= CONFIGURAÇÃO =================
API_KEY_FOOT = "f465d2868695fccca02d7204db0eaba"
TOKEN = "8794081951:AAHriFzY5yj68sacN_JD4iuoZ4h8H3Su6TY"
CHAT_ID = "6661035382"

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

def prob_pre_jogo(odd):
    return 1 / odd

def prob_escanteios(time_casa, time_fora):
    # Probabilidade estimada de over 9.5 escanteios
    return 0.6  # valor de teste, depois pode ser ajustado com estatísticas reais

def prob_cartoes(time_casa, time_fora):
    # Probabilidade estimada de over 2.5 cartões
    return 0.55  # valor de teste, depois pode ser ajustado com estatísticas reais

# ================= BUSCAR JOGO =================
def buscar_jogo_especifico(campeonato, data, time_casa, time_fora):
    url = f"https://v3.football.api-sports.io/fixtures?date={data}"
    headers = {"x-apisports-key": API_KEY_FOOT}
    try:
        res = requests.get(url, headers=headers, timeout=10).json().get("response", [])
        for j in res:
            home = j.get("teams", {}).get("home", {}).get("name")
            away = j.get("teams", {}).get("away", {}).get("name")
            league = j.get("league", {}).get("name")
            if home == time_casa and away == time_fora and league == campeonato:
                return j
        return None
    except:
        return None

# ================= STREAMLIT =================
st.title("💰 TESTE PRÉ-LIVE - SÉRIE A 04/04/2026")

banca = st.number_input("💰 Sua banca", value=1000)

# Definindo jogo específico
campeonato = "Serie A"
data = "2026-04-04"
time_casa = "São Paulo"
time_fora = "Cruzeiro"

jogo = buscar_jogo_especifico(campeonato, data, time_casa, time_fora)

if jogo:
    st.subheader(f"{time_casa} x {time_fora} - Pré-Live")
    
    # Seleção de mercados
    mercados = st.multiselect(
        "Selecione mercados",
        ["Over 2.5 Gols","Ambas Marcam","Resultado 1","Resultado X","Resultado 2",
         "Over 9.5 Escanteios","Over 2.5 Cartões"],
        default=["Over 2.5 Gols","Ambas Marcam","Resultado 1","Resultado X","Resultado 2",
                 "Over 9.5 Escanteios","Over 2.5 Cartões"]
    )

    tabela = []
    for mercado in mercados:
        if mercado.startswith("Resultado"):
            odd = 2.5
            prob = prob_pre_jogo(odd)
        elif mercado == "Over 2.5 Gols":
            odd = 1.8
            prob = prob_pre_jogo(odd)
        elif mercado == "Ambas Marcam":
            odd = 1.85
            prob = prob_pre_jogo(odd)
        elif mercado == "Over 9.5 Escanteios":
            odd = 1.9
            prob = prob_escanteios(time_casa, time_fora)
        elif mercado == "Over 2.5 Cartões":
            odd = 1.95
            prob = prob_cartoes(time_casa, time_fora)
        else:
            odd = 1.8
            prob = 0.5

        ev = calcular_ev(prob, odd)
        stake = kelly(prob, odd, banca)
        
        tabela.append([mercado, round(prob,2), odd, round(ev,2), stake])
        
        if ev >= 0.15:
            enviar(f"💰 TESTE PRÉ-LIVE\n{time_casa} x {time_fora}\nMercado: {mercado}\nProb: {round(prob,2)}\nOdd: {odd}\nEV: {round(ev,2)}\nStake: R${stake}")

    df = st.dataframe(tabela, columns=["Mercado","Prob","Odd","EV","Stake"])
else:
    st.warning("Jogo não encontrado ou ainda não disponível na API")
