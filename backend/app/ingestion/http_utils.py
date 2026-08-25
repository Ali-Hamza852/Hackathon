import httpx

from app.ingestion.exceptions import AQIProviderError

REQUEST_TIMEOUT_SECONDS = 5.0
RETRY_ATTEMPTS = 2


def request_json(
    provider: str,
    method: str,
    url: str,
    *,
    params: dict | None = None,
    data: dict | None = None,
    headers: dict | None = None,
    timeout: float = REQUEST_TIMEOUT_SECONDS,
) -> dict:
    last_error: Exception | None = None
    for attempt in range(RETRY_ATTEMPTS):
        try:
            response = httpx.request(
                method, url, params=params, data=data, headers=headers, timeout=timeout
            )
            response.raise_for_status()
            return response.json()
        except (httpx.HTTPError, ValueError) as exc:
            last_error = exc
    raise AQIProviderError(provider, str(last_error))


def get_json(provider: str, url: str, params: dict | None = None, headers: dict | None = None) -> dict:
    return request_json(provider, "GET", url, params=params, headers=headers)
