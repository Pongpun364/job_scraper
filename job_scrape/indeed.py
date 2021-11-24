from os import link
import sys
import asyncio
from requests_html import HTML
import itertools
import re
import time
import pandas as pd
from urllib.parse import urlparse
# from ..storage import list_to_sql, df_from_sql, df_to_sql
from my_logging import  set_arsenic_log_level
from scraper import scraper
from storage import df_to_csv
from my_utils import extract_id, extract_salary,\
    firsttime_query, \
    get_list_urls, get_saved_urls




async def get_link_data(body):
    datas = []
    html_r = HTML(html=body)
    for result in html_r.find('.result'):
        try:
            title = result.find('.jobTitle', first=True).text
        except:
            title = None
        try:
            path = result.attrs['href']
            id_ = await extract_id(path) 
        except:
            id_ = None
        
        min_salary , max_salary = await extract_salary(result)
        data = {
            'id' : id_,
            'title': title,
            'min_salary': min_salary,
            'max_salary': max_salary,
            'scraped': 0
        }
        datas.append(data)
    return datas   

async def get_job_data(url,body):
    html_r = HTML(html=body)
    id_ = url.split('jk=')[1]
    try:
        job_desc  = html_r.find('#jobDescriptionText', first=True).text
    except:
        job_desc = None
    datas = {
        'id':id_,
        'job_desc':job_desc
    }
    return datas

async def get_num_all_page(body):
    html_r = HTML(html=body)
    num_all_jobs = html_r.find('#searchCountPages', first=True).text

    regex = r'[\d]+'
    num_all_jobs = int(re.findall(regex,num_all_jobs)[1].replace(',',''))
    num_all_pages = num_all_jobs // 15
    num_all_pages

    return num_all_pages


async def indeed_scraper(url,first_time=False,extract_links=False,extract_jobdesc=False, i=-1, timeout = 120, start=None, delay=15):

    body = await scraper(url,i=i, timeout = timeout, start=start, delay=delay)

    links = None
    job_desc = None
    num_all_pages = None
    if extract_links:
        links = await get_link_data(body)
        print('links ==', links)
    if extract_jobdesc:
        job_desc = await get_job_data(url,body)
    if first_time:
        num_all_pages = await get_num_all_page(body)

    if start != None:
        end = time.time() - start
        print(f'{i} took {end} seconds')
    
    dataset = {
        'links': links,
        'job_desc': job_desc,
        'num_all_pages':num_all_pages
    }
    return dataset



async def run(urls, start=None,first_time=False,extract_links=False,extract_jobdesc=False):
    results = []
    for i, url in enumerate(urls):
        results.append(
            asyncio.create_task(indeed_scraper(url,first_time=first_time, 
            extract_links=extract_links, extract_jobdesc=extract_jobdesc, 
            i=i, timeout=120, start=start ,delay = 10))
        )
    list_of_links = await asyncio.gather(*results)
    return list_of_links


def run_indeed(query = 'python developer',first_time=False,
 extract_links=False, extract_jobdesc=False , 
 limit = 10, start_url=0):
    set_arsenic_log_level()
    start = time.time()
    urls = ['https://th.indeed.com/jobs?q=python+developer&start=0' ]
    scraped_id = []
    is_updated = False
    if first_time:
        urls = firsttime_query(query=query)
    if extract_links==True and first_time == False:
        urls = get_list_urls(limit=limit,query=query,start_url=start_url)
    if extract_jobdesc == True:
        urls, scraped_id, is_updated  = get_saved_urls(limit=limit,query=query)





    # print(urls)


    # create tasks
    results = asyncio.run(run(urls, start = start, 
    first_time=first_time,extract_links=extract_links,
    extract_jobdesc=extract_jobdesc))

    end = time.time() - start
    print('total time =', end)
    if extract_links:
        links = [x['links'] for x in results ] # [[],[],[]]
        print(links)
        links = itertools.chain.from_iterable(links)
        links = list(links)
        link_columns = ['id', 'title', 'min_salary', 'max_salary', 'scraped']
        df_to_csv(links, columns=link_columns)
    
    if extract_jobdesc:
        jobdesc = [x['job_desc'] for x in results ]
        job_col = ['id', 'job_desc']
        df_to_csv(jobdesc, columns=job_col,name='../job_desc.csv')
    if first_time:
        num_all_pages = results[0]['num_all_pages']
        _ = firsttime_query(query=query, num_page = num_all_pages)


    if is_updated:
        links_df = pd.read_csv('../links.csv')
        link_cond = links_df['id'].isin(scraped_id)
        links_df.loc[link_cond, 'scraped'] = 1
        links_df.to_csv('../links.csv', index=False)

if __name__ == "__main__":
    # run_indeed(query='javascript developer',first_time=True)
    # run_indeed(extract_links=True,first_time=False,start_url=1,limit=2)
    # run_indeed(extract_jobdesc=True,limit=2)
