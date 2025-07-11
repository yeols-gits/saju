from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import api.saju as saju
import datetime 

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:33900"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "FastAPI backend 연결 성공!"}

@app.get("/saju")
def read_saju():
    result = {
        "day": saju.days_calc(1995, 1, 19),
        "month": saju.months_calc(1995, 1, 19, 4, 44),
        "year": saju.years_calc(1995, 1, 19, 4, 44),
        "time": saju.times_calc(1995, 1, 19, 4, 44)
    }
    return result