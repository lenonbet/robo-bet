import requests

ligas_top = [
    "Brazilian Serie A",
    "English Premier League",
    "Spanish La Liga",
    "Italian Serie A",
    "French Ligue 1",
    "Portuguese Primeira Liga"
]

def buscar_jogos_por_data(data):
    url = f"https://www.thesportsdb.com/api/v1/json/3/eventsday.php?d={data}&s=Soccer"
    
    try:
        res = requests.get(url).json()
        eventos = res.get("events", [])
    except:
        eventos = []

    ligas = {}

    for j in eventos:
        liga = j.get("strLeague", "Outros")

        if liga not in ligas:
            ligas[liga] = []

        ligas[liga].append({
            "nome": f"{j['strHomeTeam']} x {j['strAwayTeam']}",
            "casa": j['strHomeTeam'],
            "fora": j['strAwayTeam']
        })

    # fallback completo
    fallback = {
        "Brazilian Serie A": [
            {"casa": "Flamengo", "fora": "Palmeiras"},
            {"casa": "São Paulo", "fora": "Cruzeiro"}
        ],
        "English Premier League": [
            {"casa": "Arsenal", "fora": "Chelsea"},
            {"casa": "Liverpool", "fora": "Man City"}
        ],
        "Spanish La Liga": [
            {"casa": "Rayo Vallecano", "fora": "Elche"}
        ],
        "Italian Serie A": [
            {"casa": "Juventus", "fora": "Milan"}
        ],
        "French Ligue 1": [
            {"casa": "PSG", "fora": "Lyon"}
        ]
    }

    for liga in ligas_top:
        if liga not in ligas:
            ligas[liga] = []
            for j in fallback.get(liga, []):
                ligas[liga].append({
                    "nome": f"{j['casa']} x {j['fora']}",
                    "casa": j['casa'],
                    "fora": j['fora']
                })

    return ligas
