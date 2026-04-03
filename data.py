import requests

def buscar_jogos():

    url = "https://api.football-data.org/v4/matches"
    
    headers = {
        "X-Auth-Token": "SUA_API_GRATUITA_AQUI"
    }

    try:
        res = requests.get(url, headers=headers).json()
        jogos_api = res.get("matches", [])
    except:
        jogos_api = []

    ligas = {}

    for j in jogos_api:
        try:
            liga = j["competition"]["name"]

            casa = j["homeTeam"]["name"]
            fora = j["awayTeam"]["name"]

            if liga not in ligas:
                ligas[liga] = []

            ligas[liga].append({
                "nome": f"{casa} x {fora}",
                "casa": casa,
                "fora": fora,
                "status": j["status"]
            })

        except:
            continue

    return ligas
