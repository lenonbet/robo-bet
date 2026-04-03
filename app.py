mercados = [
    # GOLS
    ("Over 2.5 Gols", prob_over(xg_total, 3), 1.80),
    ("Under 2.5 Gols", 1 - prob_over(xg_total, 3), 2.00),

    # HT
    ("Over 1.5 HT", prob_over(xg_total*0.45, 2), 1.70),
    ("Under 1.5 HT", 1 - prob_over(xg_total*0.45, 2), 1.60),

    # BTTS
    ("Ambas Marcam", prob_btts(xg_home, xg_away), 1.85),

    # RESULTADO
    ("Casa vence", xg_home/(xg_total), 2.2),
    ("Empate", 0.25, 3.2),
    ("Fora vence", xg_away/(xg_total), 2.8),

    # DUPLA CHANCE
    ("Casa ou Empate", min(0.85, (xg_home/(xg_total))+0.25), 1.40),
    ("Fora ou Empate", min(0.85, (xg_away/(xg_total))+0.25), 1.50),

    # ESCANTEIOS
    ("Escanteios Over 9.5", min(0.85, 0.5 + xg_total/5), 1.9),

    # CARTÕES
    ("Cartões Over 3.5", min(0.80, 0.5 + xg_total/6), 1.95),

    # GOLEIRO
    ("Goleiro +3 defesas", min(0.75, 0.4 + xg_total/5), 1.80),

    # JOGADOR (SIMULADO)
    ("Jogador +2 faltas cometidas", min(0.70, 0.4 + xg_total/6), 1.90),
    ("Jogador +3 desarmes", min(0.75, 0.45 + xg_total/6), 1.85),
    ("Jogador levar cartão", min(0.65, 0.35 + xg_total/7), 2.10),

    # PLACAR
    ("Placar 1x1", poisson(xg_home,1)*poisson(xg_away,1), 6.0),
    ("Placar 2x1", poisson(xg_home,2)*poisson(xg_away,1), 8.0),
    ("Placar 2x0", poisson(xg_home,2)*poisson(xg_away,0), 7.0),
]
