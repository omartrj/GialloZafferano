import base64
import json
import os
import re
from string import digits

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

from ModelRecipe import ModelRecipe

debug = False
folderRecipes = "recipes"


def saveRecipe(linkRecipeToDownload):
    soup = downloadPage(linkRecipeToDownload)
    title = findTitle(soup)

    filePath = calculateFilePath(title)
    if os.path.exists(filePath):
        return

    rating = findRating(soup)
    difficulty = findDifficulty(soup)
    tags = findTags(soup)
    ingredients = findIngredients(soup)
    category = findCategory(soup)
    imageBase64 = findImage(soup)

    modelRecipe = ModelRecipe()
    modelRecipe.title = title
    modelRecipe.link = linkRecipeToDownload
    modelRecipe.category = category
    modelRecipe.difficulty = difficulty
    modelRecipe.rating = rating
    modelRecipe.tags = tags
    modelRecipe.ingredients = ingredients
    modelRecipe.imageBase64 = imageBase64

    createFileJson(modelRecipe.toDictionary(), filePath)


def findTitle(soup):
    titleRecipe = ""
    for title in soup.find_all(attrs={"class": "gz-title-recipe gz-mBottom2x"}):
        titleRecipe = title.text
    return titleRecipe

def findRating(soup):
    ratingRecipe = ""
    for rating in soup.find_all(attrs={"class": "gz-rating-panel rating_panel"}):
        ratingRecipe = rating.get("data-content-rate")
    return ratingRecipe

def findDifficulty(soup):
    difficultyRecipe = ""
    div = soup.find("div", attrs={"class": "gz-list-featured-data"})
    ul = div.find("ul")
    li = ul.find_all("li")[0]
    span = li.find_all("span")[1]
    difficultyRecipe = span.text.replace("Difficoltà: ", "")
    return difficultyRecipe

def findTags(soup):
    allTags = []
    for tag in soup.find_all(attrs={"class": "gz-name-featured-data-other"}):
        allTags.append(tag.text)
    return allTags

def findIngredients(soup):
    allIngredients = []
    for tag in soup.find_all(attrs={"class": "gz-ingredient"}):
        nameIngredient = tag.a.string
        contents = tag.span.contents[0]
        quantityProduct = re.sub(r"\s+", " ", contents).strip()
        
        ingredient_dict = {
            "name": nameIngredient,
            "isOptional": isIngredientOptional(quantityProduct),
        }
        allIngredients.append(ingredient_dict)
    return allIngredients

def isIngredientOptional(quantityProduct):
    # List of words to flag as optional
    optionalWords = ["facoltativ", "q.b", "ramett", "fogliolin", "pizzic", "filo", "cucchiaino"]
    for word in optionalWords:
        if word in quantityProduct:
            return True
    return False


def findCategory(soup):
    for tag in soup.find_all(attrs={"class": "gz-breadcrumb"}):
        if tag.li is not None:
            if tag.li.a is not None:
                category = tag.li.a.string
                return category
    return ""



def findImage(soup):

    # Find the first picture tag
    pictures = soup.find("picture", attrs={"class": "gz-featured-image"})

    # Fallback: find a div with class `gz-featured-image-video gz-type-photo`
    if pictures is None:
        pictures = soup.find(
            "div", attrs={"class": "gz-featured-image-video gz-type-photo"}
        )

    imageSource = pictures.find("img")

    # Most of the times the url is in the `data-src` attribute
    imageURL = imageSource.get("data-src")

    # Fallback: if not found in `data-src` look for the `src` attr
    # Most likely, recipes which have the `src` attr
    # instead of the `data-src` one
    # are the older ones.
    # As a matter of fact, those are the ones enclosed
    # in <div> tags instead of <picture> tags (supported only on html5 and onward)
    if imageURL is None:
        imageURL = imageSource.get("src")

    imageToBase64 = str(base64.b64encode(requests.get(imageURL).content))
    imageToBase64 = imageToBase64[2 : len(imageToBase64) - 1]
    return imageToBase64


def calculateFilePath(title):
    compact_name = title.replace(" ", "_").lower()
    return folderRecipes + "/" + compact_name + ".json"


def createFileJson(data, path):
    with open(path, "w", encoding='utf-8') as file:
        file.write(json.dumps(data, ensure_ascii=False))


def downloadPage(linkToDownload):
    response = requests.get(linkToDownload)
    soup = BeautifulSoup(response.text, "html.parser")
    return soup


def downloadAllRecipesFromGialloZafferano():
    totalPages = countTotalPages() + 1
    # for pageNumber in range(1,totalPages):
    for pageNumber in tqdm(range(1, totalPages), desc="pages…", ascii=False, ncols=75):
        linkList = "https://www.giallozafferano.it/ricette-cat/page" + str(pageNumber)
        response = requests.get(linkList)
        soup = BeautifulSoup(response.text, "html.parser")
        for tag in soup.find_all(attrs={"class": "gz-title"}):
            link = tag.a.get("href")
            saveRecipe(link)
            if debug:
                break

        if debug:
            break


def countTotalPages():
    numberOfPages = 0
    linkList = "https://www.giallozafferano.it/ricette-cat"
    response = requests.get(linkList)
    soup = BeautifulSoup(response.text, "html.parser")
    for tag in soup.find_all(attrs={"class": "disabled total-pages"}):
        numberOfPages = int(tag.text)
    return numberOfPages


if __name__ == "__main__":
    if not os.path.exists(folderRecipes):
        os.makedirs(folderRecipes)
    downloadAllRecipesFromGialloZafferano()
