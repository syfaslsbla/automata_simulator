from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
import uvicorn
import os

from api.routes import dfa, regex_nfa, minimize, equivalence

import webbrowser
import threading

app = FastAPI(title="Automata Simulator API")

@app.on_event("startup")
def on_startup():
    def open_browser():
        webbrowser.open("http://127.0.0.1:8000")
    # Wait 1.5 seconds for the server to bind the port before launching the browser
    threading.Timer(1.5, open_browser).start()

# Ensure static and templates dirs exist
os.makedirs("static/css", exist_ok=True)
os.makedirs("static/js", exist_ok=True)
os.makedirs("templates", exist_ok=True)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

app.include_router(dfa.router)
app.include_router(regex_nfa.router)
app.include_router(minimize.router)
app.include_router(equivalence.router)

@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
