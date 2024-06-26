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

from whoop_client.models.paginated_sleep_response import PaginatedSleepResponse

class TestPaginatedSleepResponse(unittest.TestCase):
    """PaginatedSleepResponse unit test stubs"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def make_instance(self, include_optional) -> PaginatedSleepResponse:
        """Test PaginatedSleepResponse
            include_option is a boolean, when False only required
            params are included, when True both required and
            optional params are included """
        # uncomment below to create an instance of `PaginatedSleepResponse`
        """
        model = PaginatedSleepResponse()
        if include_optional:
            return PaginatedSleepResponse(
                records = [
                    whoop_client.models.sleep.Sleep(
                        id = 93845, 
                        user_id = 10129, 
                        created_at = '2022-04-24T11:25:44.774Z', 
                        updated_at = '2022-04-24T14:25:44.774Z', 
                        start = '2022-04-24T02:25:44.774Z', 
                        end = '2022-04-24T10:25:44.774Z', 
                        timezone_offset = '-05:00', 
                        nap = False, 
                        score_state = 'SCORED', 
                        score = whoop_client.models.sleep_score.SleepScore(
                            stage_summary = whoop_client.models.sleep_stage_summary.SleepStageSummary(
                                total_in_bed_time_milli = 30272735, 
                                total_awake_time_milli = 1403507, 
                                total_no_data_time_milli = 0, 
                                total_light_sleep_time_milli = 14905851, 
                                total_slow_wave_sleep_time_milli = 6630370, 
                                total_rem_sleep_time_milli = 5879573, 
                                sleep_cycle_count = 3, 
                                disturbance_count = 12, ), 
                            sleep_needed = whoop_client.models.sleep_needed.SleepNeeded(
                                baseline_milli = 27395716, 
                                need_from_sleep_debt_milli = 352230, 
                                need_from_recent_strain_milli = 208595, 
                                need_from_recent_nap_milli = -12312, ), 
                            respiratory_rate = 16.11328125, 
                            sleep_performance_percentage = 98.0, 
                            sleep_consistency_percentage = 90.0, 
                            sleep_efficiency_percentage = 91.69533848, ), )
                    ],
                next_token = 'MTIzOjEyMzEyMw'
            )
        else:
            return PaginatedSleepResponse(
        )
        """

    def testPaginatedSleepResponse(self):
        """Test PaginatedSleepResponse"""
        # inst_req_only = self.make_instance(include_optional=False)
        # inst_req_and_optional = self.make_instance(include_optional=True)

if __name__ == '__main__':
    unittest.main()
