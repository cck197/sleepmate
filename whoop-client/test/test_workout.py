# coding: utf-8

"""
    WHOOP API

    No description provided (generated by Openapi Generator https://github.com/openapitools/openapi-generator)

    The version of the OpenAPI document: 1.0.0
    Generated by OpenAPI Generator (https://openapi-generator.tech)

    Do not edit the class manually.
"""  # noqa: E501


import unittest
import datetime

from whoop_client.models.workout import Workout

class TestWorkout(unittest.TestCase):
    """Workout unit test stubs"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def make_instance(self, include_optional) -> Workout:
        """Test Workout
            include_option is a boolean, when False only required
            params are included, when True both required and
            optional params are included """
        # uncomment below to create an instance of `Workout`
        """
        model = Workout()
        if include_optional:
            return Workout(
                id = 1043,
                user_id = 9012,
                created_at = '2022-04-24T11:25:44.774Z',
                updated_at = '2022-04-24T14:25:44.774Z',
                start = '2022-04-24T02:25:44.774Z',
                end = '2022-04-24T10:25:44.774Z',
                timezone_offset = '-05:00',
                sport_id = 1,
                score_state = 'SCORED',
                score = whoop_client.models.workout_score.WorkoutScore(
                    strain = 8.2463, 
                    average_heart_rate = 123, 
                    max_heart_rate = 146, 
                    kilojoule = 1569.34033203125, 
                    percent_recorded = 100.0, 
                    distance_meter = 1772.77035916, 
                    altitude_gain_meter = 46.64384460449, 
                    altitude_change_meter = -0.781372010707855, 
                    zone_duration = whoop_client.models.zone_duration.ZoneDuration(
                        zone_zero_milli = 13458, 
                        zone_one_milli = 389370, 
                        zone_two_milli = 388367, 
                        zone_three_milli = 71137, 
                        zone_four_milli = 0, 
                        zone_five_milli = 0, ), )
            )
        else:
            return Workout(
                id = 1043,
                user_id = 9012,
                created_at = '2022-04-24T11:25:44.774Z',
                updated_at = '2022-04-24T14:25:44.774Z',
                start = '2022-04-24T02:25:44.774Z',
                end = '2022-04-24T10:25:44.774Z',
                timezone_offset = '-05:00',
                sport_id = 1,
                score_state = 'SCORED',
        )
        """

    def testWorkout(self):
        """Test Workout"""
        # inst_req_only = self.make_instance(include_optional=False)
        # inst_req_and_optional = self.make_instance(include_optional=True)

if __name__ == '__main__':
    unittest.main()
