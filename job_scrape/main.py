from fastapi import FastAPI, Request, \
    Header, Depends, HTTPException, Body
from fastapi.responses import JSONResponse

from conf import get_settings, Settings

from worker import create_task,add_scrape
from celery.result import AsyncResult
from storage import df_from_sql

app = FastAPI()

settings = get_settings()
print("DEBUG ==", settings.debug)

@app.get("/")
def get_home(request: Request):
    result = { "hello world": 111 }
    return JSONResponse(result)



def verify_auth(authorization = Header(None),settings:Settings = Depends(get_settings)):
    """          
    Authorization: Bearer <token>
    {"authorization": "Bearer <token>"}
    """
    print("settings == ...", dict(settings))
    print("authorization == ...", authorization )
    if settings.debug and settings.skip_auth:
        return
    if authorization is None:
        raise HTTPException(detail="absent of authorization headers", status_code=401)
    label, token = authorization.split()
    if token != settings.app_auth_token:
        raise HTTPException(detail="Invalid token", status_code=401)

@app.post("/")
async def test_auth(authorization = Header(None) , payload = Body(...) ,settings: Settings = Depends(get_settings)):
    print("body ==", payload)
    verify_auth(authorization,settings)
    result = {"result": 'you are pass, Congrates !'}
    return JSONResponse(result)

@app.post("/scraper/{search_keyword}", status_code=201)
async def scraper(search_keyword: str):
    task = add_scrape.delay(search_keyword) ## สร้าง task ขึ้นมา เเละ return task id กลับไปก่อน
    result = {
        "task_id": task.id
    }
    print("result = ", result)
    return JSONResponse(result)


@app.post("/test/{num}", status_code=201)
async def test_add(num: str):
    task = create_task.delay(num) ## สร้าง task ขึ้นมา เเละ return task id กลับไปก่อน
    result = {
        "task_id": task.id
    }
    # print("result = ", result)
    return JSONResponse(result)

# @app.get("/test_db/{table_name}")
def get_table(table_name: str):
    df = df_from_sql(table_name)
    return df.to_json()

@app.get("/check/{task_id}")
def get_status(task_id: str):
    task_result = AsyncResult(task_id)
    result = {
        "task_id": task_id,
        "task_status": task_result.status,
        "task_result": task_result.result
    }
    if task_result.status == "SUCCESS" and task_result.result != True:
        table_name = task_result.result
        print('table_name ....', table_name)
        data = get_table(table_name)
        return data
    else:
        return JSONResponse(result)

