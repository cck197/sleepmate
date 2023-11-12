# SleepScore

WHOOP's measurements and evaluation of the sleep activity. Only present if the Sleep State is `SCORED`

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**stage_summary** | [**SleepStageSummary**](SleepStageSummary.md) |  | 
**sleep_needed** | [**SleepNeeded**](SleepNeeded.md) |  | 
**respiratory_rate** | **float** | The user&#39;s respiratory rate during the sleep. | [optional] 
**sleep_performance_percentage** | **float** | A percentage (0-100%) of the time a user is asleep over the amount of sleep the user needed. May not be reported if WHOOP does not have enough data about a user yet to calculate Sleep Need. | [optional] 
**sleep_consistency_percentage** | **float** | Percentage (0-100%) of how similar this sleep and wake times compared to the previous day. May not be reported if WHOOP does not have enough sleep data about a user yet to understand consistency. | [optional] 
**sleep_efficiency_percentage** | **float** | A percentage (0-100%) of the time you spend in bed that you are actually asleep. | [optional] 

## Example

```python
from whoop_client.models.sleep_score import SleepScore

# TODO update the JSON string below
json = "{}"
# create an instance of SleepScore from a JSON string
sleep_score_instance = SleepScore.from_json(json)
# print the JSON string representation of the object
print SleepScore.to_json()

# convert the object into a dict
sleep_score_dict = sleep_score_instance.to_dict()
# create an instance of SleepScore from a dict
sleep_score_form_dict = sleep_score.from_dict(sleep_score_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


