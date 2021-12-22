import asyncio
from time import time
from arsenic import get_session,browsers, services, keys
from my_logging import set_arsenic_log_level
import pathlib
from fake_useragent import UserAgent
from PIL import Image
import io
import uuid

BASE_DIR = pathlib.Path().resolve()
IMAGE_DIR = BASE_DIR / "uploads"

test_url = "https://th.indeed.com/jobs?q=javascript%20developer&start=0"


async def get_user_agent():
    return UserAgent(verify_ssl=False).random


async def perform_scrape(session, url, delay):
    set_arsenic_log_level()
    await session.get(url)
    
    # curr_heigth = await session.execute_script("return document.body.scrollHeight")
    # print('curr_heght ==',curr_heigth)
    # i = 0
    # while True:
    #     await session.execute_script("window.scrollTo(0, document.body.scrollHeight)")
    await asyncio.sleep(delay)
    #     i += 1
    #     print(f'{i} time of sleep')
    #     iter_height = await session.execute_script("return document.body.scrollHeight")
    #     print('iter heght ==', iter_height)
    #     if iter_height == curr_heigth:
    #         print('i am out man !')
    #         break
    #     curr_heigth = iter_height
    # try:
    #     close_butt = await session.get_element('.popover-x-button-close')
    #     await close_butt.click()
    # except:
    #     pass
    return await session.get_screenshot()




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


def main():
    
    screenshot = asyncio.run(scraper(test_url, timeout=50))
    # print(type(screenshot))
    IMAGE_DIR.mkdir(exist_ok=True)
    img = Image.open(screenshot)

    fext = ".png"
    dest = IMAGE_DIR / f"{uuid.uuid1()}{fext}"
    # with open(str(dest), 'wb') as out:
    #     out.write(bytes_str.read())
    img.save(dest)
    return

if __name__ == "__main__":
    main()