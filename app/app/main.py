from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI(
    title="PATHFORGE AI",
    description="Your AI Career Transition Companion",
    version="1.0.0"
)

app.mount(
    "/static",
    StaticFiles(directory="app/static"),
    name="static"
)

templates = Jinja2Templates(
    directory="app/templates"
)


@app.get("/")
def home():
    return {
        "project": "PATHFORGE AI",
        "message": "Welcome to PATHFORGE AI!"
    }


@app.get("/health")
def health():
    return {
        "status": "success",
        "message": "Backend is running successfully"
    }