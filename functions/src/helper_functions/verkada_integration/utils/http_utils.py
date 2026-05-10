import requests
import time
from requests.exceptions import RequestException
from src.shared import logger

def requests_with_retry(method, url, max_retries=10, delay=1, **kwargs):
    """
    Sends an HTTP request using the requests library with a retry mechanism.

    Args:
        method (str): The HTTP method (e.g., 'get', 'post', 'put', 'delete').
        url (str): The URL for the request.
        max_retries (int): The maximum number of retries. Defaults to 10.
        delay (int): The delay between retries in seconds. Defaults to 1.
        **kwargs: Additional arguments to pass to the requests function
                  (e.g., json, data, headers, timeout).

    Returns:
        requests.Response: The response object if the request is successful.

    Raises:
        RequestException: If the request fails after all retries.
    """
    retries = 0
    last_exception = None
    while retries < max_retries:
        try:
            # Add a default timeout if not specified by the caller
            if 'timeout' not in kwargs:
                kwargs['timeout'] = 30 # Default timeout of 30 seconds

            response = requests.request(method.lower(), url, **kwargs)
            if response.status_code == 400 and response.text == 'siteId and currentSiteId are the same':
                response.status_code = 200
            # Raise an HTTPError exception for bad status codes (4xx or 5xx)
            response.raise_for_status()
            # If request is successful, return the response
            return response
        except RequestException as e:
            last_exception = e
            retries += 1
            logger.error(f"Request failed ({e}). Retrying ({retries}/{max_retries}) in {delay} second(s)... URL: {url}, Method: {method}")
            if retries < max_retries:
                time.sleep(delay)

    logger.error(f"Request failed after {max_retries} retries. URL: {url}, Method: {method}")
    # If all retries fail, raise the last captured exception
    if last_exception:
        raise last_exception
    else:
        # Fallback exception if no specific exception was caught
        raise RequestException(f"Request failed after {max_retries} retries without capturing an exception. URL: {url}, Method: {method}")
