import requests

API_KEY = "715022b452a043a2977b885ce60e6da7"

def buscar_jogos():
    url = "https://api.football-data.org/v4/matches"

    headers = {
        "X-Auth-Token": API_KEY
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
