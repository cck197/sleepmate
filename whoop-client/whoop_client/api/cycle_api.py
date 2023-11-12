# coding: utf-8

"""
    WHOOP API

    No description provided (generated by Openapi Generator https://github.com/openapitools/openapi-generator)

    The version of the OpenAPI document: 1.0.0
    Generated by OpenAPI Generator (https://openapi-generator.tech)

    Do not edit the class manually.
"""  # noqa: E501


import io
import warnings

from pydantic import validate_call, Field, StrictFloat, StrictStr, StrictInt
from typing import Dict, List, Optional, Tuple, Union, Any

try:
    from typing import Annotated
except ImportError:
    from typing_extensions import Annotated

from pydantic import Field
from typing_extensions import Annotated
from datetime import datetime

from pydantic import StrictInt, StrictStr

from typing import Optional

from whoop_client.models.cycle import Cycle
from whoop_client.models.paginated_cycle_response import PaginatedCycleResponse

from whoop_client.api_client import ApiClient
from whoop_client.api_response import ApiResponse
from whoop_client.rest import RESTResponseType


class CycleApi:
    """NOTE: This class is auto generated by OpenAPI Generator
    Ref: https://openapi-generator.tech

    Do not edit the class manually.
    """

    def __init__(self, api_client=None) -> None:
        if api_client is None:
            api_client = ApiClient.get_default()
        self.api_client = api_client


    @validate_call
    def get_cycle_by_id(
        self,
        cycle_id: Annotated[StrictInt, Field(description="ID of the cycle to retrieve")],
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> Cycle:
        """get_cycle_by_id

        Get the cycle for the specified ID

        :param cycle_id: ID of the cycle to retrieve (required)
        :type cycle_id: int
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._get_cycle_by_id_serialize(
            cycle_id=cycle_id,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "Cycle",
            '400': None,
            '404': None,
            '401': None,
            '429': None,
            '500': None
            
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        ).data


    @validate_call
    def get_cycle_by_id_with_http_info(
        self,
        cycle_id: Annotated[StrictInt, Field(description="ID of the cycle to retrieve")],
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> ApiResponse[Cycle]:
        """get_cycle_by_id

        Get the cycle for the specified ID

        :param cycle_id: ID of the cycle to retrieve (required)
        :type cycle_id: int
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._get_cycle_by_id_serialize(
            cycle_id=cycle_id,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "Cycle",
            '400': None,
            '404': None,
            '401': None,
            '429': None,
            '500': None
            
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        )


    @validate_call
    def get_cycle_by_id_without_preload_content(
        self,
        cycle_id: Annotated[StrictInt, Field(description="ID of the cycle to retrieve")],
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> RESTResponseType:
        """get_cycle_by_id

        Get the cycle for the specified ID

        :param cycle_id: ID of the cycle to retrieve (required)
        :type cycle_id: int
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._get_cycle_by_id_serialize(
            cycle_id=cycle_id,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "Cycle",
            '400': None,
            '404': None,
            '401': None,
            '429': None,
            '500': None
            
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _get_cycle_by_id_serialize(
        self,
        cycle_id,
        _request_auth,
        _content_type,
        _headers,
        _host_index,
    ) -> Tuple:

        _host = None

        _collection_formats: Dict[str, str] = {
            
        }

        _path_params: Dict[str, str] = {}
        _query_params: List[Tuple[str, str]] = []
        _header_params: Dict[str, Optional[str]] = _headers or {}
        _form_params: List[Tuple[str, str]] = []
        _files: Dict[str, str] = {}
        _body_params: Optional[bytes] = None

        # process the path parameters
        if cycle_id is not None:
            _path_params['cycleId'] = cycle_id
        # process the query parameters
        # process the header parameters
        # process the form parameters
        # process the body parameter


        # set the HTTP header `Accept`
        _header_params['Accept'] = self.api_client.select_header_accept(
            [
                'application/json'
            ]
        )


        # authentication setting
        _auth_settings: List[str] = [
            'OAuth'
        ]

        return self.api_client.param_serialize(
            method='GET',
            resource_path='/v1/cycle/{cycleId}',
            path_params=_path_params,
            query_params=_query_params,
            header_params=_header_params,
            body=_body_params,
            post_params=_form_params,
            files=_files,
            auth_settings=_auth_settings,
            collection_formats=_collection_formats,
            _host=_host,
            _request_auth=_request_auth
        )




    @validate_call
    def get_cycle_collection(
        self,
        limit: Annotated[Optional[Annotated[int, Field(le=25, strict=True)]], Field(description="Limit on the number of cycles returned")] = None,
        start: Annotated[Optional[datetime], Field(description="Return cycles that occurred after or during (inclusive) this time. If not specified, the response will not filter cycles by a minimum time.")] = None,
        end: Annotated[Optional[datetime], Field(description="Return cycles that intersect this time or ended before (exclusive) this time. If not specified, `end` will be set to `now`.")] = None,
        next_token: Annotated[Optional[StrictStr], Field(description="Optional next token from the previous response to get the next page. If not provided, the first page in the collection is returned")] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> PaginatedCycleResponse:
        """get_cycle_collection

        Get all physiological cycles for a user, paginated. Results are sorted by start time in descending order.

        :param limit: Limit on the number of cycles returned
        :type limit: int
        :param start: Return cycles that occurred after or during (inclusive) this time. If not specified, the response will not filter cycles by a minimum time.
        :type start: datetime
        :param end: Return cycles that intersect this time or ended before (exclusive) this time. If not specified, `end` will be set to `now`.
        :type end: datetime
        :param next_token: Optional next token from the previous response to get the next page. If not provided, the first page in the collection is returned
        :type next_token: str
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._get_cycle_collection_serialize(
            limit=limit,
            start=start,
            end=end,
            next_token=next_token,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "PaginatedCycleResponse",
            '400': None,
            '401': None,
            '429': None,
            '500': None
            
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        ).data


    @validate_call
    def get_cycle_collection_with_http_info(
        self,
        limit: Annotated[Optional[Annotated[int, Field(le=25, strict=True)]], Field(description="Limit on the number of cycles returned")] = None,
        start: Annotated[Optional[datetime], Field(description="Return cycles that occurred after or during (inclusive) this time. If not specified, the response will not filter cycles by a minimum time.")] = None,
        end: Annotated[Optional[datetime], Field(description="Return cycles that intersect this time or ended before (exclusive) this time. If not specified, `end` will be set to `now`.")] = None,
        next_token: Annotated[Optional[StrictStr], Field(description="Optional next token from the previous response to get the next page. If not provided, the first page in the collection is returned")] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> ApiResponse[PaginatedCycleResponse]:
        """get_cycle_collection

        Get all physiological cycles for a user, paginated. Results are sorted by start time in descending order.

        :param limit: Limit on the number of cycles returned
        :type limit: int
        :param start: Return cycles that occurred after or during (inclusive) this time. If not specified, the response will not filter cycles by a minimum time.
        :type start: datetime
        :param end: Return cycles that intersect this time or ended before (exclusive) this time. If not specified, `end` will be set to `now`.
        :type end: datetime
        :param next_token: Optional next token from the previous response to get the next page. If not provided, the first page in the collection is returned
        :type next_token: str
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._get_cycle_collection_serialize(
            limit=limit,
            start=start,
            end=end,
            next_token=next_token,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "PaginatedCycleResponse",
            '400': None,
            '401': None,
            '429': None,
            '500': None
            
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        )


    @validate_call
    def get_cycle_collection_without_preload_content(
        self,
        limit: Annotated[Optional[Annotated[int, Field(le=25, strict=True)]], Field(description="Limit on the number of cycles returned")] = None,
        start: Annotated[Optional[datetime], Field(description="Return cycles that occurred after or during (inclusive) this time. If not specified, the response will not filter cycles by a minimum time.")] = None,
        end: Annotated[Optional[datetime], Field(description="Return cycles that intersect this time or ended before (exclusive) this time. If not specified, `end` will be set to `now`.")] = None,
        next_token: Annotated[Optional[StrictStr], Field(description="Optional next token from the previous response to get the next page. If not provided, the first page in the collection is returned")] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> RESTResponseType:
        """get_cycle_collection

        Get all physiological cycles for a user, paginated. Results are sorted by start time in descending order.

        :param limit: Limit on the number of cycles returned
        :type limit: int
        :param start: Return cycles that occurred after or during (inclusive) this time. If not specified, the response will not filter cycles by a minimum time.
        :type start: datetime
        :param end: Return cycles that intersect this time or ended before (exclusive) this time. If not specified, `end` will be set to `now`.
        :type end: datetime
        :param next_token: Optional next token from the previous response to get the next page. If not provided, the first page in the collection is returned
        :type next_token: str
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._get_cycle_collection_serialize(
            limit=limit,
            start=start,
            end=end,
            next_token=next_token,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "PaginatedCycleResponse",
            '400': None,
            '401': None,
            '429': None,
            '500': None
            
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _get_cycle_collection_serialize(
        self,
        limit,
        start,
        end,
        next_token,
        _request_auth,
        _content_type,
        _headers,
        _host_index,
    ) -> Tuple:

        _host = None

        _collection_formats: Dict[str, str] = {
            
        }

        _path_params: Dict[str, str] = {}
        _query_params: List[Tuple[str, str]] = []
        _header_params: Dict[str, Optional[str]] = _headers or {}
        _form_params: List[Tuple[str, str]] = []
        _files: Dict[str, str] = {}
        _body_params: Optional[bytes] = None

        # process the path parameters
        # process the query parameters
        if limit is not None:
            
            _query_params.append(('limit', limit))
            
        if start is not None:
            if isinstance(start, datetime):
                _query_params.append(
                    (
                        'start',
                        start.strftime(
                            self.api_client.configuration.datetime_format
                        )
                    )
                )
            else:
                _query_params.append(('start', start))
            
        if end is not None:
            if isinstance(end, datetime):
                _query_params.append(
                    (
                        'end',
                        end.strftime(
                            self.api_client.configuration.datetime_format
                        )
                    )
                )
            else:
                _query_params.append(('end', end))
            
        if next_token is not None:
            
            _query_params.append(('nextToken', next_token))
            
        # process the header parameters
        # process the form parameters
        # process the body parameter


        # set the HTTP header `Accept`
        _header_params['Accept'] = self.api_client.select_header_accept(
            [
                'application/json'
            ]
        )


        # authentication setting
        _auth_settings: List[str] = [
            'OAuth'
        ]

        return self.api_client.param_serialize(
            method='GET',
            resource_path='/v1/cycle',
            path_params=_path_params,
            query_params=_query_params,
            header_params=_header_params,
            body=_body_params,
            post_params=_form_params,
            files=_files,
            auth_settings=_auth_settings,
            collection_formats=_collection_formats,
            _host=_host,
            _request_auth=_request_auth
        )


