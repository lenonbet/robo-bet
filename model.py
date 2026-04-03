import math
import random

# ================= BASE DE FORÇA DOS TIMES =================
# (simulação inteligente baseada em nível dos times)
forca_times = {
    "Barcelona": 2.2,
    "Real Madrid": 2.3,
    "Atl Madrid": 1.9,
    "Sevilla": 1.6,
    "Rayo Vallecano": 1.4,
    "Elche": 1.1,

    "Flamengo": 2.0,
    "Palmeiras": 2.1,
    "São Paulo": 1.6,
    "Cruzeiro": 1.5
}

def get_forca(time):
    return forca_times.get(time, random.uniform(1.2,1.8))

# ================= POISSON =================
def poisson(lmbda, k):
    return (lmbda**k * math.exp(-lmbda)) / math.factorial(k)

def calcular_xg(casa, fora):
    ataque_casa = get_forca(casa)
    defesa_fora = get_forca(fora)

    ataque_fora = get_forca(fora)
    defesa_casa = get_forca(casa)

    xg_home = (ataque_casa * 1.1) / defesa_fora
    xg_away = (ataque_fora * 0.9) / defesa_casa

    return xg_home, xg_away

def prob_over(xg, linha):
    return 1 - sum(poisson(xg, i) for i in range(int(linha)))

def prob_btts(xg_home, xg_away):
    return (1 - poisson(xg_home, 0)) * (1 - poisson(xg_away, 0))

def calcular_ev(prob, odd):
    return (prob * odd) - 1
