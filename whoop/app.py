import logging

from dotenv import load_dotenv
from flask import Flask, request

from sleepmate.db import *
from sleepmate.helpful_scripts import setup_logging
from sleepmate.whoop import WHOOP_TOKEN_URL, get_whoop_oauth2_session, get_whoop_token

load_dotenv()

app = Flask(__name__)

setup_logging()

log = logging.getLogger("whoop.app")


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
    return "Authenticated", 200
