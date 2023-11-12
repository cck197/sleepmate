# whoop_client.RecoveryApi

All URIs are relative to *https://api.prod.whoop.com/developer*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_recovery_collection**](RecoveryApi.md#get_recovery_collection) | **GET** /v1/recovery | 
[**get_recovery_for_cycle**](RecoveryApi.md#get_recovery_for_cycle) | **GET** /v1/cycle/{cycleId}/recovery | 


# **get_recovery_collection**
> PaginatedRecoveryResponse get_recovery_collection(limit=limit, start=start, end=end, next_token=next_token)



Get all recoveries for a user, paginated. Results are sorted by start time of the related sleep in descending order.

### Example

* OAuth Authentication (OAuth):
```python
import time
import os
import whoop_client
from whoop_client.models.paginated_recovery_response import PaginatedRecoveryResponse
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
    api_instance = whoop_client.RecoveryApi(api_client)
    limit = 10 # int | Limit on the number of recoveries returned (optional) (default to 10)
    start = '2013-10-20T19:20:30+01:00' # datetime | Return recoveries that occurred after or during (inclusive) this time. If not specified, the response will not filter recoveries by a minimum time. (optional)
    end = '2013-10-20T19:20:30+01:00' # datetime | Return recoveries that intersect this time or ended before (exclusive) this time. If not specified, `end` will be set to `now`. (optional)
    next_token = 'next_token_example' # str | Optional next token from the previous response to get the next page. If not provided, the first page in the collection is returned (optional)

    try:
        api_response = api_instance.get_recovery_collection(limit=limit, start=start, end=end, next_token=next_token)
        print("The response of RecoveryApi->get_recovery_collection:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling RecoveryApi->get_recovery_collection: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **limit** | **int**| Limit on the number of recoveries returned | [optional] [default to 10]
 **start** | **datetime**| Return recoveries that occurred after or during (inclusive) this time. If not specified, the response will not filter recoveries by a minimum time. | [optional] 
 **end** | **datetime**| Return recoveries that intersect this time or ended before (exclusive) this time. If not specified, &#x60;end&#x60; will be set to &#x60;now&#x60;. | [optional] 
 **next_token** | **str**| Optional next token from the previous response to get the next page. If not provided, the first page in the collection is returned | [optional] 

### Return type

[**PaginatedRecoveryResponse**](PaginatedRecoveryResponse.md)

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

# **get_recovery_for_cycle**
> Recovery get_recovery_for_cycle(cycle_id)



Get the recovery for a cycle

### Example

* OAuth Authentication (OAuth):
```python
import time
import os
import whoop_client
from whoop_client.models.recovery import Recovery
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
    api_instance = whoop_client.RecoveryApi(api_client)
    cycle_id = 56 # int | ID of the cycle to retrieve

    try:
        api_response = api_instance.get_recovery_for_cycle(cycle_id)
        print("The response of RecoveryApi->get_recovery_for_cycle:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling RecoveryApi->get_recovery_for_cycle: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **cycle_id** | **int**| ID of the cycle to retrieve | 

### Return type

[**Recovery**](Recovery.md)

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
**404** | No resource found |  -  |
**401** | Invalid authorization |  -  |
**429** | Request rejected due to rate limiting |  -  |
**500** | Server error occurred while making request |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

