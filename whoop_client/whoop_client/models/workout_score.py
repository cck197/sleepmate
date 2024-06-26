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


from typing import Any, ClassVar, Dict, List, Optional, Union
from pydantic import BaseModel, StrictFloat, StrictInt
from pydantic import Field
from whoop_client.models.zone_duration import ZoneDuration
try:
    from typing import Self
except ImportError:
    from typing_extensions import Self

class WorkoutScore(BaseModel):
    """
    WHOOP's measurements and evaluation of the workout activity. Only present if the Workout State is `SCORED`
    """ # noqa: E501
    strain: Union[StrictFloat, StrictInt] = Field(description="WHOOP metric of the cardiovascular load - the level of strain the workout had on the user's cardiovascular system based on the user's heart rate. Strain is scored on a scale from 0 to 21.")
    average_heart_rate: StrictInt = Field(description="The user's average heart rate (beats per minute) during the workout.")
    max_heart_rate: StrictInt = Field(description="The user's max heart rate (beats per minute) during the workout.")
    kilojoule: Union[StrictFloat, StrictInt] = Field(description="Kilojoules the user expended during the workout.")
    percent_recorded: Union[StrictFloat, StrictInt] = Field(description="Percentage (0-100%) of heart rate data WHOOP received during the workout.")
    distance_meter: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="The distance the user travelled during the workout. Only present if distance data sent to WHOOP")
    altitude_gain_meter: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="The altitude gained during the workout. This measurement does not account for downward travel - it is strictly a measure of altitude climbed. If a member climbed up and down a 1,000 meter mountain, ending at the same altitude, this measurement would be 1,000 meters. Only present if altitude data is included as part of the workout")
    altitude_change_meter: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="The altitude difference between the start and end points of the workout. If a member climbed up and down a mountain, ending at the same altitude, this measurement would be 0. Only present if altitude data is included as part of the workout")
    zone_duration: ZoneDuration
    __properties: ClassVar[List[str]] = ["strain", "average_heart_rate", "max_heart_rate", "kilojoule", "percent_recorded", "distance_meter", "altitude_gain_meter", "altitude_change_meter", "zone_duration"]

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
        """Create an instance of WorkoutScore from a JSON string"""
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
        # override the default output from pydantic by calling `to_dict()` of zone_duration
        if self.zone_duration:
            _dict['zone_duration'] = self.zone_duration.to_dict()
        return _dict

    @classmethod
    def from_dict(cls, obj: Dict) -> Self:
        """Create an instance of WorkoutScore from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "strain": obj.get("strain"),
            "average_heart_rate": obj.get("average_heart_rate"),
            "max_heart_rate": obj.get("max_heart_rate"),
            "kilojoule": obj.get("kilojoule"),
            "percent_recorded": obj.get("percent_recorded"),
            "distance_meter": obj.get("distance_meter"),
            "altitude_gain_meter": obj.get("altitude_gain_meter"),
            "altitude_change_meter": obj.get("altitude_change_meter"),
            "zone_duration": ZoneDuration.from_dict(obj.get("zone_duration")) if obj.get("zone_duration") is not None else None
        })
        return _obj


