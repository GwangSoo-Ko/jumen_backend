import requests
from app.service.kiwoom.constant import *

def _post_request(token, data, host, endpoint, cont_yn=None, next_key=None, api_id=None):
    """
    Helper function to make a POST request to the Kiwoom API.
    Args:
        token (str): Authorization token.
        data (dict): Data to be sent in the request body.
        host (str): Host URL.
        endpoint (str): API endpoint.
        cont_yn (str, optional): Continuation flag. Defaults to None.
        next_key (str, optional): Next key for pagination. Defaults to None.
        api_id (str, optional): API ID. Defaults to None.
    Returns:
        Response object from the POST request.
    """
    url = host + endpoint
    headers = {
        'Content-Type': CONTENT_TYPE,
    }
    if token is not None and token != '':
        headers['authorization'] = f'Bearer {token}'
    if cont_yn is not None:
        headers['cont-yn'] = cont_yn
    if next_key is not None:
        headers['next-key'] = next_key
    if api_id is not None:
        headers['api-id'] = api_id
    return requests.post(url, headers=headers, json=data)

def fn_auth(data, host=DEFAULT_HOST, endpoint=''):
    """
    Function to authenticate and get the token.
    Args:
        data (dict): Data to be sent in the request body.
        host (str): Host URL.
        endpoint (str): API endpoint.
    Returns:
        Response object from the POST request.
    """
    return _post_request('', data, host, endpoint)

def fn_stock_info(token, data, cont_yn='N', next_key='', host=DEFAULT_HOST, api_id=''):
    """
    Function to get stock information.
    Args:
        token (str): Authorization token.
        data (dict): Data to be sent in the request body.
        cont_yn (str, optional): Continuation flag. Defaults to 'N'.
        next_key (str, optional): Next key for pagination. Defaults to ''.
        host (str, optional): Host URL. Defaults to DEFAULT_HOST.
        api_id (str, optional): API ID. Defaults to ''.
    Returns:
        Response object from the POST request.
    """
    return _post_request(token, data, host, STOCK_INFO_ENDPOINT, cont_yn, next_key, api_id)

def fn_market_condition_info(token, data, cont_yn='N', next_key='', host=DEFAULT_HOST, api_id=''):
    """
    Function to get market condition.
    Args:
        token (str): Authorization token.
        data (dict): Data to be sent in the request body.
        cont_yn (str, optional): Continuation flag. Defaults to 'N'.
        next_key (str, optional): Next key for pagination. Defaults to ''.
        host (str, optional): Host URL. Defaults to DEFAULT_HOST.
        api_id (str, optional): API ID. Defaults to ''.
    Returns:
        Response object from the POST request.
    """
    return _post_request(token, data, host, MARKET_CONDITION_ENDPOINT, cont_yn, next_key, api_id)

def fn_foreign_institution_info(token, data, cont_yn='N', next_key='', host=DEFAULT_HOST, api_id=''):
    """
    Function to get foreign institution information.
    Args:
        token (str): Authorization token.
        data (dict): Data to be sent in the request body.
        cont_yn (str, optional): Continuation flag. Defaults to 'N'.
        next_key (str, optional): Next key for pagination. Defaults to ''.
        host (str, optional): Host URL. Defaults to DEFAULT_HOST.
        api_id (str, optional): API ID. Defaults to ''.
    Returns:
        Response object from the POST request.
    """
    return _post_request(token, data, host, FOREIGN_INSTITUTION_ENDPOINT, cont_yn, next_key, api_id)

def fn_sector_info(token, data, cont_yn='N', next_key='', host=DEFAULT_HOST, api_id=''):
    """
    Function to get sector information.
    Args:
        token (str): Authorization token.
        data (dict): Data to be sent in the request body.
        cont_yn (str, optional): Continuation flag. Defaults to 'N'.
        next_key (str, optional): Next key for pagination. Defaults to ''.
        host (str, optional): Host URL. Defaults to DEFAULT_HOST.
        api_id (str, optional): API ID. Defaults to ''.
    Returns:
        Response object from the POST request.
    """
    return _post_request(token, data, host, SECTOR_ENDPOINT, cont_yn, next_key, api_id)

def fn_rank_info(token, data, cont_yn='N', next_key='', host=DEFAULT_HOST, api_id=''):
    """
    Function to get rank information.
    Args:
        token (str): Authorization token.
        data (dict): Data to be sent in the request body.
        cont_yn (str, optional): Continuation flag. Defaults to 'N'.
        next_key (str, optional): Next key for pagination. Defaults to ''.
        host (str, optional): Host URL. Defaults to DEFAULT_HOST.
        api_id (str, optional): API ID. Defaults to ''.
    Returns:
        Response object from the POST request.
    """
    return _post_request(token, data, host, RANK_INFO_ENDPOINT, cont_yn, next_key, api_id)

def fn_chart_info(token, data, cont_yn='N', next_key='', host=DEFAULT_HOST, api_id=''):
    """
    Function to get chart information.
    Args:
        token (str): Authorization token.
        data (dict): Data to be sent in the request body.
        cont_yn (str, optional): Continuation flag. Defaults to 'N'.
        next_key (str, optional): Next key for pagination. Defaults to ''.
        host (str, optional): Host URL. Defaults to DEFAULT_HOST.
        api_id (str, optional): API ID. Defaults to ''.
    Returns:
        Response object from the POST request.
    """
    return _post_request(token, data, host, CHART_INFO_ENDPOINT, cont_yn, next_key, api_id)

def fn_account_info(token, data, cont_yn='N', next_key='', host=DEFAULT_HOST, api_id=''):
    """
    Function to get account information.
    Args:
        token (str): Authorization token.
        data (dict): Data to be sent in the request body.
        cont_yn (str, optional): Continuation flag. Defaults to 'N'.
        next_key (str, optional): Next key for pagination. Defaults to ''.
        host (str, optional): Host URL. Defaults to DEFAULT_HOST.
        api_id (str, optional): API ID. Defaults to ''.
    Returns:
        Response object from the POST request.
    """
    return _post_request(token, data, host, ACCOUNT_INFO_ENDPOINT, cont_yn, next_key, api_id)

def fn_theme_info(token, data, cont_yn='N', next_key='', host=DEFAULT_HOST, api_id=''):
    """
    Function to get theme information.
    Args:
        token (str): Authorization token.
        data (dict): Data to be sent in the request body.
        cont_yn (str, optional): Continuation flag. Defaults to 'N'.
        next_key (str, optional): Next key for pagination. Defaults to ''.
        host (str, optional): Host URL. Defaults to DEFAULT_HOST.
        api_id (str, optional): API ID. Defaults to ''.
    Returns:
        Response object from the POST request.
    """
    return _post_request(token, data, host, THEME_INFO_ENDPOINT, cont_yn, next_key, api_id)

def fn_order_execution(token, data, cont_yn='N', next_key='', host=DEFAULT_HOST, api_id=''):
    """
    Function to execute order.
    Args:
        token (str): Authorization token.
        data (dict): Data to be sent in the request body.
        cont_yn (str, optional): Continuation flag. Defaults to 'N'.
        next_key (str, optional): Next key for pagination. Defaults to ''.
        host (str, optional): Host URL. Defaults to DEFAULT_HOST.
        api_id (str, optional): API ID. Defaults to ''.
    Returns:
        Response object from the POST request.
    """
    return _post_request(token, data, host, ORDER_EXECUTION_ENDPOINT, cont_yn, next_key, api_id)

