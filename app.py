from pprint import pprint
from selenium import webdriver
from bs4 import BeautifulSoup as bs
from flask import Flask
import re, json, time


app = Flask(__name__)

@app.route('/')
def index():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    driver = webdriver.Chrome('chromedriver.exe', options = options)
    
    #shopee_url = "https://shopee.ph/%E2%9A%A1Flash-Sale%E2%9A%A1-Samsung-Galaxy-A72-Smartphone-Full-Screen-Cellphone-Sale-Original-i.668871889.16629358086?sp_atk=7191f3e8-b47f-41fe-9eb1-3be4f0f7526f&xptdk=7191f3e8-b47f-41fe-9eb1-3be4f0f7526f"
    shopee_url = "https://shopee.ph/POCO-X4-Pro-5G-8GB-256GB-Global-Version%E3%80%90In-1-year-Warranty%E3%80%91-i.178878361.11189292849?sp_atk=b944786d-688e-4687-b88b-967b61f00702&xptdk=b944786d-688e-4687-b88b-967b61f00702"
    
    #INITIALIZE WEB DRIVER AND BS4
    driver.get(shopee_url)
    driver.implicitly_wait(15)
    
    
    # Get scroll height.
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:

        # Scroll down to the bottom.
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Wait to load the page.
        time.sleep(2)

        # Calculate new scroll height and compare with last scroll height.
        new_height = driver.execute_script("return document.body.scrollHeight")

        if new_height == last_height:
            break
        last_height = new_height       
    
    
    response = driver.page_source
    driver.close()
    soup = bs(response, "html.parser")
    

    #GET PRODUCT NAME
    names = soup.find_all("div", {"class": "VCNVHn"})
    for name in names:
        name = name.select_one('span')
        product_name = name.get_text(strip=True)

    #GET PRODUCT RATING
    ratings = soup.find_all("div", {"class": "_3uBhVI URjL1D"})
    for rating in ratings:
        product_rating = rating.get_text(strip=True)
        
    #GET PRODUCT RATING COUNT
    ratings_count = soup.find_all("div", {"class": "_3uBhVI"})
    for rating_count in ratings_count:
        product_rating_count = rating_count.get_text(strip=True)
        
    #GET PRODUCT RATINGS BREAKDOWN
    ratings_breakdown = soup.find_all("div", {"class": "product-rating-overview__filter"})
    
    product_ratings_breakdown = []
    product_ratings_breakdown_dict = {}
    for rating_breakdown in ratings_breakdown:        
        product_rating_breakdown = rating_breakdown.get_text(strip=True)
        product_ratings_breakdown.append(product_rating_breakdown)
    
    product_ratings_breakdown.remove("all")   
    
    for product_rating_breakdown in product_ratings_breakdown:
        result = re.search('\(([^)]+)', product_rating_breakdown).group(1)    
        product_ratings_breakdown_dict[product_rating_breakdown[0]] = result
        
    product_ratings_breakdown_dict["with_comments"] = product_ratings_breakdown_dict["w"]
    del product_ratings_breakdown_dict["w"]      
    
    product_ratings_breakdown_dict["with_media"] = product_ratings_breakdown_dict["W"]
    del product_ratings_breakdown_dict["W"]      
    
      
    #GET PRODUCT SOLD COUNT
    solds_count = soup.find_all("div", {"class": "_3b2Btx"})
    for sold_count in solds_count:
        product_sold_count = sold_count.get_text(strip=True)        

    #GET PRODUCT PRICE
    prices = soup.find_all("div", {"class": "_2v0Hgx"})
    for price in prices:
        product_price = price.get_text(strip=True)

    #GET PRODUCT PHOTOS        
    photos_url = soup.find_all("div", {"class": "_2UWcUi _1vc1W7"})    
    product_images_list = []
    for photo_url in photos_url:
        photo_urls = re.findall('\("(http.*)"\)',photo_url['style'])
        for image_url in photo_urls:
            image_url = image_url.replace("_tn", "")
            product_images_list.append(image_url)

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
        value = value.get_text(strip=True)
        values_list.append(value)
        specification = specification.get_text(strip=True)
        specification = specification.lower()
        specification = specification.replace(" ", "_")
        specifications_list.append(specification)

    specification_dict = {}
    for specification in specifications_list:
        for value in values_list:
            if specification == "category":
                specification_dict[specification] = ' > '.join(categories)
                values_list.remove(value)
                break
            else:
                specification_dict[specification] = value
                values_list.remove(value)
                break
  
    #GET PRODUCT DESCRIPTION    
    descriptions = soup.find_all("p", {"class": "_2Y002L"})
    for description in descriptions:
        product_description = description.get_text(strip=True)
        product_description = product_description.replace("\n", " " ).replace("\r", " ")
        
    #GET PRODUCT STORE NAME
    stores = soup.find_all("div", {"class": "_1wVLAc"})
    for store in stores:
        product_store = store.get_text(strip=True) 
        
    #GET PRODUCT STORE INFORMATION
    store_infos = soup.find_all("span", {"class": "_33OqNH _2YMXyO"})
    product_store_info_list = []
    for store_info in store_infos:
        product_store_info = store_info.get_text(strip=True)
        product_store_info_list.append(product_store_info)
        
    stores_followers = soup.find_all("span", {"class": "_33OqNH"})
    for store_followers in stores_followers:
        store_followers_count = store_followers.get_text(strip=True)
        
       
    #CREATE JSON RESPONSE
    data_set = {"name": product_name, "product_images": product_images_list, "rating": product_rating, "rating_count": product_rating_count, "ratings_breakdown": product_ratings_breakdown_dict, "sold_count": product_sold_count, "price": product_price, "variations": variations_list, "shipping_from": shipping_from, "shipping_to": shipping_to , "product_description": product_description, "product_specifications": specification_dict, "store" : { "name": product_store, "store_rating": product_store_info_list[0], "number_of_products": product_store_info_list[1], "response_rate": product_store_info_list[2], "number_of_followers": store_followers_count }}
    json_dump = json.dumps(data_set)
    json_object = json.loads(json_dump)


    return json_object