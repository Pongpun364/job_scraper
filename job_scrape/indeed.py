from os import link
import sys
import asyncio
from requests_html import HTML
import itertools
import re
import time
from urllib.parse import urlparse
# from ..storage import list_to_sql, df_from_sql, df_to_sql
from my_logging import  set_arsenic_log_level
from scraper import scraper
from storage import df_to_csv

# print(sys.path)
async def extract_id(url_path):
    regex = r"([0-9a-z]+)\Sfccid"
    my_match = re.findall(regex, url_path)
    if not my_match:
        return None
    return my_match[0]

async def extract_salary(result):
    data = result.find('.salary-snippet', first=True)
    if data != None:
        regex = r"[\d,]+"
        my_match = re.findall(regex, data.text)
        if not my_match:
            return None, None
        return my_match[0].replace(',', '') , my_match[1].replace(',', '')
    return None, None


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






async def indeed_scraper(url, i=-1, timeout = 120, start=None, delay=15):

    body = await scraper(url,i=i, timeout = timeout, start=start, delay=delay)

    links = await get_link_data(body)
    print('links ==', links)
    # product_data = await get_product_data(url, body )
    
    
    if start != None:
        end = time.time() - start
        print(f'{i} took {end} seconds')
    
    dataset = {
        'links': links,
        'job_desc': None
    }
    return dataset



async def run(urls, start=None):
    results = []
    for i, url in enumerate(urls):
        results.append(
            asyncio.create_task(indeed_scraper(url, i=i, timeout=120, start=start ,delay = 10))
        )
    list_of_links = await asyncio.gather(*results)
    return list_of_links


# def get_saved_urls(limit=5):

    # links_df = df_from_sql('spoonflower_links')
    # urls = []
    # scraped_ids = []
    # used_df = False

    # if not links_df.empty:
    #     sub_link_df = links_df.copy()
    #     sub_link_df = sub_link_df[sub_link_df['scraped'] == 0]
    #     sub_link_df = sub_link_df.sample(limit)
    #     urls = [f'https://www.spoonflower.com{x}'for x in sub_link_df['path'].to_list()]
    #     scraped_ids = sub_link_df.id.to_list()
    #     if len(urls) > 0:
    #         used_df = True
    # return urls, scraped_ids, used_df



# def get_list_range(limit=10, is_random=True, random_max=150):
#     urls = []
#     for i in range(limit):
#         if is_random:
#             page = random.randint(i+1, random_max)
#         else:
#             page = i + 1
#         urls.append(f"https://www.spoonflower.com/en/shop?on=fabric&page_offset={page}")
#     return urls



def run_indeed():
    set_arsenic_log_level()
    start = time.time()
    urls = ['https://th.indeed.com/jobs?q=python+developer&l=กรุงเทพ&start=0' ]

    results = asyncio.run(run(urls, start = start))
    end = time.time() - start
    print('total time =', end)
    links = [x['links'] for x in results ] # [[],[],[]]
    links = itertools.chain.from_iterable(links)
    links = list(links)
    link_columns = ['id', 'title', 'min_salary', 'max_salary', 'scraped']
    df_to_csv(links, columns=link_columns)


if __name__ == "__main__":
    run_indeed()
    
