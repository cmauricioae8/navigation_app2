import requests
from utilities.enums import HttpMethod
from config.settings import SERVER_IP, SERVER_PORT


def try_endpoint(method, url, params, payload) -> list:
    status_code = None
    message = None
    
    try:
        if method == HttpMethod.POST:
            response = requests.post(url, json=payload, params=params, timeout=3)
        elif method == HttpMethod.GET:
            response = requests.get(url, params=params,timeout=3)
        else:
            print(f"Error: {method} NOT supported")
            return False
        
        # response.raise_for_status()
        status_code = response.status_code
        message = response.text

    except requests.exceptions.Timeout:
        message = "The request timed out after 3 seconds."
    except requests.exceptions.RequestException as ex:
        message = f"Error: {ex}"

    return status_code, message


def consume_endpoint(method, expected_code, url_suffix, params, payload) -> bool:
    url_base = f"http://{SERVER_IP}:{SERVER_PORT}/"
    url = url_base + url_suffix
    # print(f"Change mode: {url=}")

    status_code, message = try_endpoint(method, url, params, payload)

    print(f"{status_code=}\n{message=}")
    
    ## TODO: implement handler exceptions for 3xx and 4xx status codes
    if status_code == expected_code:
        return True
    else: return False

