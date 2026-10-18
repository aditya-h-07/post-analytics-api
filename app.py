import os
from collections import defaultdict
from typing import List

from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="POST Analytics API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

API_KEY = os.environ.get("API_KEY", "")
EMAIL = "23f2004697@ds.study.iitm.ac.in"


class Event(BaseModel):
    user: str
    amount: float
    ts: int


class AnalyticsRequest(BaseModel):
    events: List[Event]


@app.post("/analytics")
def analytics(
    body: AnalyticsRequest,
    x_api_key: str = Header(default=None, alias="X-API-Key"),
):
    if not API_KEY or x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

    events = body.events
    positive_totals = defaultdict(float)
    users = set()
    revenue = 0.0

    for event in events:
        users.add(event.user)

        if event.amount > 0:
            revenue += event.amount
            positive_totals[event.user] += event.amount

    top_user = (
        max(positive_totals, key=positive_totals.get)
        if positive_totals
        else None
    )

    return {
        "email": EMAIL,
        "total_events": len(events),
        "unique_users": len(users),
        "revenue": round(revenue, 2),
        "top_user": top_user,
    }


@app.get("/healthz")
def healthz():
    return {"status": "ok"}
