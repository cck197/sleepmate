# Workout

The collection of records in this page.

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **int** | Unique identifier for the workout activity | 
**user_id** | **int** | The WHOOP User who performed the workout | 
**created_at** | **datetime** | The time the workout activity was recorded in WHOOP | 
**updated_at** | **datetime** | The time the workout activity was last updated in WHOOP | 
**start** | **datetime** | Start time bound of the workout | 
**end** | **datetime** | End time bound of the workout | 
**timezone_offset** | **str** | The user&#39;s timezone offset at the time the workout was recorded. Follows format for Time Zone Designator (TZD) - &#39;+hh:mm&#39;, &#39;-hh:mm&#39;, or &#39;Z&#39;. | 
**sport_id** | **int** | ID of the WHOOP Sport performed during the workout | 
**score_state** | **str** | &#x60;SCORED&#x60; means the workout activity was scored and the measurement values will be present. &#x60;PENDING_SCORE&#x60; means WHOOP is currently evaluating the workout activity. &#x60;UNSCORABLE&#x60; means this activity could not be scored for some reason - commonly because there is not enough user metric data for the time range. | 
**score** | [**WorkoutScore**](WorkoutScore.md) |  | [optional] 

## Example

```python
from whoop_client.models.workout import Workout

# TODO update the JSON string below
json = "{}"
# create an instance of Workout from a JSON string
workout_instance = Workout.from_json(json)
# print the JSON string representation of the object
print Workout.to_json()

# convert the object into a dict
workout_dict = workout_instance.to_dict()
# create an instance of Workout from a dict
workout_form_dict = workout.from_dict(workout_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


