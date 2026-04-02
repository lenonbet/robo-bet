import streamlit as st
import pandas as pd
import numpy as np

def calcular_ev(prob, odd):
    return (prob * odd) - 1

def modelo_ml(features):
    pesos = np.array([0.4, 0.3, 0.2, 0.1])
    return min(np.dot(features, pesos), 0.9)

def analisar():
    dados = []
    jogos = [("Time A","Time B"),("Time C","Time D")]
    for casa, fora in jogos:
        prob = 0.65
        odd = 1.95
        ev = calcular_ev(prob, odd)
        if ev > 0.1:
            dados.append({"Jogo":f"{casa} x {fora}","Prob":prob,"Odd":odd,"EV":round(ev,2)})
    return dados

def stake(banca, ev):
    return round(banca * (0.02 + ev), 2)

st.title("🚀 Robô de Apostas")

banca = st.number_input("Banca", value=1000)

if st.button("Analisar"):
    resultados = analisar()
    if resultados:
        df = pd.DataFrame(resultados)
        df['Stake'] = df['EV'].apply(lambda x: stake(banca, x))
        st.dataframe(df)
    else:
        st.write("Sem entradas")
