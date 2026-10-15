from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, HTMLResponse
from models import poll_details, update_poll_details
from uuid import uuid4
from configuration import collection
from database.schema import response_parser
from fastapi.templating import Jinja2Templates


app=FastAPI()
try:
    templates = Jinja2Templates(directory="views")
except Exception as _e:
    templates = None
    print("Warning: jinja2 must be installed to use template endpoints.\nInstall with: python -m pip install Jinja2\nOr run the app with: uvicorn main:app --reload")


@app.get("/", response_class=HTMLResponse)
def home(req: Request):
    if templates is None:
        return JSONResponse(status_code=500, content={
            "msg": "jinja2 not available. Install with `python -m pip install Jinja2` and run via `uvicorn main:app --reload`."
        })

    data = response_parser(collection.find())
    return templates.TemplateResponse("home.html", {"request": req, "polls": data})

@app.post("/create_poll")
def create_poll(req: poll_details):
    req= req.dict()
    req["poll_id"] = str(uuid4())
    req["response"] = [0] * len(req["options"])
    
    data = collection.find_one({"question": req["question"]})
    if not data:
        collection.insert_one(req)
    else:
        return JSONResponse(status_code=500, content= "An error occured" )
    
    return JSONResponse(status_code=201,content={"msg": "Poll created successfully", "polling_id": req["poll_id"]})


@app.get("/polls")
def get_all_polls():
    data = response_parser(collection.find())
    
    return JSONResponse(data)


@app.put("/update_poll")
def changing_poll(req: update_poll_details):
    req = req.dict()
    res = collection.find_one({"poll_id": req["poll_id"]})
    if res is None:
        return JSONResponse(status_code=404, detail="Poll-Id not found")
    if len(req["options"]) != len(req["response"]):
        return JSONResponse(status_code=400, content={"msg": "Each poll option must have a response count"})
    else:
        collection.update_one({"poll_id":req["poll_id"]}, {"$set":req})
    
    return JSONResponse(status_code=200,content={"msg": "Event updated successfully"})
        

@app.delete("/delete_poll/{poll_id}")
def deleting_poll(poll_id: str):
    res = collection.find_one({"poll_id":poll_id})
    if res is None:
        return JSONResponse(status_code=404, content={"msg":"Poll not found"})
    else:
        collection.delete_one({"poll_id":poll_id})

    return JSONResponse(status_code=200, content={"msg": "Poll deleted successfully"})


@app.get("/polls/{poll_id}",response_class = HTMLResponse)
def get_poll(req: Request, poll_id: str):
    res = collection.find_one({"poll_id": poll_id})
    if res is None:
        return JSONResponse(status_code=404, content={"msg":"Poll not found"})
    if res:
        res["_id"] = str(res["_id"])
    if templates is None:
        return JSONResponse(status_code=500, content={
            "msg": "jinja2 not available. Install with `python -m pip install Jinja2` and run via `uvicorn main:app --reload`."
        })

    return templates.TemplateResponse("index.html", {"request": req, "details": res})


@app.post("/submit")
async def submitResponse(req: update_poll_details):
    req = req.dict()
    pollOption = req["pollOption"];
    res = collection.find_one({"poll_id": req["poll_id"]})
    if res is None:
        return JSONResponse(status_code=404, detail="Poll-Id not found")
    elif not (0 <= pollOption < len(res["options"])):
        return JSONResponse(status_code=400, content={"msg": "Poll-Option not found"})
    elif len(res["options"]) != len(res["response"]):
        return JSONResponse(status_code=400, content={"msg": "Poll options and response counts are inconsistent"})
    else:
        req = res
        req["response"][pollOption]+=1
        collection.update_one({"poll_id":req["poll_id"]}, {"$set":req})
    
    return JSONResponse(status_code=200, content={"msg": "Event updated successfully"})


@app.get("/poll/result/{poll_id}",response_class = HTMLResponse)
def get_poll(req: Request, poll_id: str):
    res = collection.find_one({"poll_id": poll_id})
    if res is None:
        return JSONResponse(status_code=404, content={"msg":"Poll not found"})

    res["_id"] = str(res["_id"])
    
    total_count = sum(res["response"])
    for i in range(len(res["response"])):
        if(total_count >0):
            res["response"][i] = (res["response"][i] / total_count) * 100
    if templates is None:
        return JSONResponse(status_code=500, content={
            "msg": "jinja2 not available. Install with `python -m pip install Jinja2` and run via `uvicorn main:app --reload`."
        })

    return templates.TemplateResponse("result.html", {"request": req, "details": res, "totalCount": total_count})
