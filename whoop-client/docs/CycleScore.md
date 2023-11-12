# CycleScore

WHOOP's measurements and evaluation of the cycle. Only present if the score state is `SCORED`

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**strain** | **float** | WHOOP metric of the cardiovascular load - the level of strain  on the user&#39;s cardiovascular system based on the user&#39;s heart rate during the cycle. Strain is scored on a scale from 0 to 21. | 
**kilojoule** | **float** | Kilojoules the user expended during the cycle. | 
**average_heart_rate** | **int** | The user&#39;s average heart rate during the cycle. | 
**max_heart_rate** | **int** | The user&#39;s max heart rate during the cycle. | 

## Example

```python
from whoop_client.models.cycle_score import CycleScore

# TODO update the JSON string below
json = "{}"
# create an instance of CycleScore from a JSON string
cycle_score_instance = CycleScore.from_json(json)
# print the JSON string representation of the object
print CycleScore.to_json()

# convert the object into a dict
cycle_score_dict = cycle_score_instance.to_dict()
# create an instance of CycleScore from a dict
cycle_score_form_dict = cycle_score.from_dict(cycle_score_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


