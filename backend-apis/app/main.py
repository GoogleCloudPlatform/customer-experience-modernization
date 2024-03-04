# Copyright 2023 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
Main Fast API app for CSM
"""

import tomllib
import traceback

import google.cloud.logging
from fastapi import FastAPI
from fastapi.exception_handlers import (
    http_exception_handler,
    request_validation_exception_handler,
)
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.routers import (
    p1_customer,
    p2_content_creator,
    p4_customer_service_agent,
    p5_contact_center_analyst,
    p6_field_service_agent,
)

client = google.cloud.logging.Client()
client.setup_logging()


with open("app/config.toml", "rb") as f:
    config = tomllib.load(f)


app = FastAPI()
app.include_router(router=p1_customer.router)
app.include_router(router=p2_content_creator.router)
app.include_router(router=p4_customer_service_agent.router)
app.include_router(router=p5_contact_center_analyst.router)
app.include_router(router=p6_field_service_agent.router)

origins = [
    "http://localhost:5000",
    "http://localhost:8080",
    "https://csm-frontend-nightly.web.app",
]


app.add_middleware(
    middleware_class=CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
@app.get("/customer/{path}")
@app.get("/contact-center-analyst/{path}")
@app.get("/content-creator/{path}")
@app.get("/customer-experience-analyst/{path}")
@app.get("/customer-service-agent/{path}")
@app.get("/field-service-agent/{path}")
@app.get("/demo/{path}")
async def angular() -> FileResponse:
    """
    ## Angular app

    ### Returns:
    - Angular app index.html with the right route

    """
    return FileResponse("/static/index.html")


app.mount(
    path="/", app=StaticFiles(directory="/static", html=True), name="static"
)


@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request, exc):
    """

    Args:
        request ():
        exc ():

    Returns:

    """
    traceback.print_exc()
    return await http_exception_handler(request, exc)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    """

    Args:
        request ():
        exc ():

    Returns:

    """
    traceback.print_exc()
    return await request_validation_exception_handler(request, exc)
