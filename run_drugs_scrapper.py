import requests 
import pandas as pd
import os
from bs4 import BeautifulSoup
import time
from tqdm import tqdm
import json


with open('./drugs/drugs_urls.json') as handle:
    d = json.loads(handle.read())
    
    
number_of_drugs = len(d.keys())
number_of_drugs


for idx in tqdm(range(number_of_drugs)):
    drug_id = list(d.keys())[idx]
    drug_link = d[list(d.keys())[idx]] 
    try:
        drug_scrapper = Drugs_Scrapper(drug_id, drug_link)
        drug_scrapper.get_drug_html()
        drug_scrapper.get_interaction_link()
        drug_scrapper.get_interaction_html()
        interactions_tags = drug_scrapper.get_interactions_tags()
        drug_scrapper.get_interactions()
        drug_scrapper.get_disease_interactions()
        drug_json = drug_scrapper.get_json('./drugs/data/')      
        r = requests.put('https://258jx22haf.execute-api.us-east-1.amazonaws.com/items', json = drug_json)
        with open("scrapped_list.txt", "a") as myfile:
            myfile.write(str(idx)+" - "+str(drug_id)+" - "+ str(drug_link)+" - "+str(r.json()) + "\n")
    except Exception as e:
        with open("failed_list.txt", "a") as myfile:
            myfile.write(str(idx)+ " - " + str(drug_id)+" - "+ str(drug_link)+  " - "+ str(e)+"\n")
    time.sleep(3)