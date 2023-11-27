# Recovery


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**cycle_id** | **int** | The Recovery represents how recovered the user is for this physiological cycle | 
**sleep_id** | **int** | ID of the Sleep associated with the Recovery | 
**user_id** | **int** | The WHOOP User for the recovery | 
**created_at** | **datetime** | The time the recovery was recorded in WHOOP | 
**updated_at** | **datetime** | The time the recovery was last updated in WHOOP | 
**score_state** | **str** | &#x60;SCORED&#x60; means the recovery was scored and the measurement values will be present. &#x60;PENDING_SCORE&#x60; means WHOOP is currently evaluating the cycle. &#x60;UNSCORABLE&#x60; means this activity could not be scored for some reason - commonly because there is not enough user metric data for the time range. | 
**score** | [**RecoveryScore**](RecoveryScore.md) |  | [optional] 

## Example

```python
from whoop_client.models.recovery import Recovery

# TODO update the JSON string below
json = "{}"
# create an instance of Recovery from a JSON string
recovery_instance = Recovery.from_json(json)
# print the JSON string representation of the object
print Recovery.to_json()

# convert the object into a dict
recovery_dict = recovery_instance.to_dict()
# create an instance of Recovery from a dict
recovery_form_dict = recovery.from_dict(recovery_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


