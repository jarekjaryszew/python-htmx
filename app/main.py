from typing import Annotated
from time import sleep

from fastapi import FastAPI, Request, Response, Form, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse, HTMLResponse

from .plot import myplot

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Fake persistence
current_user = None
item_list = []


# Login Screen
@app.get("/login", response_class=HTMLResponse)
def login(request: Request):
    return templates.TemplateResponse(request=request, name="login.html.jinja")


# Auth methods
class RequiresLoginException(Exception):
    pass


async def loggedInCookieRequired(request: Request):
    global current_user
    if request.cookies.get("LoggedIn") is None or current_user is None:
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
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    global current_user
    return templates.TemplateResponse(
        request=request, name="index.html.jinja", context={"current_user": current_user}
    )


@app.get("/home", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(request=request, name="home.html.jinja")


@app.get("/secured_home", response_class=HTMLResponse)
async def home(request: Request, dependencies=Depends(loggedInCookieRequired)):
    return templates.TemplateResponse(request=request, name="home.html.jinja")


@app.get("/echo", response_class=HTMLResponse)
async def echo(shout: str):
    return HTMLResponse(content=shout if shout else "Silence...", status_code=200)


# List example
@app.get("/list", response_class=HTMLResponse)
async def list(request: Request):
    global item_list
    return templates.TemplateResponse(
        request=request, name="list.html.jinja", context={"item_list": item_list}
    )


@app.post("/item", response_class=HTMLResponse)
async def add_item(
    request: Request,
    item: Annotated[str, Form()],
    dependencies=Depends(loggedInCookieRequired),
):
    global item_list
    item_list.append(item)
    return templates.TemplateResponse(
        request=request, name="item_list.html.jinja", context={"item_list": item_list}
    )


@app.delete("/item/{item_id}", response_class=HTMLResponse)
async def delete_item(
    request: Request, item_id: int, dependencies=Depends(loggedInCookieRequired)
):
    global item_list
    del item_list[item_id - 1]
    return templates.TemplateResponse(
        request=request, name="item_list.html.jinja", context={"item_list": item_list}
    )


# Paging example with delay
@app.get("/paging", response_class=HTMLResponse)
async def list(request: Request):
    item_list = [f"Item {i}" for i in range(1, 11)]
    return templates.TemplateResponse(
        request=request, name="paging.html.jinja", context={"item_list": item_list}
    )


@app.get("/paging/{page}", response_class=HTMLResponse)
async def list(request: Request, page: int):
    sleep(1)
    offset = page * 10
    item_list = [f"Item {i}" for i in range(1 + offset, 11 + offset)]
    return templates.TemplateResponse(
        request=request, name="page.html.jinja", context={"item_list": item_list}
    )


# Plot example
@app.get("/plot", response_class=HTMLResponse)
async def plot(request: Request):
    plot = myplot(1, 1, 1, 2, 0, 0)
    return templates.TemplateResponse(
        request=request, name="plot.html.jinja", context={"plot": plot}
    )


@app.get("/plot_internal", response_class=HTMLResponse)
async def plot_internal(
    amp1: Annotated[float, Form] = 1,
    amp2: Annotated[float, Form] = 1,
    freq1: Annotated[float, Form] = 1,
    freq2: Annotated[float, Form] = 2,
    phase1: Annotated[float, Form] = 0,
    phase2: Annotated[float, Form] = 0,
):
    PRE = '<img id="plot-swap" src="data:image/png;base64, '
    POST = '">'
    return HTMLResponse(
        content=PRE
        + myplot(
            amp1=amp1, amp2=amp2, freq1=freq1, freq2=freq2, phase1=phase1, phase2=phase2
        )
        + POST,
        status_code=200,
    )
