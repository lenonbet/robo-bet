import random

def gerar_stats(xg_home, xg_away):

    total = xg_home + xg_away

    stats = {
        "finalizacoes": int(total * random.uniform(8,12)),
        "escanteios": int(total * random.uniform(3,5)),
        "cartoes": int(random.uniform(3,7)),
        "faltas": int(random.uniform(20,35)),
        "defesas_gk": int(random.uniform(2,8))
    }

    return stats
