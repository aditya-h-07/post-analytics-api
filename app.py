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

# Use the assigned key as the fallback if Render's API_KEY
# environment variable has not been configured.
ASSIGNED_API_KEY = "ak_qf956rousyn52mvhv2yvpqam"
API_KEY = os.environ.get("API_KEY", ASSIGNED_API_KEY).strip()

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
    if x_api_key is None or x_api_key != API_KEY:
        raise HTTPException(
            status_code=401,
            detail="Unauthorized",
        )

    positive_totals = defaultdict(float)
    unique_users = set()
    revenue = 0.0

    for event in body.events:
        unique_users.add(event.user)

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
        "total_events": len(body.events),
        "unique_users": len(unique_users),
        "revenue": round(revenue, 2),
        "top_user": top_user,
    }


@app.get("/healthz")
def healthz():
    return {"status": "ok"}
