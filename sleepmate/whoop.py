import logging
from datetime import datetime
from urllib.parse import urlparse

from authlib.integrations.requests_client import OAuth2Session
from langchain.pydantic_v1 import BaseModel, Field
from mongoengine import ReferenceField
from whoop_client import ApiClient, Configuration, UserApi

from .bmi import DBBodyMeasures
from .config import (
    WHOOP_CLIENT_ID,
    WHOOP_CLIENT_SECRET,
    WHOOP_REDIRECT_URI,
    WHOOP_SCOPE,
)
from .structured import pydantic_to_mongoengine
from .user import DBUser

parsed_url = urlparse(Configuration().host)
base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
WHOOP_AUTH_URL = f"{base_url}/oauth/oauth2/auth"
WHOOP_TOKEN_URL = f"{base_url}/oauth/oauth2/token"

log = logging.getLogger(__name__)


class WhoopToken(BaseModel):
    state: str = Field(description="state")
    access_token: str = Field(description="access token", default=None)
    expires_in: int = Field(description="expires in", default=None)
    refresh_token: str = Field(description="refresh token", default=None)
    scope: str = Field(description="scope", default=None)
    token_type: str = Field(description="token type", default=None)
    expires_at: int = Field(description="expires at", default=None)


DBWhoopToken = pydantic_to_mongoengine(
    WhoopToken, extra_fields={"user": ReferenceField(DBUser, required=True)}
)


def get_whoop_token(**kwargs) -> DBWhoopToken:
    """Returns the WHOOP token by given kwargs."""
    db_token = DBWhoopToken.objects(**kwargs).order_by("-id").first()
    if db_token:
        return db_token
    return DBWhoopToken(**kwargs)


def get_whoop_oauth2_session():
    assert WHOOP_CLIENT_ID, "WHOOP_CLIENT_ID is required"
    assert WHOOP_CLIENT_SECRET, "WHOOP_CLIENT_SECRET is required"
    assert WHOOP_REDIRECT_URI, "WHOOP_REDIRECT_URI is required"
    return OAuth2Session(
        WHOOP_CLIENT_ID,
        WHOOP_CLIENT_SECRET,
        scope=WHOOP_SCOPE,
        redirect_uri=WHOOP_REDIRECT_URI,
        token_endpoint_auth_method="client_secret_post",
    )


def get_whoop_auth_url(db_user_id: str):
    authorization_url, state = get_whoop_oauth2_session().create_authorization_url(
        WHOOP_AUTH_URL
    )
    db_token = get_whoop_token(user=db_user_id)
    db_token.state = state
    db_token.save()
    return authorization_url


def get_whoop_api_client(db_user_id: str):
    db_token = get_whoop_token(user=db_user_id)
    if not db_token.access_token:
        return None
    return ApiClient(Configuration(access_token=db_token.access_token))


def get_whoop_body_measures(db_user_id: str) -> DBBodyMeasures:
    api_response = UserApi(get_whoop_api_client(db_user_id)).get_body_measurement()
    return DBBodyMeasures(
        **{
            "user": db_user_id,
            "date": datetime.now(),
            "height": api_response.height_meter,
            "weight": api_response.weight_kilogram,
        }
    )
