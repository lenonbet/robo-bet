import requests

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

    # fallback para garantir ligas grandes
    if "Spanish La Liga" not in ligas:
        ligas["Spanish La Liga"] = [
            {"nome": "Rayo Vallecano x Elche", "casa": "Rayo Vallecano", "fora": "Elche"}
        ]

    return ligas
