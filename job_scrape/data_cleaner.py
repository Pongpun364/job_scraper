import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pandas as pd
import numpy as np
import re
import json

import nltk
from collections import Counter
from nltk import word_tokenize
import matplotlib.pyplot as plt
nltk.download('stopwords')
nltk.download('punkt')
from nltk.corpus import stopwords

from storage import df_from_sql, df_to_sql, list_to_sql

stop_words = stopwords.words('english')
technical_skills = ['python', 'c','r', 'c++','java','hadoop','scala','flask','pandas','spark','scikit-learn',
                    'numpy','php','sql','mysql','css','nltk','fastapi' , 'keras', 'pytorch','tensorflow',
                   'linux','Ruby','JavaScript','django','react','reactjs','ai','ui','tableau','blockchain','angular','backend',
                    'docker','jquery','nodejs', 'mongodb', 'postgresql', 'kubernetes', 'bootstrap' ,'kafka','kotlin','tdd','unix',
                   'laravel','microservices','swift','amazon','vuejs','apache','ansible','ajax','perl','nginx','telecommunications',
                   'spring','sass','azure','nosql','jira','git','ios','android','scrum','jenkins','elasticsearch','golang',
                   'solidity','rails','selenium','excel','powerbi','raspberry','nextjs','oracle','bash','grafana','visio']




def extract_salary2(row):
    # extract min max or salary
    if pd.isnull(row['min_salary']):
        regex = r'\b[\d]{2,3},[\d]{3}|[\d]{2,3}[k|K]*\s-\s[\d]{2,3}[k|K]{1}'
        try:
            my_match = re.findall(regex, row['job_desc'])
        except:
            my_match = None
        if not my_match:
            pass
        elif len(my_match) == 2:
            my_match[0] = my_match[0].replace(',', '').strip()
            my_match[1] = my_match[1].replace(',', '').strip()
            try:
                if int(my_match[0]) > int(my_match[1]):
                    row['max_salary'] = my_match[0]
                    row['min_salary'] = my_match[1]
                else:
                    row['min_salary'] = my_match[0]
                    row['max_salary'] = my_match[1]
            except:
                pass
        elif len(my_match) == 1:
            if 'k' in my_match[0] or 'K' in my_match[0]:
                result = my_match[0].split('-')
                row['min_salary'] = result[0].strip().replace('k','000').replace('K','000')
                row['max_salary'] = result[1].strip().replace('k','000').replace('K','000')
            else:
                row['salary'] = my_match[0].replace(',', '').strip()
        else:
            pass
    return row



def clean_data(desc):
    if desc == None:
        pass
    else:
        desc = word_tokenize(desc)
        desc = [ word.lower() for word in desc if word.isalpha() and len(word) > 2]
        regex = r"[a-zA-Z\d]+"
        desc = list(set([ word for word in desc if word not in stop_words and re.findall(regex,word) ]))
    return desc




def extract_experience(row):
    # extract english first
    row['min_exp'] = np.nan
    row['max_exp'] = np.nan
    try:
        regex1 = r"(?=.*years|year)(?=.*experience|experiences).*"
        result = []
        for line in re.findall(regex1,row['job_desc'],re.IGNORECASE):
            regex2 = r"([\d]+\s?-?(?:to)?\s?[\d+]*)"
            result += re.findall(regex2,line)

    except TypeError:
        print('TypeError')
        print(result)
        return row
    
    if not result:
        regex3 = r'(?=.*ประสบการณ์)(?=.*ปี).*'
        result = []
        for line in re.findall(regex3,row['job_desc']):
            regex4 = r'[\d]+\s?-?\s?[\d+]*'
            result += re.findall(regex4,line)
    
    if not result:
        return row
    else:
        result = result[0].replace("+","")
        
    if '-' in result:
        exp_ = result.split('-')
        min_exp = exp_[0].strip()
        max_exp = exp_[1].strip()
        if int(min_exp) > 18 or int(max_exp) > 18 :
            return row
        row['min_exp'] = min_exp
        row['max_exp'] = max_exp
    elif 'to' in result:
        exp_ = result.split('to')
        min_exp = exp_[0].strip()
        max_exp = exp_[1].strip()
        if int(min_exp) > 18 or int(max_exp) > 18 :
            return row
        row['min_exp'] = min_exp
        row['max_exp'] = max_exp
    else:
        min_exp = result.strip()
        if int(min_exp) > 18:
            return row
        row['min_exp'] = min_exp
    
    return row


def clean_series_exp(x):
    for k in x.copy():
        if k not in technical_skills:
            del x[k] 
    return json.dumps(dict(x))
    

async def summary_data(query = 'python developer'):
    query_name = query.replace(' ','_')
    link_df = df_from_sql(table_name = f'{query_name}_link')
    link_df.replace([None], np.nan, inplace=True)
    job_df = df_from_sql(table_name = f'{query_name}_job_desc')

    new_df = pd.merge(job_df,link_df,how='outer',on='id')
    new_df = new_df.apply(extract_salary2, axis="columns")
    tag_df = new_df['job_desc'].apply(clean_data)
    new_df['extracted_skill'] = tag_df.apply(Counter)

    new_df = new_df.apply(extract_experience, axis=1)
    new_df['extracted_skill'] = new_df['extracted_skill'].apply(clean_series_exp)
    new_df = new_df[['max_salary','min_salary','salary','extracted_skill','min_exp','max_exp']]
    df_to_sql(new_df, table_name=f'{query_name}_final')
