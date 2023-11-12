# WorkoutScore

WHOOP's measurements and evaluation of the workout activity. Only present if the Workout State is `SCORED`

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**strain** | **float** | WHOOP metric of the cardiovascular load - the level of strain the workout had on the user&#39;s cardiovascular system based on the user&#39;s heart rate. Strain is scored on a scale from 0 to 21. | 
**average_heart_rate** | **int** | The user&#39;s average heart rate (beats per minute) during the workout. | 
**max_heart_rate** | **int** | The user&#39;s max heart rate (beats per minute) during the workout. | 
**kilojoule** | **float** | Kilojoules the user expended during the workout. | 
**percent_recorded** | **float** | Percentage (0-100%) of heart rate data WHOOP received during the workout. | 
**distance_meter** | **float** | The distance the user travelled during the workout. Only present if distance data sent to WHOOP | [optional] 
**altitude_gain_meter** | **float** | The altitude gained during the workout. This measurement does not account for downward travel - it is strictly a measure of altitude climbed. If a member climbed up and down a 1,000 meter mountain, ending at the same altitude, this measurement would be 1,000 meters. Only present if altitude data is included as part of the workout | [optional] 
**altitude_change_meter** | **float** | The altitude difference between the start and end points of the workout. If a member climbed up and down a mountain, ending at the same altitude, this measurement would be 0. Only present if altitude data is included as part of the workout | [optional] 
**zone_duration** | [**ZoneDuration**](ZoneDuration.md) |  | 

## Example

```python
from whoop_client.models.workout_score import WorkoutScore

# TODO update the JSON string below
json = "{}"
# create an instance of WorkoutScore from a JSON string
workout_score_instance = WorkoutScore.from_json(json)
# print the JSON string representation of the object
print WorkoutScore.to_json()

# convert the object into a dict
workout_score_dict = workout_score_instance.to_dict()
# create an instance of WorkoutScore from a dict
workout_score_form_dict = workout_score.from_dict(workout_score_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


