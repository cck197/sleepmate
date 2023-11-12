# PaginatedRecoveryResponse


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**records** | [**List[Recovery]**](Recovery.md) | The collection of records in this page. | [optional] 
**next_token** | **str** | A token that can be used on the next request to access the next page of records. If the token is not present, there are no more records in the collection. | [optional] 

## Example

```python
from whoop_client.models.paginated_recovery_response import PaginatedRecoveryResponse

# TODO update the JSON string below
json = "{}"
# create an instance of PaginatedRecoveryResponse from a JSON string
paginated_recovery_response_instance = PaginatedRecoveryResponse.from_json(json)
# print the JSON string representation of the object
print PaginatedRecoveryResponse.to_json()

# convert the object into a dict
paginated_recovery_response_dict = paginated_recovery_response_instance.to_dict()
# create an instance of PaginatedRecoveryResponse from a dict
paginated_recovery_response_form_dict = paginated_recovery_response.from_dict(paginated_recovery_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


