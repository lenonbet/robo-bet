import streamlit as st
import requests
import pandas as pd
import datetime
import time
import json
from pathlib import Path

# ================= CONFIGURAÇÃO =================
API_KEY_FOOT = "f465d2868695fccca02d7204db0eaba"
TOKEN = "8794081951:AAHriFzY5yj68sacN_JD4iuoZ4h8H3Su6TY"
CHAT_ID = "6661035382"

alertas = set()
HISTORICO_FILE = Path("historico_apostas.json")
if not HISTORICO_FILE.exists():
    HISTORICO_FILE.write_text(json.dumps([]))

# ================= TELEGRAM =================
def enviar(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    try:
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg})
    except:
        pass

# ================= FUNÇÕES =================
def calcular_ev(prob, odd):
    return (prob * odd) - 1

def kelly(prob, odd, banca):
    b = odd - 1
    q = 1 - prob
    stake = (b * prob - q) / b
    return max(0, round(stake * banca, 2))

def prob_pre_jogo(odd):
    return 1 / odd

def prob_ao_vivo(total, tempo):
    ritmo = total / max(tempo, 1)
    base = 0.50
    ajuste = ritmo * 2.5
    prob = base + ajuste
    return min(max(prob, 0.05), 0.92)

# ================= HISTÓRICO =================
def salvar_historico(entry):
    historico = json.loads(HISTORICO_FILE.read_text())
    historico.append(entry)
    HISTORICO_FILE.write_text(json.dumps(historico, indent=2))

def carregar_historico():
    return pd.DataFrame(json.loads(HISTORICO_FILE.read_text()))

# ================= BUSCAR JOGOS =================
def buscar_jogos_football(live=False):
    hoje_utc = datetime.datetime.utcnow().strftime("%Y-%m-%d")
    url = f"https://v3.football.api-sports.io/fixtures?date={hoje_utc}" if not live else "https://v3.football.api-sports.io/fixtures?live=all"
    headers = {"x-apisports-key": API_KEY_FOOT}
    try:
        return requests.get(url, headers=headers, timeout=10).json().get("response", [])
    except:
        return []

# ================= FILTRO =================
PRINCIPAIS_FOOT = ["English Premier League","La Liga","Serie A","Bundesliga","Ligue 1","Champions League"]
def filtrar_jogos(jogos, campeonatos):
    return [j for j in jogos if j.get("league", {}).get("name") in campeonatos]

# ================= MERCADOS =================
def gerar_mercados(jogo, banca, ao_vivo=False):
    mercados = []
    casa = jogo.get('teams', {}).get('home', {}).get('name','Desconhecido')
    fora = jogo.get('teams', {}).get('away', {}).get('name','Desconhecido')
    tempo = jogo.get('fixture', {}).get('status', {}).get('elapsed') or 0
    g1 = jogo.get('goals', {}).get('home') or 0
    g2 = jogo.get('goals', {}).get('away') or 0
    total = g1 + g2

    # Over 2.5
    odd = jogo.get('odds', {}).get('over25', round(1.8,2))  # se não existir, usar valor simulado
    prob = prob_ao_vivo(total, tempo) if ao_vivo else prob_pre_jogo(odd)
    ev = calcular_ev(prob, odd)
    stake = kelly(prob, odd, banca)
    mercados.append({"Mercado":"Over 2.5","Odd":odd,"Prob":prob,"EV":ev,"Stake":stake})

    # Ambas marcam
    odd = jogo.get('odds', {}).get('both_score', round(1.85,2))
    prob = prob_ao_vivo(total, tempo) if ao_vivo else prob_pre_jogo(odd)
    ev = calcular_ev(prob, odd)
    stake = kelly(prob, odd, banca)
    mercados.append({"Mercado":"Ambas Marcam","Odd":odd,"Prob":prob,"EV":ev,"Stake":stake})

    # Resultado 1X2
    for resultado in ["1","X","2"]:
        odd = jogo.get('odds', {}).get(f'result_{resultado}', round(2.5,2))
        prob = prob_pre_jogo(odd)
        ev = calcular_ev(prob, odd)
        stake = kelly(prob, odd, banca)
        mercados.append({"Mercado":f"Resultado {resultado}","Odd":odd,"Prob":prob,"EV":ev,"Stake":stake})

    return mercados, casa, fora, tempo

# ================= STREAMLIT =================
st.title("💰 ROBÔ PROFISSIONAL - FUTEBOL AO VIVO & PRÉ-JOGO")

banca = st.number_input("💰 Sua banca", value=1000)
modo = st.selectbox("Modo de Análise", ["PRÉ-JOGO","AO VIVO","TODOS"])
manual = st.checkbox("Selecionar jogos manualmente")

status = st.empty()

while True:
    status.warning("🔄 Analisando jogos...")

    jogos = []
    if modo in ["PRÉ-JOGO","TODOS"]:
        jogos += filtrar_jogos(buscar_jogos_football(live=False), PRINCIPAIS_FOOT)
    if modo in ["AO VIVO","TODOS"]:
        jogos += filtrar_jogos(buscar_jogos_football(live=True), PRINCIPAIS_FOOT)

    # ================= SELEÇÃO MANUAL =================
    if manual and jogos:
        opcoes = [f"{j['teams']['home']['name']} x {j['teams']['away']['name']}" for j in jogos]
        selecionados = st.multiselect("Escolha os jogos que quer analisar", opcoes)
        jogos = [j for j in jogos if f"{j['teams']['home']['name']} x {j['teams']['away']['name']}" in selecionados]

    tabela = []
    for j in jogos:
        mercados, casa, fora, tempo = gerar_mercados(j, banca, ao_vivo=(modo=="AO VIVO"))
        row = [casa, fora, tempo]
        for m in mercados:
            row += [m["Mercado"], m["Odd"], round(m["Prob"],2), round(m["EV"],2), m["Stake"]]

            key_alerta = f"{casa}-{fora}-{m['Mercado']}"
            if key_alerta not in alertas and m["EV"]>=0.15:
                enviar(f"💰 VALUE BET\n{casa} x {fora}\nMercado: {m['Mercado']}\nProb: {round(m['Prob'],2)}\nOdd: {m['Odd']}\nEV: {round(m['EV'],2)}\nStake: R${m['Stake']}")
                alertas.add(key_alerta)
                salvar_historico({"Data":str(datetime.datetime.now()),"Casa":casa,"Fora":fora,"Mercado":m['Mercado'],"EV":m['EV']})

        tabela.append(row)

    if tabela:
        col_names = ["Casa","Fora","Min"]
        for i in range(3):  # 3 mercados
            col_names += [f"Mercado{i+1}","Odd{i+1}","Prob{i+1}","EV{i+1}","Stake{i+1}"]
        df = pd.DataFrame(tabela, columns=col_names)
        st.dataframe(df)
    else:
        st.info("Nenhuma entrada forte agora")

    st.subheader("📜 Histórico de apostas")
    st.dataframe(carregar_historico())

    time.sleep(180)
