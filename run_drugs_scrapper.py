import requests 
import pandas as pd
import os
from bs4 import BeautifulSoup
import time
from tqdm import tqdm
import json
from lxml import etree

from drugs_scrapper import Drugs_Scrapper

with open('./drugs/drugs_urls.json') as handle:
    d = json.loads(handle.read())
    
    
first_batch = ids

def scrap(drug_id):
    drug_id = drug_id
    drug_link = d[drug_id] 
    try:
        drug_scrapper = Drugs_Scrapper(drug_id, drug_link)
        drug_scrapper.get_drug_html()
        drug_scrapper.get_interaction_link()
        drug_scrapper.get_interaction_html()
        interactions_tags = drug_scrapper.get_interactions_tags()
        drug_scrapper.get_interactions()
        drug_scrapper.get_disease_interactions()
        drug_jsons = drug_scrapper.get_json('./drugs/data/')
        r = None
        for drug_json in drug_jsons:
            r = requests.put('https://258jx22haf.execute-api.us-east-1.amazonaws.com/items', json = drug_json)
        
           
        for brand in drug_scrapper.brand_name:
            with open("first_batch_map.txt", "a") as myfile:
                 myfile.write(str(brand)+","+ str(drug_id)+ "\n")
                    
            with open("first_batch_scrapped_list.txt", "a") as myfile:
                myfile.write(str(brand)+"- "+str(drug_id)+" - "+ str(drug_link)+" - "+str(r.json()) + "\n")
                    
                    
    except Exception  as e:
        with open("first_batch_failed_list.txt", "a") as myfile:
            myfile.write(str(drug_id)+" - "+ str(drug_link)+  " - "+ str(e)+"\n")

        
            
for drug_id in tqdm(range(1,1000)):
     drug_id = list(d.keys())[idx]
     if drug_id in done:
        continue

     scrap(drug_id)
     time.sleep(30)
        
        
        
        
        
        
        
        