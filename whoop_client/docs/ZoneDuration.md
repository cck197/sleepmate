# ZoneDuration

Breakdown of time spent in each heart rate zone during the workout.

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**zone_zero_milli** | **int** | Time spent with Heart Rate lower than Zone One [0-50%) | [optional] 
**zone_one_milli** | **int** | Time spent in Heart Rate Zone One [50-60%) | [optional] 
**zone_two_milli** | **int** | Time spent in Heart Rate Zone Two [60-70%) | [optional] 
**zone_three_milli** | **int** | Time spent in Heart Rate Zone Three [70-80%) | [optional] 
**zone_four_milli** | **int** | Time spent in Heart Rate Zone Four [80-90%) | [optional] 
**zone_five_milli** | **int** | Time spent in Heart Rate Zone Five [90-100%) | [optional] 

## Example

```python
from whoop_client.models.zone_duration import ZoneDuration

# TODO update the JSON string below
json = "{}"
# create an instance of ZoneDuration from a JSON string
zone_duration_instance = ZoneDuration.from_json(json)
# print the JSON string representation of the object
print ZoneDuration.to_json()

# convert the object into a dict
zone_duration_dict = zone_duration_instance.to_dict()
# create an instance of ZoneDuration from a dict
zone_duration_form_dict = zone_duration.from_dict(zone_duration_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


