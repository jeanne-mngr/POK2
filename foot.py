import requests
from bs4 import BeautifulSoup


def setSoup(url):
    with requests.Session() as session :
        try : 
            response = session.get(url)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print("Il y a eu un problème lors de l'accès au site")
            raise requests.exceptions.RequestException from e
        soup = BeautifulSoup(response.text, 'html.parser')
        return(soup)

def getAgePlayer(soup):
    age = soup.findAll('span', 'Text cGjIku')[1]
    return(f"L'age moyen au psg est de {age.text.strip()}")

url = "https://www.sofascore.com/fr/equipe/football/paris-saint-germain/1644"

print(getAgePlayer(setSoup(url)))