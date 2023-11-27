# UserBodyMeasurement


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**height_meter** | **float** | User&#39;s height in meters | 
**weight_kilogram** | **float** | User&#39;s weight in kilograms | 
**max_heart_rate** | **int** | The max heart rate WHOOP calculated for the user | 

## Example

```python
from whoop_client.models.user_body_measurement import UserBodyMeasurement

# TODO update the JSON string below
json = "{}"
# create an instance of UserBodyMeasurement from a JSON string
user_body_measurement_instance = UserBodyMeasurement.from_json(json)
# print the JSON string representation of the object
print UserBodyMeasurement.to_json()

# convert the object into a dict
user_body_measurement_dict = user_body_measurement_instance.to_dict()
# create an instance of UserBodyMeasurement from a dict
user_body_measurement_form_dict = user_body_measurement.from_dict(user_body_measurement_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


