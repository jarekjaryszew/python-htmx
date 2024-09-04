from typing import Annotated

from fastapi import FastAPI, Request, Response, Form, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse, HTMLResponse

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

current_user = None


# Login Screen
@app.get("/login", response_class=templates.TemplateResponse)
def login(request: Request):
    return templates.TemplateResponse(request=request, name="login.html.jinja")


# Auth methods
class RequiresLoginException(Exception):
    pass

async def loggedInCookieRequired(request: Request):
    if request.cookies.get("LoggedIn") is None:
        raise RequiresLoginException()

@app.exception_handler(RequiresLoginException)
async def exception_handler(request: Request, exc: RequiresLoginException) -> Response:
    resp = RedirectResponse(url='/login', status_code=200)
    resp.headers["HX-Redirect"] = "/login"
    return resp

@app.post("/login")
async  def login_user(username: Annotated[str, Form()], password: Annotated[str, Form()]):
    global current_user
    current_user = username
    response = RedirectResponse(url="/", status_code=303)
    response.set_cookie(key="LoggedIn", value=True, secure=True, httponly=True)

    return response


@app.post("/logout")
async def logout_user():
    global current_user
    current_user = None
    response = RedirectResponse(url="/", status_code=303)
    response.delete_cookie("LoggedIn")
    return response

# Home Screen
@app.get("/", response_class=templates.TemplateResponse)
async def read_root(request: Request):
    global current_user
    return templates.TemplateResponse(
        request=request, name="index.html.jinja", context={"current_user": current_user}
    )


@app.get("/home", response_class=templates.TemplateResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        request=request, name="home.html.jinja", context={"current_user": current_user}
    )

@app.get("/secured_home", response_class=templates.TemplateResponse)
async def home(request: Request, dependencies=Depends(loggedInCookieRequired)):
    return templates.TemplateResponse(
        request=request, name="home.html.jinja", context={"current_user": current_user}
    )

@app.get("/echo", response_class=HTMLResponse)
async def echo(request: Request, shout : str = "Silence..."):
    return HTMLResponse(content=shout if shout else "Silence...", status_code=200)
