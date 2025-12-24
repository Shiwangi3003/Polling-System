from starlette.datastructures import UploadFile
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, HTMLResponse
from models import poll_details, update_poll_details
from uuid import uuid4
from configuration import collection
from fastapi.templating import Jinja2Templates
from bson import ObjectId

def convert_mongo(obj):
    if isinstance(obj, ObjectId):
        return str(obj)
    if isinstance(obj, dict):
        return {k: convert_mongo(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [convert_mongo(v) for v in obj]
    return obj


app=FastAPI()
templates = Jinja2Templates(directory="views")

@app.post("/create_poll")
def create_poll(req: poll_details):
    req= req.dict()
    req["poll_id"] = str(uuid4())
    
    data = collection.find_one({"question": req["question"]})
    if not data:
        collection.insert_one(req)
    else:
        return JSONResponse(status_code=500, content= "An error occured" )
    
    return JSONResponse(status_code=201,content={"msg": "Poll created successfully", "polling_id": req["poll_id"]})


@app.get("/polls")
def get_all_polls():
    data = collection.find()
    data = list(data)
    for i in data:
        i["_id"]=str(i["_id"])
    
    return JSONResponse(data)


@app.put("/update_poll")
def changing_poll(req: update_poll_details):
    req = req.dict()
    res = collection.find_one({"poll_id": req["poll_id"]})
    if res == "Null":
        return JSONResponse(status_code=404, detail="Poll-Id not found")
    else:
        collection.update_one({"poll_id":req["poll_id"]}, {"$set":req})
    
    return JSONResponse(status_code=200,content={"msg": "Event updated successfully"})
        

@app.delete("/delete_poll/{poll_id}")
def deleting_poll(poll_id: str):
    res = collection.find_one({"poll_id":poll_id})
    if res == "Null":
        return JSONResponse(status_code=404, content={"msg":"Poll not found"})
    else:
        collection.delete_one({"poll_id":poll_id})

    return JSONResponse(status_code=200, content={"msg": "Poll deleted successfully"})


@app.get("/polls/{poll_id}",response_class = HTMLResponse)
def get_poll(req: Request, poll_id: str):
    res = collection.find_one({"poll_id": poll_id})
    if res == "Null":
        return JSONResponse(status_code=404, content={"msg":"Poll not found"})
    res = convert_mongo(res)
    
    return templates.TemplateResponse("index.html", {"request": req, "details": res})


@app.post("/submit")
async def submitResponse(req: update_poll_details):
    req = req.dict()
    pollOption = req["pollOption"];
    res = collection.find_one({"poll_id": req["poll_id"]})
    if res == "Null":
        return JSONResponse(status_code=404, detail="Poll-Id not found")
    else:
        req = res
        req["response"][pollOption]+=1
        collection.update_one({"poll_id":req["poll_id"]}, {"$set":req})
    
    return JSONResponse(status_code=200,content={"msg": "Event updated successfully"})


@app.get("/poll/result/{poll_id}",response_class = HTMLResponse)
def get_poll(req: Request, poll_id: str):
    res = collection.find_one({"poll_id": poll_id})
    res = convert_mongo(res)
    
    if res == "Null":
        return JSONResponse(status_code=404, content={"msg":"Poll not found"})
    
    total_count = sum(res["response"])
    for i in range(len(res["response"])):
        res["response"][i] = (res["response"][i] / total_count) * 100 

    return templates.TemplateResponse("result.html", {"request": req, "details": res, "totalCount": total_count})
