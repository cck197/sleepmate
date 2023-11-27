# PaginatedCycleResponse


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**records** | [**List[Cycle]**](Cycle.md) | The collection of records in this page. | [optional] 
**next_token** | **str** | A token that can be used on the next request to access the next page of records. If the token is not present, there are no more records in the collection. | [optional] 

## Example

```python
from whoop_client.models.paginated_cycle_response import PaginatedCycleResponse

# TODO update the JSON string below
json = "{}"
# create an instance of PaginatedCycleResponse from a JSON string
paginated_cycle_response_instance = PaginatedCycleResponse.from_json(json)
# print the JSON string representation of the object
print PaginatedCycleResponse.to_json()

# convert the object into a dict
paginated_cycle_response_dict = paginated_cycle_response_instance.to_dict()
# create an instance of PaginatedCycleResponse from a dict
paginated_cycle_response_form_dict = paginated_cycle_response.from_dict(paginated_cycle_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


