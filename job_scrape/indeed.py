import asyncio
from requests_html import HTML
import itertools
import re
import random
import time
import pandas as pd
from urllib.parse import urlparse
# from ..storage import list_to_sql, df_from_sql, df_to_sql
from my_logging import  set_arsenic_log_level
from scraper import scraper
from storage import df_from_sql, df_to_sql, list_to_sql
from my_utils import extract_salary,\
    firsttime_query, \
    get_list_urls, get_saved_urls,\
    extract_salary_one


from data_cleaner import summary_data


async def get_link_data(body):
    if not body:
        return [{
            'id' : None,
            'title': None,
            'min_salary': None,
            'max_salary': None,
            'salary':None,
            'scraped': 0
        }]
    datas = []
    html_r = HTML(html=body)
    salary = None
    min_salary = None
    max_salary = None
    for result in html_r.find('.result'):
        try:
            title = result.find('.jobTitle', first=True).text
        except:
            title = None
        try:
            class_result = list(result.attrs['class'])
            id_ = [x for x in class_result if x.startswith('job')][0]
            id_ = id_.split('_')[1]

        except:
            id_ = None
        try:
            min_salary , max_salary = await extract_salary(result)
        except:
            salary = await extract_salary_one(result)
        # print(min_salary,max_salary)
        data = {
            'id' : id_,
            'title': title,
            'min_salary': min_salary,
            'max_salary': max_salary,
            'salary':salary,
            'scraped': 0
        }
        datas.append(data)
    return datas   

async def get_job_data(url,body):
    if not body:
        return {
            'id':None,
            'job_desc':None
            }
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
    try:
        num_all_jobs = html_r.find('#searchCountPages', first=True).text
    except:
        return 20
    regex = r'[\d,]+'
    num_all_jobs = re.findall(regex,num_all_jobs)[1].replace(',','')
    num_all_pages = int(num_all_jobs) // 15
    num_all_pages
    return num_all_pages


async def indeed_scraper(url,first_time=False,extract_links=False,
extract_jobdesc=False, i=-1, timeout = 120, start=None, delay=15):

    body = await scraper(url,i=i, timeout = timeout, start=start, delay=delay)

    links = None
    job_desc = None
    num_all_pages = None
    if extract_links:
        links = await get_link_data(body)
        print(f'links({i}) ==', links)

    if extract_jobdesc:
        job_desc = await get_job_data(url,body)
        # print("get the job desc ############# {}".format(job_desc))

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
    delay = 5
    if first_time:
        delay = 10
    for i, url in enumerate(urls):
        results.append(
            asyncio.create_task(indeed_scraper(url,first_time=first_time, 
            extract_links=extract_links, extract_jobdesc=extract_jobdesc, 
            i=i, timeout=60, start=start ,delay = delay))
        )
    list_of_links = await asyncio.gather(*results)
    return list_of_links


async def run_indeed(query = 'python developer',first_time=False,
 extract_links=False, extract_jobdesc=False , 
 limit = 10, start_url=0):
    set_arsenic_log_level()
    query_name = query.strip().replace(' ','_')
    start = time.time()
    urls = ['https://th.indeed.com/jobs?q=python+developer&start=0' ]
    scraped_id = []
    is_updated = False
    is_done = False
    is_failed = False
    if first_time:
        print('query (run_indeed,first time) = ', query)
        print('query_name (run_indeed,first time) = ', query_name)
        urls = firsttime_query(query=query)
    if extract_links==True and first_time == False:
        print('query (run_indeed,extract_links) = ', query)
        print('query_name (run_indeed,extract_links) = ', query_name)
        urls = get_list_urls(limit=limit,query=query,start_url=start_url)
    if extract_jobdesc == True:
        urls, scraped_id, is_updated,is_done,is_failed  = get_saved_urls(limit=limit,query=query_name)


    if is_done or is_failed:
        return is_done,is_failed


    # print(urls)


    # create tasks
    results = await run(urls, start = start, 
    first_time=first_time,extract_links=extract_links,
    extract_jobdesc=extract_jobdesc)

    end = time.time() - start
    print('total time =', end)
    if extract_links:
        links = [x['links'] for x in results ] # [[],[],[]]
        print('link before itertool =', links)
        links = itertools.chain.from_iterable(links)

        links = list(links)
        link_columns = ['id', 'title', 'min_salary', 'max_salary','salary', 'scraped']
        list_to_sql(links, table_name=f'{query_name}_link', columns=link_columns)

    
    if extract_jobdesc:
        
        jobdesc = [x['job_desc'] for x in results ]
        job_col = ['id', 'job_desc']
        list_to_sql(jobdesc, table_name=f'{query_name}_job_desc', columns=job_col)

    if first_time:
        num_all_pages = results[0]['num_all_pages']
        
        old_df = df_from_sql('query_note_table')
        if old_df.empty:
            old_df = pd.DataFrame([{'q_str':None, 'num_page': None}])
        new_df = pd.DataFrame([{'q_str':f'{query_name}', 
                'num_page': num_all_pages if num_all_pages < 30 else 30}])
        df = pd.concat([old_df,new_df])
        df.dropna(inplace=True)
        df = df.loc[~df['q_str'].duplicated(keep='first')]
        df_to_sql(df, table_name='query_note_table')

        return num_all_pages


    if is_updated:
        links_df = df_from_sql(table_name=f'{query_name}_link')
        link_cond = links_df['id'].isin(scraped_id)
        links_df.loc[link_cond, 'scraped'] = 1
        df_to_sql(links_df, table_name=f'{query_name}_link')
    
    return is_done,is_failed


