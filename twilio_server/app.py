import logging

from dotenv import load_dotenv
from flask import Flask, request

from twilio.rest import Client

load_dotenv()

from sleepmate.config import TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_NUMBER
from sleepmate.executor import X
from sleepmate.helpful_scripts import setup_logging
from sleepmate.user import get_user_from_username

app = Flask(__name__)

setup_logging()

log = logging.getLogger("twilio.bot")

log.info(f"starting twilio bot {TWILIO_ACCOUNT_SID=} {TWILIO_NUMBER=}")

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)


def get_db_user():
    return get_user_from_username(
        username=request.form["From"], name=request.form["ProfileName"], create=True
    )


@app.route("/twilio_status", methods=["POST"])
def twilio_status():
    log.info(f"received status {request.form=}")
    return "Success!", 200


@app.route("/twilio", methods=["POST"])
def twilio():
    log.info(f"received webhook {request.form=}")
    db_user = get_db_user()
    log.info(f"{db_user.to_mongo()=}")
    x = X(username=db_user.username, hello=None, log_=log, display=False)
    try:
        reply_content = x.run(request.form["Body"])
    except Exception as e:
        log.exception(f"{e}")
        reply_content = (
            "Whoops, I had a problem answering that question. Try again later."
        )
    message = client.messages.create(
        from_=TWILIO_NUMBER, body=reply_content, to=request.form["From"]
    )
    log.info(f"sent message {message=}")

    return "Success!", 200
