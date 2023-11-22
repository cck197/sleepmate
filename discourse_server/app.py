import logging

from dotenv import load_dotenv
from flask import Flask, jsonify, request
from pydiscourse import DiscourseClient

load_dotenv()

from sleepmate.config import DISCOURSE_API_KEY, DISCOURSE_BASE_URL, DISCOURSE_USERNAME
from sleepmate.executor import X
from sleepmate.helpful_scripts import setup_logging
from sleepmate.user import get_user_from_username

app = Flask(__name__)

setup_logging()

log = logging.getLogger("discourse.bot")

log.info(f"starting discourse bot {DISCOURSE_BASE_URL=} {DISCOURSE_USERNAME=}")


def get_discourse_client():
    return DiscourseClient(
        DISCOURSE_BASE_URL,
        api_key=DISCOURSE_API_KEY,
        api_username=DISCOURSE_USERNAME,
    )


def get_db_user(post):
    return get_user_from_username(
        username=post["username"], name=post["name"], create=True
    )


def get_utterance(content):
    """Remove the username from the content"""
    return content.replace(f"@{DISCOURSE_USERNAME}", "").strip()


def was_tagged(content):
    return f"@{DISCOURSE_USERNAME.lower()}" in content


@app.route("/discourse", methods=["POST"])
def discourse():
    data = request.get_json()
    log.info(f"received webhook {data=}")

    post = data.get("post", {})
    content = post.get("raw", "")

    # print(f"{content=}")

    reply_to_user = post.get("reply_to_user", {}).get("username")

    if was_tagged(content) or (reply_to_user == DISCOURSE_USERNAME):
        db_user = get_db_user(post)
        log.info(f"{db_user.to_mongo()=}")
        x = X(username=db_user.username, hello=None, log_=log, display=False)
        # The specific user has been mentioned (tagged) in the post
        topic_id = post.get("topic_id")
        post_number = post.get("post_number")
        try:
            reply_content = x.run(get_utterance(content))
        except Exception as e:
            log.exception(f"{e}")
            reply_content = (
                "Whoops, I had a problem answering that question. Try again later."
            )

        # print(f"{topic_id=}")
        discourse_client = get_discourse_client()
        r = discourse_client.create_post(
            reply_content, reply_to_post_number=post_number, topic_id=topic_id
        )
        log.info(f"{r=}")

    return jsonify({"status": "success"})