async def orchestrator(query = 'python developer'):
    # run first time and collect the number of all pages
    num_all_pages = await run_indeed(query=query,first_time=True,extract_links=True)
    my_num = [5,6,7,8,9,10]
    print('initialize query == ', query)
    # collecting all the links from all the pages according to the num_all_pages given previous
    await asyncio.sleep(5)



    ### extract links from all pages
    if num_all_pages <= 10:
        await run_indeed(query=query, extract_links=True,first_time=False,start_url=1,limit=5)
        await asyncio.sleep(random.choice(my_num))
        await run_indeed(query=query, extract_links=True,first_time=False,start_url=6,limit=5)
    else: # num_all_pages > 10 #### and num_all_pages<=20: 
        await run_indeed(query=query, extract_links=True,first_time=False,start_url=1,limit=5)
        await asyncio.sleep(random.choice(my_num))
        await run_indeed(query=query, extract_links=True,first_time=False,start_url=6,limit=5)
        await asyncio.sleep(random.choice(my_num))
        await run_indeed(query=query, extract_links=True,first_time=False,start_url=11,limit=5)
        await asyncio.sleep(random.choice(my_num))
        await run_indeed(query=query, extract_links=True,first_time=False,start_url=16,limit=5)
        await asyncio.sleep(random.choice(my_num))
    # else:
    #     print('query (orchestrator) = ', query)
    #     await run_indeed(query=query, extract_links=True,first_time=False,start_url=1,limit=5)
    #     await asyncio.sleep(random.choice(my_num))
    #     await run_indeed(query=query, extract_links=True,first_time=False,start_url=6,limit=5)
    #     await asyncio.sleep(random.choice(my_num))
    #     await run_indeed(query=query, extract_links=True,first_time=False,start_url=11,limit=5)
    #     await asyncio.sleep(random.choice(my_num))
    #     await run_indeed(query=query, extract_links=True,first_time=False,start_url=16,limit=5)
    #     await asyncio.sleep(random.choice(my_num))
    #     await run_indeed(query=query, extract_links=True,first_time=False,start_url=21,limit=5)
    #     await asyncio.sleep(random.choice(my_num))
    #     await run_indeed(query=query, extract_links=True,first_time=False,start_url=26,limit=5)
    #     await asyncio.sleep(random.choice(my_num))


    # collecting all the job_data randomly 
    # num_all_job = num_all_pages * 15
    # num_iter = (num_all_job // 6) + 1
    # # num_iter = 5


    while True:
        # print("i'am in while loop")
        is_done,is_failed = await run_indeed(query=query, extract_jobdesc=True,limit=6)
        # print("done extracting job description!")
        if is_failed:
            print("sorry, i am failing ...  ")
            return
        await asyncio.sleep(random.choice(my_num)) 
        print("is_done variable ...  ", is_done)
        if is_done:
            start = time.time()
            print("start finalize the process .....")
            await summary_data(query=query)
            print("TIME CONSUMED == ", time.time() - start)
            print('DONE ALL PROCESS, CONGRATES! ')
            return
            
    # return

def perform_scrape(query='game developer'):
    asyncio.run(orchestrator(query=query))
    return

if __name__ == "__main__":
    perform_scrape(query='painter')
    # run_indeed(query='web developer',first_time=True)
    # run_indeed(extract_links=True,first_time=False,start_url=1,limit=2)
    # run_indeed(extract_jobdesc=True,limit=2)



        #    query_name = query.replace(' ','+')
        #     links_df = pd.DataFrame([{'q_str':f'{query_name}', 
        #     'num_page': num_all_pages if num_all_pages < 20 else 20}])