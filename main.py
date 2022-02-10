import argparse
import requests
import os
import re
import json
import math
import time
from constants import *
from bs4 import BeautifulSoup
from random_user_agent.user_agent import UserAgent
from random_user_agent.params import SoftwareName, OperatingSystem
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import FirefoxOptions

opts = FirefoxOptions()
opts.add_argument("--headless")
opts.add_argument("window-size=3440,1440")
driver = webdriver.Firefox(options=opts)
collections_url = "https://opensea.io/explore-collections" # trending tab
top_collections_url = "https://opensea.io/explore-collections?tab=top"
art_collections_url = "https://opensea.io/explore-collections?tab=art"
collection_url = "https://opensea.io/collection/"
asset_base_url = "https://opensea.io"

def parse_to_int(s):
    if s[-1] == "K":
        return int(float(s[:-1]) * 1000)
    else:
        return int(s)

def download_specific_collections(collections, nr_to_download):
    if not os.path.exists("./images"):
        os.mkdir('./images')
    for collection in collections:
        print("Now downloading:", collection,"; NFTs in this collection: ",end="")

        # Creating folders for each collection
        if not os.path.exists("./images/"+collection):
            os.mkdir("./images/"+collection)
        current_url = collection_url + collection

        # Finding how many NFTs are in the current collection
        driver.get(current_url)
        data = driver.page_source
        new_soup = BeautifulSoup(data, 'html.parser')

        # Find the part where the number of items is stored
        nr_items = str(new_soup.find_all("div", class_="Overflowreact__OverflowContainer-sc-7qr9y8-0 jPSCbX")[0])

        # Find and parse the exact number to an integer
        start = nr_items.find("tabindex=\"-1\">") + 14
        nr_items = nr_items[start:]
        end = nr_items.find("</div>")
        nr_items = nr_items[:end]
        nr_items = parse_to_int(nr_items)
        print(nr_items)
        if nr_to_download == -1:
            nr_to_download = nr_items
        time.sleep(1)
        
        nr_identified_fungible_tokens = 0
        fungible_token_paths = set()
        while nr_identified_fungible_tokens < nr_to_download:
            new_soup = BeautifulSoup(data, 'html.parser')
            elements = new_soup.find_all("a", class_="styles__StyledLink-sc-l6elh8-0 ekTmzq Asset--anchor")
            for elem in elements:
                start = str(elem).find("href=\"") + 6
                end = str(elem).find("\">")
                fungible_token_path = str(elem)[start:end]
                fungible_token_paths.add(fungible_token_path)
            nr_identified_fungible_tokens = len(fungible_token_paths)
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(SCROLL_PAUSE_TIME)
            data += driver.page_source
        fungible_token_paths = list(fungible_token_paths)
        idx = 0
        for path in fungible_token_paths:
            driver.get(asset_base_url + path)
            data = driver.page_source
            good_soup = BeautifulSoup(data, 'html.parser')
            img_element = str(good_soup.find("img", class_="Image--image"))
            start = img_element.find("src=\"") + 5
            end = img_element.find("=w600")
            fungible_token_url = img_element[start:end] + "=s0"
            fungible_token = requests.get(fungible_token_url, verify=False, timeout=5)
            with open("./images/"+collection+"/" + str(idx) + ".png", "wb") as out_file:
                out_file.write(fungible_token.content)
            time.sleep(DOWNLOAD_PAUSE_TIME)
            idx += 1

def main():

    config = json.load(open("config.json"))
    selected_url = ""
    if config[DOWNLOAD] == "trending":
        selected_url = collections_url
    elif config[DOWNLOAD] == "top":
        selected_url = top_collections_url
    elif config[DOWNLOAD] == "art":
        selected_url = art_collections_url
    elif config[DOWNLOAD] == "collections":
        selected_url = collection_url
    else:
        print("Please specify in the config file from which tab to steal NFTs.")
        exit()

    if config[DOWNLOAD] == "collections":
        download_specific_collections(config[COLLECTIONS], config[PER_COLLECTION])
    else :
        # Getting collections on the selected page (trending, top or art)
        n_identified_collections = 0
        identified_collections_set = set()
        identified_collections = []
        driver.get(selected_url)
        data = driver.page_source
        last_height = driver.execute_script("return document.body.scrollHeight")
        while n_identified_collections < config[N_TO_DOWNLOAD]:
            soup = BeautifulSoup(data, 'html.parser')
            available_collections = soup.find_all("a", class_="styles__StyledLink-sc-l6elh8-0 ekTmzq CarouselCard--main CollectionCardreact__Card-sc-1b2ne4j-0 eKLGyb")
            for coll in available_collections:
                collection = str(str(coll))
                start = collection.find("/collection")
                end = collection.find("\"><div class=\"")
                if start != None:
                    if collection[(start + 12):end] not in identified_collections_set:
                        identified_collections.append(collection[(start + 12):end])
                        identified_collections_set.add(collection[(start + 12):end])
            n_identified_collections = len(identified_collections_set)
            if n_identified_collections < config[N_TO_DOWNLOAD]:
                # driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(SCROLL_PAUSE_TIME)
                data += driver.page_source
                new_height = driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height
        print(n_identified_collections)
        print(identified_collections)
        if config[DEBUG]:
            with open("collections.html", "w") as out_file:
                out_file.write(data)
    
if __name__ == "__main__":
    main()