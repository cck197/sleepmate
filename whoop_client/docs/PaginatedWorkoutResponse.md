# PaginatedWorkoutResponse


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**records** | [**List[Workout]**](Workout.md) | The collection of records in this page. | [optional] 
**next_token** | **str** | A token that can be used on the next request to access the next page of records. If the token is not present, there are no more records in the collection. | [optional] 

## Example

```python
from whoop_client.models.paginated_workout_response import PaginatedWorkoutResponse

# TODO update the JSON string below
json = "{}"
# create an instance of PaginatedWorkoutResponse from a JSON string
paginated_workout_response_instance = PaginatedWorkoutResponse.from_json(json)
# print the JSON string representation of the object
print PaginatedWorkoutResponse.to_json()

# convert the object into a dict
paginated_workout_response_dict = paginated_workout_response_instance.to_dict()
# create an instance of PaginatedWorkoutResponse from a dict
paginated_workout_response_form_dict = paginated_workout_response.from_dict(paginated_workout_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


