from pprint import pprint
from selenium import webdriver
from bs4 import BeautifulSoup as bs
from flask import Flask, render_template, request
import requests, json


app = Flask(__name__)

@app.route('/')
def index():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    driver = webdriver.Chrome('chromedriver.exe', options = options)
    #shopee_url = "https://shopee.ph/realme-C11-2021-(2-32GB)-i.119485441.6986779215?sp_atk=eb8af231-8741-49aa-b427-bdf747bb9158"
    shopee_url = "https://shopee.ph/%E2%9A%A1Flash-Sale%E2%9A%A1-Samsung-Galaxy-A72-Smartphone-Full-Screen-Cellphone-Sale-Original-i.668871889.16629358086?sp_atk=7191f3e8-b47f-41fe-9eb1-3be4f0f7526f&xptdk=7191f3e8-b47f-41fe-9eb1-3be4f0f7526f"
    
    
    driver.get(shopee_url)
    driver.implicitly_wait(15)
    response = driver.page_source
    driver.close()
    soup = bs(response, "html.parser")
    

    #GET PRODUCT NAME
    names = soup.find_all("div", {"class": "_3g8My-"})
    for name in names:
        name = name.select_one('span')
        product_name = name.get_text(strip=True)

    #GET PRODUCT RATING
    ratings = soup.find_all("div", {"class": "_3uBhVI URjL1D"})
    for rating in ratings:
        product_rating = rating.get_text(strip=True)

    #GET PRODUCT PRICE
    prices = soup.find_all("div", {"class": "_2v0Hgx"})
    for price in prices:
        product_price = price.get_text(strip=True)

    #GET PRODUCT VARIATIONS
    variations = soup.find_all("button", {"class": "product-variation"})
    variations_list = []
    for variation in variations:
        variation = variation.get_text(strip=True)
        variations_list.append(variation)

    #GET PRODUCT SHIPPING FROM
    shipping_froms = soup.find_all("div", {"class": "_2wbMJu"})
    for shipping_from in shipping_froms:
        shipping_from = shipping_from.get_text(strip=True)

    if len(shipping_froms) == 0:
        shipping_from = ""

    #GET PRODUCT SHIPPING TO
    shipping_tos = soup.find_all("span", {"class": "_1uIhvN"})
    for shipping_to in shipping_tos:
        shipping_to = shipping_to.get_text(strip=True)

    if len(shipping_tos) == 0:
        shipping_to = ""

    #GET PRODUCT SPECIFICATIONS
    specifications_list = []
    values_list = []
    
    specifications = soup.find_all("label", {"class": "_1A0RCW"})
    for specification in specifications:
        if specification.get_text(strip=True) == "Category":
            categories_list = []
            categories = []
            categories_list =soup.find_all("a", {"class": "_2572CL ni2r2i"})
            for category in categories_list:
                category = category.get_text(strip=True)
                categories.append(category)


        value = specification.find_next_sibling('div')
        if not value:
            value = specification.find_next_sibling('a')
        print(value)
        value = value.get_text(strip=True)
        values_list.append(value)
        specification = specification.get_text(strip=True)
        specifications_list.append(specification)

    specification_dict = {}
    for specification in specifications_list:
        for value in values_list:
            if specification == "Category":
                specification_dict[specification] = ' > '.join(categories)
                values_list.remove(value)
                break
            else:
                specification_dict[specification] = value
                values_list.remove(value)
                break
    
    data_set = {"name": product_name, "rating": product_rating, "price": product_price, "variations": variations_list, "shipping_from": shipping_from, "shipping_to": shipping_to , "product_specifications": specification_dict}
    json_dump = json.dumps(data_set)
    json_object = json.loads(json_dump)


    return json_object




