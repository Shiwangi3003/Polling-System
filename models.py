from pydantic import BaseModel

class poll_details(BaseModel):
    poll_id: str=""
    question: str
    options: list
    response: list=[]

class update_poll_details(BaseModel):
    poll_id: str
    question: str=""
    options: list=[]
    response: list=[]
    pollOption: int
