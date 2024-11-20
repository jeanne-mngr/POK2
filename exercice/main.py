from math import ceil
import re

import requests
from bs4 import BeautifulSoup


#Todo : récupérer toutes les catégories du site (sur le coté à gauche)
# FAire exo min 55s

def setSoup(url, session):
    # with requests.Session() as session :
    try : 
        response = session.get(url)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print("Il y a eu un problème lors de l'accès au site")
        raise requests.exceptions.RequestException from e
    soup = BeautifulSoup(response.text, 'html.parser')
    return(soup)

def getAllCategories():
    soup = setSoup("https://books.toscrape.com")

    aside = soup.find('aside')

    links = aside.find('ul', class_='nav-list').find('ul').findAll('a')

    cat = [child.text.strip() for child in links if child.name]

    return cat

def getAllBooksTitle():
    soup = setSoup("https://books.toscrape.com")
    section = soup.find('section')
    list = section.findAll('h3')
    titleList = [child.a.get('title') for child in list]
    return (titleList)


def searchCatWithlimitNumberOfBook(numberMax: int = 5):
    cat= getAllCategories()
    catLessThanMax = []
    i=2
    for category in cat : 
        soup = setSoup("https://books.toscrape.com/catalogue/category/books/"+category.replace(' ', '-').lower()+'_'+str(i)+"/index.html")
        numberOfBook = int(soup.find('form', class_='form-horizontal').find('strong').text.strip())
        #Alternative 
        # numberOfBook = int(soup.select_one('form.form-horizontal strong').text.strip())
        if numberOfBook <= numberMax :
            catLessThanMax.append(category)
            print(f"Cette catégorie n'a pas assez de livre ( {category} a {numberOfBook} livre(s))")
        i += 1


def findOneStarBook(): #Should return book's name AND id (de 0 à 1000) qui est dans le lien du livre 
    #Faire lien['href'] pour avoir le lien
    soup = setSoup("https://books.toscrape.com")
    section = soup.find('section')
    articleList = section.select('article')
    oneStarBook = []
    for article in articleList:
        if article.find('p', class_="star-rating One"):
            title = article.find('h3').a['title']
            if article.find('h3').a['href']:
                link = article.find('h3').a['href']
                id = link.split('_')[1].split('/')[0]
            else: id = "L'identifiant n'a pas été renseigné" #On aurait pu faire un try...exept ... avec un raise
            oneStarBook.append((title, id))
        elif article.find('p', class_="star-rating") == None:
            title = article.find('h3').a['title']
            print(f"Le livre {title} n'a pas de note renseignée")
    return oneStarBook


def bookValue(url, session):
    soup = setSoup(url, session)
    try :
        stock = soup.find('p', class_='instock availability')
    except AttributeError as e:
        print('Impossible de trouver la balise <p>')
        raise requests.exceptions.RequestException from e
    numberInStock = int(re.findall(r'\d+', stock.text)[0])
    price = float(soup.find('p', class_='price_color').text[2:])
    return numberInStock*price

def getAllUrlBook(url, session):
    soup = setSoup(url, session)
    try :
        h3List = soup.find('section').find_all('h3')
    except AttributeError as e:
        print('Impossible de trouver les balises <section> ou <h3>')
        raise requests.exceptions.RequestException from e
    urlList = []
    for h3 in h3List:
        try :
            urlBook = h3.a['href']
        except KeyError as e:
            print("Impossible de trouver l'élément href")
            raise requests.exceptions.RequestException from e
        if urlBook[:10] == 'catalogue/' :
            urlBook = urlBook[10:]
        urlList.append(urlBook)
    return(urlList)

def onePageValue(url, session):
    urlList = getAllUrlBook(url, session)
    pageValue = 0
    for urlInList in urlList:
        pageValue += bookValue("https://books.toscrape.com" + "/catalogue/" + urlInList, session)
    return pageValue

def getNumberOfPages(session):
    url = "https://books.toscrape.com"
    soup = setSoup(url, session)
    try :
        form = soup.find('form', 'form-horizontal')
        numberOfPage = int(re.findall(r'\d+',form.text.strip().split('to')[0])[0]) / int(re.findall(r'\d+',form.text.strip().split('to')[-1])[0])
    except AttributeError as e:
        print('Impossible de trouver le nombre de pages')
        raise requests.exceptions.RequestException from e 
    return ceil(numberOfPage)

def libraryValue():
    with requests.Session() as session:
        numberOfPage = getNumberOfPages(session)
        value = 0
        url = "https://books.toscrape.com"
        for i in range(1, numberOfPage + 1):
            print(i)
            url = "https://books.toscrape.com/catalogue/page-"+str(i)+".html"
            value += onePageValue(url, session)
    return(value)


print(libraryValue())
