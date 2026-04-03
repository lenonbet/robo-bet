import math
import random

# ================= FORÇA DOS TIMES =================
forca_times = {
    "Flamengo": 2.1,
    "Palmeiras": 2.2,
    "São Paulo": 1.7,
    "Santos": 1.6,
    "Barcelona": 2.3,
    "Real Madrid": 2.4,
    "Rayo Vallecano": 1.5,
    "Elche": 1.2
}

def get_forca(time):
    return forca_times.get(time, random.uniform(1.3,1.9))

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

# ================= PROB =================
def prob_over(xg, linha):
    return 1 - sum(poisson(xg, i) for i in range(int(linha)))

def prob_btts(xg_home, xg_away):
    return (1 - poisson(xg_home, 0)) * (1 - poisson(xg_away, 0))

# ================= ODDS JUSTAS =================
def odd_justa(prob):
    if prob <= 0:
        return 0
    return round(1 / prob, 2)

# simula odd da casa (tipo bet365)
def odd_mercado(prob):
    margem = random.uniform(0.90, 0.95)  # margem da casa
    return round((1 / prob) * margem, 2)

# ================= EV =================
def calcular_ev(prob, odd):
    return (prob * odd) - 1
