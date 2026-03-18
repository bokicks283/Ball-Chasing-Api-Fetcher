import random
import time
from typing import Optional

import requests

from ballchasing_client.exceptions import (
    BallChasingAuthError,
    BallChasingRequestError,
    BallChasingServerError,
    BallChasingUnexpectedError,
)
from ballchasing_client.model.ballchasing_model import ReplayQuery


class BallChasingClient:
    def __init__(
        self,
        token: str,
        base_url: str = "https://ballchasing.com/api",
        timeout: int = 15,
    ):
        self._token = token
        self._base_url = base_url
        self._timeout = timeout
        self._session = requests.Session()
        self._session.headers.update({"Authorization": self._token})

    # Context function defs
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._session.close()

    # Helper function defs
    def _build_url(self, path: Optional[str]) -> str:
        base = self._base_url.rstrip("/")
        if not path:
            return base
        return f"{base}/{path.lstrip('/')}"

    def _exp_backoff_with_jitter(self, attempt: int, max_backoff: float = 60.0):
        # trunk-ignore(bandit/B311)
        return min(2**attempt + (0.5 - random.random()), max_backoff)

    def _is_retriable_exception(self, exception: Exception):
        retriable = [requests.exceptions.ConnectionError, requests.Timeout]
        return isinstance(exception, tuple(retriable))

    def _is_response_successful(self, response: requests.Response):
        if response.status_code >= 200 and response.status_code < 300:
            return True
        return False

    def _is_auth_error(self, response: requests.Response):
        return response.status_code == 401 or response.status_code == 403

    def _is_unexpected_error(self, response: requests.Response):
        return response.status_code < 200 or (
            response.status_code >= 300 and response.status_code < 400
        )

    def _is_400_error(self, response: requests.Response):
        return response.status_code >= 400 and response.status_code < 500

    def _is_500_error(self, response: requests.Response):
        return response.status_code >= 500

    def _is_response_retriable(self, response: requests.Response):
        retriable = [408, 429, 500, 502, 503, 504]
        return response.status_code in retriable

    def _request(
        self,
        method: str,
        path: Optional[str] = None,
        url: Optional[str] = None,
        headers: Optional[dict] = None,
        params: Optional[dict | list[tuple[str, str]]] = None,
        json: Optional[dict] = None,
        files: Optional[dict] = None,
        retries: int = 3,
    ) -> dict:
        """base request method with retry logic

        Args:
            **method** (str): The HTTP method to use for the request (e.g., "GET", "POST").
            **path** (Optional[str], optional): The path to append to the base URL. Is ignored if url is provided. Defaults to None.
            **url** (Optional[str], optional): The full URL to use for the request. Defaults to None.
            **headers** (Optional[dict], optional): Additional headers to include in the request. Defaults to None.
            **params** (Optional[dict  |  list[tuple[str, str]]], optional): Query parameters for the request. Defaults to None.
            **json** (Optional[dict], optional): JSON payload for the request. Defaults to None.
            **files** (Optional[dict], optional): Files to upload with the request. Defaults to None.
            **retries** (int, optional): Number of times to retry the request in case of failure. Defaults to 3.

        Raises:
            BallChasingRequestError
            BallChasingAuthError
            BallChasingUnexpectedError
            BallChasingServerError

        Returns:
            dict: The JSON response from the API.
        """
        # Make request to api
        uri = self._build_url(path)
        last_exception: Optional[Exception] = None
        last_response: Optional[requests.Response] = (
            None  # pyright: ignore[reportAssignmentType]
        )
        for i in range(1, retries + 1):
            try:
                response = self._session.request(
                    method,
                    url if url is not None else uri,
                    params=params,
                    json=json,
                    files=files,
                    headers=headers,
                    timeout=self._timeout,
                )
            except requests.RequestException as e:
                last_exception = e
                if not self._is_retriable_exception(last_exception):
                    # raise error
                    raise BallChasingRequestError(
                        str(last_exception)
                    ) from last_exception
                if i < retries:
                    time.sleep(self._exp_backoff_with_jitter(i))
                continue

            last_response = response
            if self._is_response_successful(last_response):
                return last_response.json()
            elif self._is_auth_error(last_response):
                raise BallChasingAuthError(
                    "Authentication error. Please check this client was initialized with a valid token."
                )
            elif self._is_response_retriable(last_response):
                if i < retries:
                    time.sleep(self._exp_backoff_with_jitter(i))
                continue
            elif self._is_400_error(last_response):
                raise BallChasingRequestError(
                    f"Bad request. Please check the request parameters. Status code: {last_response.status_code}"
                )
            elif self._is_500_error(last_response):
                raise BallChasingServerError(
                    f"Server error. Status code: {last_response.status_code}, Response: {last_response.text}"
                )
            elif self._is_unexpected_error(last_response):
                raise BallChasingUnexpectedError(
                    f"Unexpected error. Status code: {last_response.status_code}, Response: {last_response.text}"
                )
        else:
            if last_exception is not None:
                raise BallChasingUnexpectedError(
                    f"Unexpected error occurred. URI: {uri} Exception: {str(last_exception)}"
                )
            if last_response is not None:
                if last_response.status_code == 429:
                    raise BallChasingRequestError(
                        f"Rate limit exceeded. URI: {uri} Status code: {last_response.status_code}, Response: {last_response.text}"
                    )
                elif self._is_500_error(last_response):
                    raise BallChasingServerError(
                        f"Server error. URI: {uri} Status code: {last_response.status_code}, Response: {last_response.text}"
                    )
                raise BallChasingServerError(
                    f"Max retries exceeded. URI: {uri} Status code: {last_response.status_code}, Response: {last_response.text}"
                )
            raise BallChasingUnexpectedError(f"URI: {uri} Unknown error.")

    # Public API function defs
    def close(self):
        self._session.close()

    def ping(self):
        return self._request("GET")

    def list_replays(
        self,
        input_query: Optional[ReplayQuery] = None,
        extra_params: Optional[dict] = None
    ) -> list:
        # process the query into request parameters
        params = {}
        query = input_query or ReplayQuery()
        if query.players:
            for player in query.players:
                # prefer id over name if available
                if player.id:
                    if player.platform is None:
                        # Just to make the linter happy.
                        raise ValueError(
                            "Player platform must be provided if player id is provided. This should never happen."
                        )
                    params.setdefault("player-id", []).append(
                        f"{player.platform.value}:{player.id}"
                    )
                elif player.name:
                    params.setdefault("player-name", []).append(player.name)
        if query.playlists:
            for playlist in query.playlists:
                params.setdefault("playlist", []).append(playlist.value)
        if query.season:
            params["season"] = query.season
        if query.match_result:
            params["match-result"] = query.match_result.value
        if query.min_rank:
            params["min-rank"] = query.min_rank.value
        if query.max_rank:
            params["max-rank"] = query.max_rank.value
        if query.pro is not None:
            params["pro"] = str(query.pro).lower()
        if query.uploader:
            params["uploader"] = str(query.uploader)
        if query.group:
            params["group"] = query.group
        if query.map:
            params["map"] = query.map
        if query.created_before:
            params["created-before"] = query.created_before.isoformat()
        if query.created_after:
            params["created-after"] = query.created_after.isoformat()
        if query.replay_date_after:
            params["replay-date-after"] = query.replay_date_after.isoformat()
        if query.replay_date_before:
            params["replay-date-before"] = query.replay_date_before.isoformat()
        if query.count:
            params["count"] = query.count
        if query.sort_by:
            params["sort-by"] = query.sort_by.value
        if query.sort_dir:
            params["sort-dir"] = query.sort_dir.value
        if extra_params:
            for key, value in extra_params.items():
                if key not in params:
                    params[key] = value
        replays = []
        has_next = False
        result = self._request("GET", "/replays", params=params)
        replays.extend(result.get("list", []))
        has_next = "next" in result
        if has_next:
            # keep calling the next url until we reach 'query.limit' or no more pages
            next_url = result.get("next", "")
            while next_url:
                if query.limit and len(replays) >= query.limit:
                    if len(replays) > query.limit:
                        replays = replays[: query.limit]
                    break
                next_result = self._request("GET", url=next_url)
                replays.extend(next_result.get("list", []))
                next_url = next_result.get("next")
                if next_url is None:
                    break
        if query.limit:
            if len(replays) > query.limit:
                replays = replays[: query.limit]
        return replays
