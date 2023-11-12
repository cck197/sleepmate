# UserBasicProfile


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**user_id** | **int** | The WHOOP User | 
**email** | **str** | User&#39;s Email | 
**first_name** | **str** | User&#39;s First Name | 
**last_name** | **str** | User&#39;s Last Name | 

## Example

```python
from whoop_client.models.user_basic_profile import UserBasicProfile

# TODO update the JSON string below
json = "{}"
# create an instance of UserBasicProfile from a JSON string
user_basic_profile_instance = UserBasicProfile.from_json(json)
# print the JSON string representation of the object
print UserBasicProfile.to_json()

# convert the object into a dict
user_basic_profile_dict = user_basic_profile_instance.to_dict()
# create an instance of UserBasicProfile from a dict
user_basic_profile_form_dict = user_basic_profile.from_dict(user_basic_profile_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


