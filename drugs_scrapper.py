import requests 
import pandas as pd
import os
from bs4 import BeautifulSoup
import time
from tqdm import tqdm
import json
from lxml import etree


class Drugs_Scrapper:
    def __init__(self, drug_id, drug_link):
        self.drug_link = drug_link
        self.base_url =  "https://www.drugs.com/"
        self.interaction_class_to_level_dict = {
                                                "int_0":"Unkown",
                                                "int_1":"Minor",
                                                "int_2":"Moderate",
                                                "int_3":"Major"
                                            }
        self.drug_id = drug_id
        self.generic_name = None
        self.brand_name = []
        self.drug_class = []
        
        self.drug_html = None
        self.dom = None
        self.interaction_link = None
        self.interaction_html = None
        self.interactions_tags = []
        self.disease_interactions_tags = []
        self.interactions = []
        self.disease_interactions = []
        
        self.request_maxout = 5
        self.scrap_succeeded = []
        self.scrap_failed = []
    
    def reset_maxout(self):
        self.request_maxout = 5
        
    def assert_brand_name(self):
        brands = self.dom[0].xpath('//*[@id="content"]/div[2]/p[1]/text()')
        for idx, ls in enumerate(brands[:-2]):
            if brands[idx] == '\n' and brands[idx+2] == '\n':
                self.brand_name = self.remove_tags(brands[idx+1]).split(',')
                break
    
    def assert_generic_name(self):
        generic_extracted = str(self.drug_html.find("p","drug-subtitle")).split("<br/>")[0].split('</b>')[-1]
        self.generic_name = self.remove_tags(generic_extracted)
        
    def assert_drug_class(self):
        self.drug_class = [ self.remove_tags(a.text) for a in self.drug_html.find("p","drug-subtitle").find_all("a")] 
        
    def asser_names(self):
        self.assert_brand_name()
        self.assert_generic_name()
        self.assert_drug_class()
        
    def get_drug_html(self):
        self.reset_maxout()
        while self.request_maxout != 0:
            res = requests.get(self.drug_link)
            if res.status_code == 200: 
                self.drug_html = BeautifulSoup(res.text, 'html.parser') 
                self.dom = etree.HTML(str(self.drug_html))
                self.asser_names()
                return 
            else:
                self.request_maxout -= 1
                print(res)
        raise Exception("couldn't get the drug page")
    
    def get_interaction_link(self):
        divs_links_list = self.drug_html.find_all("div","ddc-related-link")
        a_tag_list = [div.find("a") for div in divs_links_list]
        for a in a_tag_list:
            if "interactions" in a.string:
                if a.has_attr("href"):
                    self.interaction_link = a.get("href")
                    return self.interaction_link
        raise Exception("no link found")
    
    def get_interaction_html(self):
        self.reset_maxout()        
        while self.request_maxout != 0:
            res = requests.get(self.base_url + self.interaction_link)
            if res.status_code == 200: 
                self.interaction_html = BeautifulSoup(res.text, 'html.parser') 
                return
            else:
                self.request_maxout -= 1
        raise Exception("couldn't get the drug interaction page")
        
    
    def get_interactions_tags(self):
        ul_list = self.interaction_html.find_all("ul")
        
        li_interaction_list = []
        i = 0
        for ul in ul_list:
            if ul.get("class")is not None and "interactions" in ul.get("class"):
                if i == 0: # first list for interactions
                    self.interactions_tags = ul.find_all("li")
                    i+=1
                else: # second list for disease interactions
                    self.disease_interactions_tags = ul.find_all("li")
    
    def get_interactions(self):
        for li in self.interactions_tags:
            self.interactions.append( (li.string , self.interaction_class_to_level_dict[li.get("class")[0]]) )
#             print(li.string, interaction_level[li.get("class")[0]])
            
    def get_disease_interactions(self):
        for li in self.disease_interactions_tags:
            self.disease_interactions.append( (li.string, self.interaction_class_to_level_dict[li.get("class")[0]]) )
#             print(li.string, interaction_level[li.get("class")[0]])


    def remove_tags_helper(self, s):
        idx = 0
        open_tag = 0
        close_tag = 0
        tag_type = None
        s_reduced = s
        found_tag = False
        for i in range(len(s)):
            if s[i] == '<' and s[i+2] != '>':
                    open_tag = i
                    tag_type = s[i+1]
                    found_tag = True
                    for j in range(i,len(s)):
                        if s[j] == '>':
                            close_tag = j
                            break
                    s_reduced =  s[:open_tag] + s[close_tag+1:]

        return s_reduced


    def remove_tags(self, s):
        s_reduced = self.remove_tags_helper(s)
        while s_reduced != s:
            s = s_reduced
            s_reduced = self.remove_tags_helper(s)
        return s_reduced
        
    
    def get_json(self, path = None, save = False):
        dicts = []
        for brand_name in self.brand_name:
            with open('./drugs/new/'+str(brand_name)+'.txt', 'w', encoding='utf-8') as f:
                f.write(str(self.drug_html)) 

            aDict = {
                    'id': self.drug_id,
                    'generic_name': self.generic_name,
                    'brand_name': brand_name,
                    'drug_class': self.drug_class,
                    'drug_interaction': self.interactions,
                    'disease_interaction': self.disease_interactions,
                    'source': 'drugs.com'
            }
            dicts.append(aDict)
        
        return dicts