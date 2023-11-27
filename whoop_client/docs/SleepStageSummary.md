# SleepStageSummary

Summary of the sleep stages

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**total_in_bed_time_milli** | **int** | Total time the user spent in bed, in milliseconds | 
**total_awake_time_milli** | **int** | Total time the user spent awake, in milliseconds | 
**total_no_data_time_milli** | **int** | Total time WHOOP did not receive data from the user during the sleep, in milliseconds | 
**total_light_sleep_time_milli** | **int** | Total time the user spent in light sleep, in milliseconds | 
**total_slow_wave_sleep_time_milli** | **int** | Total time the user spent in Slow Wave Sleep (SWS), in milliseconds | 
**total_rem_sleep_time_milli** | **int** | Total time the user spent in Rapid Eye Movement (REM) sleep, in milliseconds | 
**sleep_cycle_count** | **int** | Number of sleep cycles during the user&#39;s sleep | 
**disturbance_count** | **int** | Number of times the user was disturbed during sleep | 

## Example

```python
from whoop_client.models.sleep_stage_summary import SleepStageSummary

# TODO update the JSON string below
json = "{}"
# create an instance of SleepStageSummary from a JSON string
sleep_stage_summary_instance = SleepStageSummary.from_json(json)
# print the JSON string representation of the object
print SleepStageSummary.to_json()

# convert the object into a dict
sleep_stage_summary_dict = sleep_stage_summary_instance.to_dict()
# create an instance of SleepStageSummary from a dict
sleep_stage_summary_form_dict = sleep_stage_summary.from_dict(sleep_stage_summary_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


