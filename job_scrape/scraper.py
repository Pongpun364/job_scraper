import asyncio
from time import time
from arsenic import get_session,browsers, services
import pathlib
from fake_useragent import UserAgent


BASE_DIR = pathlib.Path().resolve()
print('BASE_DIR == ' ,BASE_DIR)
EXE_PATH = str(BASE_DIR / "driver" / "chromedriver.exe")
print('EXE_PATH ==', EXE_PATH)



async def get_user_agent():
    return UserAgent(verify_ssl=False).random

# reference is in nbs: "webscrape asynchronous.ipynb"
async def perform_scrape(session, url, delay):
    await session.get(url)
    
    curr_heigth = await session.execute_script("return document.body.scrollHeight")
    print('curr_heght ==',curr_heigth)
    i = 0
    while True:
        await session.execute_script("window.scrollTo(0, document.body.scrollHeight)")
        await asyncio.sleep(delay)
        i += 1
        print(f'{i} time of sleep')
        iter_height = await session.execute_script("return document.body.scrollHeight")
        print('iter heght ==', iter_height)
        if iter_height == curr_heigth:
            print('i am out man !')
            break
        curr_heigth = iter_height
    try:
        close_butt = await session.get_element('.popover-x-button-close')
        await close_butt.click()
    except:
        pass
    return await session.get_page_source()




async def scraper(url, i=-1, timeout = 120, start=None, delay=15):
    print("real time out used ==...", timeout)
    service = services.Chromedriver()
    browser = browsers.Chrome()
    my_user_agent = await get_user_agent()
    browser.capabilities = {
        "goog:chromeOptions": {"args": [ "--whitelisted-ips=","--disable-dev-shm-usage","--no-sandbox", "--headless", "--disable-gpu", f'user-agent={my_user_agent}', "--verbose"]}
    }
    async with get_session(service, browser) as session:
        try:
            body = await asyncio.wait_for(perform_scrape(session, url, delay), timeout = timeout)
        except asyncio.TimeoutError:
            print('time out fuckkkk!!!')
            return
        except Exception as e:
            print( ' what is this fuck ===============================================================', e)
            return
        return body