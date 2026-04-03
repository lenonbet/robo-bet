import requests

# LIGAS QUE VOCÊ QUER (PRINCIPAIS)
LIGAS_DESEJADAS = [
    "Brazilian Serie A",
    "Brazilian Serie B",
    "Premier League",
    "Spanish La Liga",
    "Italian Serie A",
    "French Ligue 1",
    "Portuguese Primeira Liga",
    "German Bundesliga",
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

        # FILTRA SÓ AS LIGAS IMPORTANTES
        if liga not in LIGAS_DESEJADAS:
            continue

        if liga not in ligas:
            ligas[liga] = []

        ligas[liga].append({
            "nome": f"{j['strHomeTeam']} x {j['strAwayTeam']}",
            "casa": j['strHomeTeam'],
            "fora": j['strAwayTeam'],
            "hora": j.get("strTime", "")
        })

    return ligas
  
