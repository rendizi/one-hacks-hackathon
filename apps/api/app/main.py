from fastapi import FastAPI
from auth.router import router as auth_router
from followings.router import router as followings_router 
from summarizes.summarizer import summarize

summarize()

app = FastAPI()

app.include_router(auth_router, prefix="/auth")
app.include_router(followings_router, prefix="/followings")
