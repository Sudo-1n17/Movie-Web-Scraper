import json
import logging
import time
import requests
from bs4 import BeautifulSoup
from termcolor import colored
from art import *

def ascci_art():
    tprint("1n17", font="tarty7")
    print(colored("GITHUB : https://github.com/Sudo-1n17\n", color='white', on_color="on_grey"))
    time.sleep(2)
ascci_art()

# - basic config logging 
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [%(levelname)s] - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

def send_requests(url):
    """sending requests and get html source"""

    logging.info("sending requests to website")
    resposne = requests.get(url)
    
    #Handling status error
    if resposne.status_code != 200:
        logging.error("error to send request")
        return None
    else:
        logging.info("successful sending requests")
    
    # return html source
    logging.info("saved html source")
    return resposne.text

def scrap_website(url, film_name):
    """parsing html and find film"""
    soup = BeautifulSoup(send_requests(url=url), "html.parser")
    logging.info("parsing html for bs4")

    logging.info("creat data for post")
    data = {
        "search_name" : film_name
    }

    logging.info("posting data to website")
    response = requests.post(url, data=data)
    
    logging.info("find and fetch all data")
    soup_2 = BeautifulSoup(response.text, "html.parser")
    main_div = soup_2.find("div", class_="uas_search_modal__results__items")
    
    if main_div:
        logging.info("find main div, searching film name ...")
        script_nonce_tag = soup.find("script", id="uas-public-script-js-extra")
        if script_nonce_tag:
            js_content = script_nonce_tag.string.strip()
    
            json_start = js_content.find("{")
            json_end = js_content.rfind("}") + 1
            json_str = js_content[json_start:json_end]

            data = json.loads(json_str)
            nonce = data["nonce"]
            
            if nonce:
                ajax_url = url + "wp-admin/admin-ajax.php"
                data = {
                    "action": "uas_search",
                    "nonce": nonce,
                    "query": film_name
                }

                headers = {
                    "User-Agent": "Mozilla/5.0",
                    "X-Requested-With": "XMLHttpRequest",
                    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                    "Origin": url
                }
                

                logging.info("sending POST request with nonce to admin-ajax.php")
                response_ajax = requests.post(ajax_url, data=data, headers=headers)

                if response_ajax.status_code == 200:
                    logging.info("POST successful")
                    if response_ajax.json():
                        logging.info("parsing JSON response")
                        result_json = response_ajax.json()
                        html_ajax_results = result_json["data"]["results"]
                        soup_result = BeautifulSoup(html_ajax_results, "html.parser")
                        logging.info("find all tag <a> in ajax result")
                        links = soup_result.find_all("a", class_="uas_search_modal__results__items__element")

                        if links:
                            for link in links:
                                href = link.get("href")
                                title = link.get("title")
                                print(colored(f"Title -> {title}", 'yellow'))
                                print(colored(f"Download-Link -> {href}\n", 'blue'))
                        else:
                            logging.error("Not Found film")
                    else:
                        logging.error("error to get response from ajax try again later ...")
                        exit()
                else:
                    logging.error(f"POST request failed: {response.status_code}")


# start script
if __name__ == "__main__":
    url = "https://www.uptvs.com/"
    film_name = input("enter your film name: ")
    scrap_website(url=url, film_name=film_name)
