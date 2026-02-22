from fastapi import FastAPI, Request, Query
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.exceptions import RequestValidationError
from models import poll_details, update_poll_details
from uuid import uuid4
from configuration import collection
from fastapi.templating import Jinja2Templates
from bson import ObjectId
from datetime import datetime, timezone


def convert_mongo(obj):
    if isinstance(obj, ObjectId):
        return str(obj)
    if isinstance(obj, dict):
        return {k: convert_mongo(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [convert_mongo(v) for v in obj]
    return obj


def is_expired(poll: dict) -> bool:
    """Return True if the poll has an expiry date that has passed."""
    expires_at = poll.get("expires_at", "")
    if not expires_at:
        return False
    try:
        expiry = datetime.fromisoformat(expires_at)
        # Make expiry offset-aware if it isn't
        if expiry.tzinfo is None:
            expiry = expiry.replace(tzinfo=timezone.utc)
        return datetime.now(timezone.utc) > expiry
    except ValueError:
        return False


app = FastAPI()

try:
    templates = Jinja2Templates(directory="views")
except Exception as _e:
    templates = None
    print("Warning: jinja2 must be installed to use template endpoints.\nInstall with: python -m pip install Jinja2\nOr run the app with: uvicorn main:app --reload")


# ── Validation error handler ──────────────────────────────────────────────────
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = [{"field": e["loc"][-1], "msg": e["msg"]} for e in exc.errors()]
    return JSONResponse(status_code=422, content={"errors": errors})


# ── Home ──────────────────────────────────────────────────────────────────────
@app.get("/", response_class=HTMLResponse)
def home(req: Request, page: int = Query(1, ge=1), limit: int = Query(10, ge=1, le=100)):
    if templates is None:
        return JSONResponse(status_code=500, content={"msg": "jinja2 not available."})

    skip = (page - 1) * limit
    total = collection.count_documents({})
    data = list(collection.find().skip(skip).limit(limit))
    for item in data:
        item["_id"] = str(item["_id"])
        item["expired"] = is_expired(item)

    total_pages = max(1, -(-total // limit))  # ceiling division
    return templates.TemplateResponse("home.html", {
        "request": req,
        "polls": data,
        "page": page,
        "limit": limit,
        "total_pages": total_pages,
    })


# ── Create Poll ───────────────────────────────────────────────────────────────
@app.post("/create_poll")
def create_poll(req: poll_details):
    data = req.dict()
    data["poll_id"] = str(uuid4())
    # Initialize response counts to 0 for each option
    data["response"] = [0] * len(data["options"])

    if collection.find_one({"question": data["question"]}):
        return JSONResponse(status_code=409, content={"msg": "A poll with this question already exists"})

    collection.insert_one(data)
    return JSONResponse(status_code=201, content={"msg": "Poll created successfully", "poll_id": data["poll_id"]})


# ── Get All Polls (JSON, paginated) ───────────────────────────────────────────
@app.get("/polls")
def get_all_polls(page: int = Query(1, ge=1), limit: int = Query(10, ge=1, le=100)):
    skip = (page - 1) * limit
    total = collection.count_documents({})
    data = list(collection.find().skip(skip).limit(limit))
    for item in data:
        item["_id"] = str(item["_id"])
    return JSONResponse({"total": total, "page": page, "limit": limit, "polls": data})


# ── Get Single Poll (Voting Page) ─────────────────────────────────────────────
@app.get("/polls/{poll_id}", response_class=HTMLResponse)
def get_poll(req: Request, poll_id: str):
    res = collection.find_one({"poll_id": poll_id})
    if res is None:
        return JSONResponse(status_code=404, content={"msg": "Poll not found"})
    res = convert_mongo(res)
    res["expired"] = is_expired(res)

    if templates is None:
        return JSONResponse(status_code=500, content={"msg": "jinja2 not available."})

    # Check if user already voted via cookie
    voted = req.cookies.get(f"voted_{poll_id}") == "1"
    return templates.TemplateResponse("index.html", {"request": req, "details": res, "already_voted": voted})


# ── Update Poll ───────────────────────────────────────────────────────────────
@app.put("/update_poll")
def update_poll(req: update_poll_details):
    data = req.dict()
    res = collection.find_one({"poll_id": data["poll_id"]})
    if res is None:
        return JSONResponse(status_code=404, content={"msg": "Poll not found"})
    collection.update_one({"poll_id": data["poll_id"]}, {"$set": data})
    return JSONResponse(status_code=200, content={"msg": "Poll updated successfully"})


# ── Delete Poll ───────────────────────────────────────────────────────────────
@app.delete("/delete_poll/{poll_id}")
def delete_poll(poll_id: str):
    res = collection.find_one({"poll_id": poll_id})
    if res is None:
        return JSONResponse(status_code=404, content={"msg": "Poll not found"})
    collection.delete_one({"poll_id": poll_id})
    return JSONResponse(status_code=200, content={"msg": "Poll deleted successfully"})


# ── Submit Vote ───────────────────────────────────────────────────────────────
@app.post("/submit")
async def submit_response(req: Request, body: update_poll_details):
    data = body.dict()
    poll_id = data["poll_id"]
    poll_option = data["pollOption"]

    # Duplicate vote check
    if req.cookies.get(f"voted_{poll_id}") == "1":
        return JSONResponse(status_code=403, content={"msg": "You have already voted on this poll"})

    res = collection.find_one({"poll_id": poll_id})
    if res is None:
        return JSONResponse(status_code=404, content={"msg": "Poll not found"})

    # Expiry check
    if is_expired(res):
        return JSONResponse(status_code=410, content={"msg": "This poll has expired"})

    # Bounds check
    if poll_option < 0 or poll_option >= len(res["response"]):
        return JSONResponse(status_code=400, content={"msg": "Invalid poll option index"})

    res["response"][poll_option] += 1
    collection.update_one({"poll_id": poll_id}, {"$set": {"response": res["response"]}})

    response = JSONResponse(status_code=200, content={"msg": "Vote submitted successfully"})
    # Set cookie so same browser can't vote again
    response.set_cookie(key=f"voted_{poll_id}", value="1", max_age=60 * 60 * 24 * 365, httponly=True, samesite="lax")
    return response


# ── Poll Results ──────────────────────────────────────────────────────────────
@app.get("/poll/result/{poll_id}", response_class=HTMLResponse)
def get_poll_result(req: Request, poll_id: str):
    res = collection.find_one({"poll_id": poll_id})
    if res is None:
        return JSONResponse(status_code=404, content={"msg": "Poll not found"})
    res = convert_mongo(res)
    res["expired"] = is_expired(res)

    total_count = sum(res["response"])
    percentages = [
        round((v / total_count) * 100, 1) if total_count > 0 else 0
        for v in res["response"]
    ]

    if templates is None:
        return JSONResponse(status_code=500, content={"msg": "jinja2 not available."})

    return templates.TemplateResponse("result.html", {
        "request": req,
        "details": res,
        "totalCount": total_count,
        "percentages": percentages,
    })
