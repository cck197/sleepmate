# Sleep

The collection of records in this page.

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **int** | Unique identifier for the sleep activity | 
**user_id** | **int** | The WHOOP User who performed the sleep activity | 
**created_at** | **datetime** | The time the sleep activity was recorded in WHOOP | 
**updated_at** | **datetime** | The time the sleep activity was last updated in WHOOP | 
**start** | **datetime** | Start time bound of the sleep | 
**end** | **datetime** | End time bound of the sleep | 
**timezone_offset** | **str** | The user&#39;s timezone offset at the time the sleep was recorded. Follows format for Time Zone Designator (TZD) - &#39;+hh:mm&#39;, &#39;-hh:mm&#39;, or &#39;Z&#39;. | 
**nap** | **bool** | If true, this sleep activity was a nap for the user | 
**score_state** | **str** | &#x60;SCORED&#x60; means the sleep activity was scored and the measurement values will be present. &#x60;PENDING_SCORE&#x60; means WHOOP is currently evaluating the sleep activity. &#x60;UNSCORABLE&#x60; means this activity could not be scored for some reason - commonly because there is not enough user metric data for the time range. | 
**score** | [**SleepScore**](SleepScore.md) |  | [optional] 

## Example

```python
from whoop_client.models.sleep import Sleep

# TODO update the JSON string below
json = "{}"
# create an instance of Sleep from a JSON string
sleep_instance = Sleep.from_json(json)
# print the JSON string representation of the object
print Sleep.to_json()

# convert the object into a dict
sleep_dict = sleep_instance.to_dict()
# create an instance of Sleep from a dict
sleep_form_dict = sleep.from_dict(sleep_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


