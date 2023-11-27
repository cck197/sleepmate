# whoop_client.WorkoutApi

All URIs are relative to *https://api.prod.whoop.com/developer*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_workout_by_id**](WorkoutApi.md#get_workout_by_id) | **GET** /v1/activity/workout/{workoutId} | 
[**get_workout_collection**](WorkoutApi.md#get_workout_collection) | **GET** /v1/activity/workout | 


# **get_workout_by_id**
> Workout get_workout_by_id(workout_id)



Get the workout for the specified ID

### Example

* OAuth Authentication (OAuth):
```python
import time
import os
import whoop_client
from whoop_client.models.workout import Workout
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
    api_instance = whoop_client.WorkoutApi(api_client)
    workout_id = 56 # int | ID of the workout to retrieve

    try:
        api_response = api_instance.get_workout_by_id(workout_id)
        print("The response of WorkoutApi->get_workout_by_id:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WorkoutApi->get_workout_by_id: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **workout_id** | **int**| ID of the workout to retrieve | 

### Return type

[**Workout**](Workout.md)

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

# **get_workout_collection**
> PaginatedWorkoutResponse get_workout_collection(limit=limit, start=start, end=end, next_token=next_token)



Get all workouts for a user, paginated. Results are sorted by start time in descending order.

### Example

* OAuth Authentication (OAuth):
```python
import time
import os
import whoop_client
from whoop_client.models.paginated_workout_response import PaginatedWorkoutResponse
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
    api_instance = whoop_client.WorkoutApi(api_client)
    limit = 10 # int | Limit on the number of workouts returned (optional) (default to 10)
    start = '2013-10-20T19:20:30+01:00' # datetime | Return workouts that occurred after or during (inclusive) this time. If not specified, the response will not filter workouts by a minimum time. (optional)
    end = '2013-10-20T19:20:30+01:00' # datetime | Return workouts that intersect this time or ended before (exclusive) this time. If not specified, `end` will be set to `now`. (optional)
    next_token = 'next_token_example' # str | Optional next token from the previous response to get the next page. If not provided, the first page in the collection is returned (optional)

    try:
        api_response = api_instance.get_workout_collection(limit=limit, start=start, end=end, next_token=next_token)
        print("The response of WorkoutApi->get_workout_collection:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WorkoutApi->get_workout_collection: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **limit** | **int**| Limit on the number of workouts returned | [optional] [default to 10]
 **start** | **datetime**| Return workouts that occurred after or during (inclusive) this time. If not specified, the response will not filter workouts by a minimum time. | [optional] 
 **end** | **datetime**| Return workouts that intersect this time or ended before (exclusive) this time. If not specified, &#x60;end&#x60; will be set to &#x60;now&#x60;. | [optional] 
 **next_token** | **str**| Optional next token from the previous response to get the next page. If not provided, the first page in the collection is returned | [optional] 

### Return type

[**PaginatedWorkoutResponse**](PaginatedWorkoutResponse.md)

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

