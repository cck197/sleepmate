# Cycle

The collection of records in this page.

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **int** | Unique identifier for the physiological cycle | 
**user_id** | **int** | The WHOOP User for the physiological cycle | 
**created_at** | **datetime** | The time the cycle was recorded in WHOOP | 
**updated_at** | **datetime** | The time the cycle was last updated in WHOOP | 
**start** | **datetime** | Start time bound of the cycle | 
**end** | **datetime** | End time bound of the cycle. If not present, the user is currently in this cycle | [optional] 
**timezone_offset** | **str** | The user&#39;s timezone offset at the time the cycle was recorded. Follows format for Time Zone Designator (TZD) - &#39;+hh:mm&#39;, &#39;-hh:mm&#39;, or &#39;Z&#39;. | 
**score_state** | **str** | &#x60;SCORED&#x60; means the cycle was scored and the measurement values will be present. &#x60;PENDING_SCORE&#x60; means WHOOP is currently evaluating the cycle. &#x60;UNSCORABLE&#x60; means this activity could not be scored for some reason - commonly because there is not enough user metric data for the time range. | 
**score** | [**CycleScore**](CycleScore.md) |  | [optional] 

## Example

```python
from whoop_client.models.cycle import Cycle

# TODO update the JSON string below
json = "{}"
# create an instance of Cycle from a JSON string
cycle_instance = Cycle.from_json(json)
# print the JSON string representation of the object
print Cycle.to_json()

# convert the object into a dict
cycle_dict = cycle_instance.to_dict()
# create an instance of Cycle from a dict
cycle_form_dict = cycle.from_dict(cycle_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


