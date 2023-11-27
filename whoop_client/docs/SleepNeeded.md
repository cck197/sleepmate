# SleepNeeded

Breakdown of the amount of sleep a user needed before the sleep activity. Summing all individual components results in the amount of sleep the user needed prior to this sleep activity

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**baseline_milli** | **int** | The amount of sleep a user needed based on historical trends | 
**need_from_sleep_debt_milli** | **int** | The difference between the amount of sleep the user&#39;s body required and the amount the user actually got | 
**need_from_recent_strain_milli** | **int** | Additional sleep need accrued based on the user&#39;s strain | 
**need_from_recent_nap_milli** | **int** | Reduction in sleep need accrued based on the user&#39;s recent nap activity (negative value or zero) | 

## Example

```python
from whoop_client.models.sleep_needed import SleepNeeded

# TODO update the JSON string below
json = "{}"
# create an instance of SleepNeeded from a JSON string
sleep_needed_instance = SleepNeeded.from_json(json)
# print the JSON string representation of the object
print SleepNeeded.to_json()

# convert the object into a dict
sleep_needed_dict = sleep_needed_instance.to_dict()
# create an instance of SleepNeeded from a dict
sleep_needed_form_dict = sleep_needed.from_dict(sleep_needed_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


