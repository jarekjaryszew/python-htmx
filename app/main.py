from typing import Annotated

from fastapi import FastAPI, Request, Response, Form, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse, HTMLResponse

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

current_user = None
item_list = []


# Login Screen
@app.get("/login", response_class=templates.TemplateResponse)
def login(request: Request):
    return templates.TemplateResponse(request=request, name="login.html.jinja")


# Auth methods
class RequiresLoginException(Exception):
    pass


async def loggedInCookieRequired(request: Request):
    if request.cookies.get("LoggedIn") is None:
        # We need to throw an exception to trigger the exception handler
        # if we want to change the response in FastAPI
        raise RequiresLoginException()


@app.exception_handler(RequiresLoginException)
async def exception_handler(request: Request, exc: RequiresLoginException) -> Response:
    # We want to redirect an entire page, so we need to return a response
    # with the HX-Redirect header set
    # If we return redirect response, it will swap the hx-target with a redirect response
    resp = HTMLResponse(
        content="You need to be logged in to access this page", status_code=401
    )
    resp.headers["HX-Redirect"] = "/login"
    return resp


@app.post("/login")
async def login_user(
    username: Annotated[str, Form()], password: Annotated[str, Form()]
):
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
    return templates.TemplateResponse(request=request, name="home.html.jinja")


@app.get("/secured_home", response_class=templates.TemplateResponse)
async def home(request: Request, dependencies=Depends(loggedInCookieRequired)):
    return templates.TemplateResponse(request=request, name="home.html.jinja")


@app.get("/echo", response_class=HTMLResponse)
async def echo(shout: str = "Silence..."):
    return HTMLResponse(content=shout if shout else "Silence...", status_code=200)

# List example
@app.get("/list", response_class=templates.TemplateResponse)
async def list(request: Request):
    global item_list
    return templates.TemplateResponse(
        request=request, name="list.html.jinja", context={"item_list": item_list}
    )


@app.post("/item", response_class=templates.TemplateResponse)
async def add_item(request: Request, item: Annotated[str, Form()]):
    global item_list
    item_list.append(item)
    return templates.TemplateResponse(
        request=request, name="item_list.html.jinja", context={"item_list": item_list}
    )


@app.delete("/item/{item_id}", response_class=templates.TemplateResponse)
async def delete_item(request: Request, item_id: int):
    global item_list
    del item_list[item_id - 1]
    return templates.TemplateResponse(
        request=request, name="item_list.html.jinja", context={"item_list": item_list}
    )
