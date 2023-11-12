# whoop_client.UserApi

All URIs are relative to *https://api.prod.whoop.com/developer*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_body_measurement**](UserApi.md#get_body_measurement) | **GET** /v1/user/measurement/body | 
[**get_profile_basic**](UserApi.md#get_profile_basic) | **GET** /v1/user/profile/basic | 
[**revoke_user_o_auth_access**](UserApi.md#revoke_user_o_auth_access) | **DELETE** /v1/user/access | 


# **get_body_measurement**
> UserBodyMeasurement get_body_measurement()



Get the user's body measurements

### Example

* OAuth Authentication (OAuth):
```python
import time
import os
import whoop_client
from whoop_client.models.user_body_measurement import UserBodyMeasurement
from whoop_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://api.prod.whoop.com/developer
# See configuration.py for a list of all supported configuration parameters.
configuration = whoop_client.Configuration(
    host = "https://api.prod.whoop.com/developer"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

configuration.access_token = os.environ["ACCESS_TOKEN"]

# Enter a context with an instance of the API client
with whoop_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = whoop_client.UserApi(api_client)

    try:
        api_response = api_instance.get_body_measurement()
        print("The response of UserApi->get_body_measurement:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling UserApi->get_body_measurement: %s\n" % e)
```



### Parameters
This endpoint does not need any parameter.

### Return type

[**UserBodyMeasurement**](UserBodyMeasurement.md)

### Authorization

[OAuth](../README.md#OAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful request |  -  |
**400** | Client error constructing the request |  -  |
**401** | Invalid authorization |  -  |
**429** | Request rejected due to rate limiting |  -  |
**500** | Server error occurred while making request |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_profile_basic**
> UserBasicProfile get_profile_basic()



Get the user's Basic Profile

### Example

* OAuth Authentication (OAuth):
```python
import time
import os
import whoop_client
from whoop_client.models.user_basic_profile import UserBasicProfile
from whoop_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://api.prod.whoop.com/developer
# See configuration.py for a list of all supported configuration parameters.
configuration = whoop_client.Configuration(
    host = "https://api.prod.whoop.com/developer"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

configuration.access_token = os.environ["ACCESS_TOKEN"]

# Enter a context with an instance of the API client
with whoop_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = whoop_client.UserApi(api_client)

    try:
        api_response = api_instance.get_profile_basic()
        print("The response of UserApi->get_profile_basic:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling UserApi->get_profile_basic: %s\n" % e)
```



### Parameters
This endpoint does not need any parameter.

### Return type

[**UserBasicProfile**](UserBasicProfile.md)

### Authorization

[OAuth](../README.md#OAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful request |  -  |
**400** | Client error constructing the request |  -  |
**401** | Invalid authorization |  -  |
**429** | Request rejected due to rate limiting |  -  |
**500** | Server error occurred while making request |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **revoke_user_o_auth_access**
> revoke_user_o_auth_access()



Revoke the access token granted by the user. If the associated OAuth client is configured to receive webhooks, it will no longer receive them for this user.

### Example

* OAuth Authentication (OAuth):
```python
import time
import os
import whoop_client
from whoop_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://api.prod.whoop.com/developer
# See configuration.py for a list of all supported configuration parameters.
configuration = whoop_client.Configuration(
    host = "https://api.prod.whoop.com/developer"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

configuration.access_token = os.environ["ACCESS_TOKEN"]

# Enter a context with an instance of the API client
with whoop_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = whoop_client.UserApi(api_client)

    try:
        api_instance.revoke_user_o_auth_access()
    except Exception as e:
        print("Exception when calling UserApi->revoke_user_o_auth_access: %s\n" % e)
```



### Parameters
This endpoint does not need any parameter.

### Return type

void (empty response body)

### Authorization

[OAuth](../README.md#OAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**204** | Successful request; no response body |  -  |
**400** | Client error constructing the request |  -  |
**401** | Invalid authorization |  -  |
**429** | Request rejected due to rate limiting |  -  |
**500** | Server error occurred while making request |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

