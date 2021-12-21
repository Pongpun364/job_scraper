import re
import pandas as pd
from storage import df_to_sql, df_from_sql, list_to_sql
# print(sys.path)
async def extract_id(url_path):
    regex = r"([0-9a-z]+)\Sfccid"
    my_match = re.findall(regex, url_path)
    if not my_match:
        return None
    return my_match[0]

async def extract_salary(result):
    data = result.find('.salary-snippet', first=True)
    print('data = = ', data)
    if data != None:
        regex = r"[\d,]+"
        my_match = re.findall(regex, data.text)
        if not my_match:
            return None, None
        return my_match[0].replace(',', '') , my_match[1].replace(',', '')
    return None, None

async def extract_salary_one(result):
    data = result.find('.salary-snippet', first=True)
    print('data = = ', data)
    if data != None:
        regex = r"[\d,]+"
        my_match = re.findall(regex, data.text)
        if not my_match:
            return None
        return my_match[0].replace(',', '')
    return None




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







def firsttime_query(query='python developer'):
    q_str = query.replace(' ','%20')
    print('query in function firsttime_query == ',query)
    urls = [f'https://th.indeed.com/jobs?q={q_str}&start=0']
    return urls

def get_list_urls(limit=10,query='python developer',start_url=0):
    urls = []
    print('query in function get_list_urls == ',query)
    q_str = query.replace(' ','+')
    for i in range(limit):
        urls.append(f'https://th.indeed.com/jobs?q={q_str}&start={(start_url+i)*10}')
    return urls

def get_saved_urls(limit=10,query='python developer'):
    links_df = df_from_sql(table_name=f'{query}_link')
    urls = []
    scraped_id = []
    is_updated = False
    is_done = False
    is_failed = False
    if links_df.empty:
        is_done = True
        is_failed = True
        return urls, scraped_id, is_updated, is_done,is_failed
    sub_link_df = links_df.copy()
    sub_link_df = sub_link_df[~(sub_link_df['id'].isnull()) & (sub_link_df['scraped'] == 0)]
    if sub_link_df.empty:
        is_done = True
        return urls, scraped_id, is_updated, is_done,is_failed
    try:
        sub_link_df = sub_link_df.sample(limit)
    except:
        sub_link_df = sub_link_df
    urls = [f'https://th.indeed.com/viewjob?jk={x}' for x in sub_link_df['id'].to_list()]
    scraped_id = sub_link_df.id.to_list()
    if len(urls) > 0:
        is_updated = True
    return urls, scraped_id, is_updated, is_done,is_failed
