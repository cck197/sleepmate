import base64
import hashlib
import hmac
import logging

from dotenv import load_dotenv
from flask import Flask, request

load_dotenv()

from sleepmate.db import *
from sleepmate.helpful_scripts import setup_logging
from sleepmate.whoop import (
    WHOOP_CLIENT_ID,
    WHOOP_CLIENT_SECRET,
    WHOOP_REDIRECT_URI,
    WHOOP_TOKEN_URL,
    get_user_by_whoop_id,
    get_whoop_oauth2_session,
    get_whoop_token,
    import_whoop_sleep_by_id,
)

app = Flask(__name__)

setup_logging()

log = logging.getLogger("whoop.app")

log.info(f"starting WHOOP server {WHOOP_CLIENT_ID=} {WHOOP_REDIRECT_URI=}")


def check_signature() -> bool:
    """Check the signature of the request to make sure it's from WHOOP."""
    # https://developer.whoop.com/docs/developing/webhooks/#webhooks-security
    timestamp_header = request.headers["X-Whoop-Signature-Timestamp"].encode()
    request_signature = request.headers["X-Whoop-Signature"]
    encoded_string = base64.b64encode(
        hmac.new(
            WHOOP_CLIENT_SECRET.encode(),
            timestamp_header + request.data,
            hashlib.sha256,
        ).digest()
    ).decode()
    ok = encoded_string == request_signature
    log.info(f"{encoded_string=} {request_signature=} {ok=}")
    return ok


@app.route("/whoop_update", methods=["POST"])
def whoop_update():
    if not check_signature():
        return "Invalid signature", 403
    data = request.json
    if data["type"] != "sleep.updated":
        log.info(f"ignoring {data=}")
        return "Success!", 200
    db_entry = import_whoop_sleep_by_id(
        get_user_by_whoop_id(data["user_id"]), int(data["id"])
    )
    db_entry.save()
    log.info(f"{db_entry.to_mongo()=}")
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
