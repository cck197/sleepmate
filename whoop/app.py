import logging

from dotenv import load_dotenv
from flask import Flask, request

from sleepmate.db import *
from sleepmate.helpful_scripts import setup_logging
from sleepmate.whoop import (
    WHOOP_CLIENT_ID,
    WHOOP_TOKEN_URL,
    get_whoop_oauth2_session,
    get_whoop_token,
)

load_dotenv()

app = Flask(__name__)

setup_logging()

log = logging.getLogger("whoop.app")

log.info(f"starting WHOOP server {WHOOP_CLIENT_ID=}")


def log_request():
    headers = "\n".join(f"{k}: {v}" for k, v in request.headers.items())
    log_message = f"Request {request.method} {request.url}\nHeaders:\n{headers}"

    if request.method == "POST":
        if request.json:
            post_data = request.json
            log_message += f"\nJSON POST Data: {post_data}"
        elif request.form:
            post_data = request.form
            log_message += f"\nForm POST Data: {post_data}"

    log.info(log_message)


@app.before_request
def before_request():
    log_request()


@app.route("/whoop_update", methods=["POST"])
def whoop_update():
    log.info(f"{request.form=}")
    return "Success!", 200


@app.route("/whoop_login", methods=["GET"])
def whoop_login():
    state = request.args.get("state")
    assert state, "state is required"
    token = get_whoop_oauth2_session().fetch_token(
        WHOOP_TOKEN_URL, authorization_response=request.url
    )
    log.info(f"{token=}")
    db_token = get_whoop_token(state=state)
    assert db_token, "token for state not found"
    db_token.update(**token)
    db_token.save()
    return "Success!", 200
