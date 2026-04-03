import math
import random

def poisson(lmbda, k):
    return (lmbda**k * math.exp(-lmbda)) / math.factorial(k)

def calcular_xg():
    return random.uniform(1.0, 2.5), random.uniform(0.8, 2.2)

def prob_over(xg, linha):
    return 1 - sum(poisson(xg, i) for i in range(int(linha)))

def prob_btts(xg_home, xg_away):
    return (1 - poisson(xg_home, 0)) * (1 - poisson(xg_away, 0))

def prob_escanteios(stats):
    return min(0.85, stats["escanteios"] / 15)

def prob_cartoes(stats):
    return min(0.85, stats["cartoes"] / 8)

def odd_justa(prob):
    return round(1 / prob, 2) if prob > 0 else 0

def odd_mercado(prob):
    margem = random.uniform(0.90, 0.96)
    return round((1 / prob) * margem, 2)

def calcular_ev(prob, odd):
    return (prob * odd) - 1
