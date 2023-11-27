# RecoveryScore

WHOOP's measurements and evaluation of the recovery. Only present if the Recovery State is `SCORED`

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**user_calibrating** | **bool** | True if the user is still calibrating and not enough data is available in WHOOP to provide an accurate recovery. | 
**recovery_score** | **float** | Percentage (0-100%) that reflects how well prepared the user&#39;s body is to take on Strain. The Recovery score is a measure of the user body&#39;s \&quot;return to baseline\&quot; after a stressor. | 
**resting_heart_rate** | **float** | The user&#39;s resting heart rate. | 
**hrv_rmssd_milli** | **float** | The user&#39;s Heart Rate Variability measured using Root Mean Square of Successive Differences (RMSSD), in milliseconds. | 
**spo2_percentage** | **float** | The percentage of oxygen in the user&#39;s blood. Only present if the user is on 4.0 or greater. | [optional] 
**skin_temp_celsius** | **float** | The user&#39;s skin temperature, in Celsius. Only present if the user is on 4.0 or greater. | [optional] 

## Example

```python
from whoop_client.models.recovery_score import RecoveryScore

# TODO update the JSON string below
json = "{}"
# create an instance of RecoveryScore from a JSON string
recovery_score_instance = RecoveryScore.from_json(json)
# print the JSON string representation of the object
print RecoveryScore.to_json()

# convert the object into a dict
recovery_score_dict = recovery_score_instance.to_dict()
# create an instance of RecoveryScore from a dict
recovery_score_form_dict = recovery_score.from_dict(recovery_score_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


