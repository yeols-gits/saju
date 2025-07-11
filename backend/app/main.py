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
    return saju.get_ipchun_datetime(1995)