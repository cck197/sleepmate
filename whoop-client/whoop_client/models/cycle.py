# coding: utf-8

"""
    WHOOP API

    No description provided (generated by Openapi Generator https://github.com/openapitools/openapi-generator)

    The version of the OpenAPI document: 1.0.0
    Generated by OpenAPI Generator (https://openapi-generator.tech)

    Do not edit the class manually.
"""  # noqa: E501


from __future__ import annotations
import pprint
import re  # noqa: F401
import json

from datetime import datetime
from typing import Any, ClassVar, Dict, List, Optional
from pydantic import BaseModel, StrictInt, StrictStr, field_validator
from pydantic import Field
from whoop_client.models.cycle_score import CycleScore
try:
    from typing import Self
except ImportError:
    from typing_extensions import Self

class Cycle(BaseModel):
    """
    The collection of records in this page.
    """ # noqa: E501
    id: StrictInt = Field(description="Unique identifier for the physiological cycle")
    user_id: StrictInt = Field(description="The WHOOP User for the physiological cycle")
    created_at: datetime = Field(description="The time the cycle was recorded in WHOOP")
    updated_at: datetime = Field(description="The time the cycle was last updated in WHOOP")
    start: datetime = Field(description="Start time bound of the cycle")
    end: Optional[datetime] = Field(default=None, description="End time bound of the cycle. If not present, the user is currently in this cycle")
    timezone_offset: StrictStr = Field(description="The user's timezone offset at the time the cycle was recorded. Follows format for Time Zone Designator (TZD) - '+hh:mm', '-hh:mm', or 'Z'.")
    score_state: StrictStr = Field(description="`SCORED` means the cycle was scored and the measurement values will be present. `PENDING_SCORE` means WHOOP is currently evaluating the cycle. `UNSCORABLE` means this activity could not be scored for some reason - commonly because there is not enough user metric data for the time range.")
    score: Optional[CycleScore] = None
    __properties: ClassVar[List[str]] = ["id", "user_id", "created_at", "updated_at", "start", "end", "timezone_offset", "score_state", "score"]

    @field_validator('score_state')
    def score_state_validate_enum(cls, value):
        """Validates the enum"""
        if value not in ('SCORED', 'PENDING_SCORE', 'UNSCORABLE'):
            raise ValueError("must be one of enum values ('SCORED', 'PENDING_SCORE', 'UNSCORABLE')")
        return value

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True
    }


    def to_str(self) -> str:
        """Returns the string representation of the model using alias"""
        return pprint.pformat(self.model_dump(by_alias=True))

    def to_json(self) -> str:
        """Returns the JSON representation of the model using alias"""
        # TODO: pydantic v2: use .model_dump_json(by_alias=True, exclude_unset=True) instead
        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, json_str: str) -> Self:
        """Create an instance of Cycle from a JSON string"""
        return cls.from_dict(json.loads(json_str))

    def to_dict(self) -> Dict[str, Any]:
        """Return the dictionary representation of the model using alias.

        This has the following differences from calling pydantic's
        `self.model_dump(by_alias=True)`:

        * `None` is only added to the output dict for nullable fields that
          were set at model initialization. Other fields with value `None`
          are ignored.
        """
        _dict = self.model_dump(
            by_alias=True,
            exclude={
            },
            exclude_none=True,
        )
        # override the default output from pydantic by calling `to_dict()` of score
        if self.score:
            _dict['score'] = self.score.to_dict()
        return _dict

    @classmethod
    def from_dict(cls, obj: Dict) -> Self:
        """Create an instance of Cycle from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "id": obj.get("id"),
            "user_id": obj.get("user_id"),
            "created_at": obj.get("created_at"),
            "updated_at": obj.get("updated_at"),
            "start": obj.get("start"),
            "end": obj.get("end"),
            "timezone_offset": obj.get("timezone_offset"),
            "score_state": obj.get("score_state"),
            "score": CycleScore.from_dict(obj.get("score")) if obj.get("score") is not None else None
        })
        return _obj


