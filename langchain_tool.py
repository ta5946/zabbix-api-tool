import os
import json
import requests
from datetime import datetime
from langchain_core.tools import tool


headers_dict = {
    'Content-Type': 'application/json-rpc'
}


@tool(parse_docstring=True)
def zabbix_host_list() -> str:
    """
    This tool lets you retrieve a list of hosts monitored by Zabbix.
    You can use it as a starting point for further exploration.

    Host is a device, such as desktop or a VM.

    Returns:
        str: List of host ids, names and statuses.
    """

    body_dict = {
        'jsonrpc': '2.0',
        'method': 'host.get',
        'params': {
            'output': ['host', 'status'],
        },
        'id': 1,
        'auth': os.getenv('ZABBIX_API_TOKEN')
    }
    body_json = json.dumps(body_dict)

    try:
        response = requests.post(os.getenv('ZABBIX_API_URL'), headers=headers_dict, data=body_json)
        result = response.json()['result']
        return "Here is the requested list of hosts: " + str(result)
    except Exception as error:
        return "Error occurred while retrieving the list of hosts: " + str(error)


@tool(parse_docstring=True)
def zabbix_item_list() -> str:
    """
    This tool lets you retrieve a list of items monitored by Zabbix.
    You can use it as a starting point for further exploration.

    Item is a metric, such as CPU utilization or OS version.

    Returns:
        str: List of item ids, names and descriptions.
    """

    body_dict = {
        'jsonrpc': '2.0',
        'method': 'item.get',
        'params': {
            'host': 'Server',
            'output': ['name', 'description'],
        },
        'id': 1,
        'auth': os.getenv('ZABBIX_API_TOKEN')
    }
    body_json = json.dumps(body_dict)

    try:
        response = requests.post(os.getenv('ZABBIX_API_URL'), headers=headers_dict, data=body_json)
        result = response.json()['result']
        return "Here is the requested list of items: " + str(result)
    except Exception as error:
        return "Error occurred while retrieving the list of items: " + str(error)


@tool(parse_docstring=True)
def zabbix_item_value(host_name: str, item_name: str) -> str:
    """
    It is advised to retrieve the list of hosts and items before using this tool!

    This tool lets you retrieve a single item value for a selected host.
    You can use it if you are interested in the current state.

    Host is a device, such as desktop or a VM.
    Item is a metric, such as CPU utilization or OS version.

    Args:
        host_name: Must be a value from the retrieved host list.
        item_name: Must be a value from the retrieved item list.

    Returns:
        str: Item id, name, value and units.
    """

    body_dict = {
        'jsonrpc': '2.0',
        'method': 'item.get',
        'params': {
            'host': host_name,
            'search': {
                'name': item_name,
            },
            'output': ['name', 'lastvalue', 'units'],
        },
        'id': 1,
        'auth': os.getenv('ZABBIX_API_TOKEN')
    }
    body_json = json.dumps(body_dict)

    try:
        response = requests.post(os.getenv('ZABBIX_API_URL'), headers=headers_dict, data=body_json)
        result = response.json()['result']
        if result:
            return "Here is the requested item value: " + str(result)
        else:
            return "The requested item is not monitored on the selected host."
    except Exception as error:
        return "Error occurred while retrieving the item value: " + str(error)


@tool(parse_docstring=True)
def zabbix_item_history(host_name: str, item_name: str) -> str:
    """
    It is advised to retrieve the list of hosts and items before using this tool!

    This tool lets you retrieve history of item values for a selected host.
    You can use it if you are interested in past events.

    Host is a device, such as desktop or a VM.
    Item is a metric, such as CPU utilization or OS version.

    Args:
        host_name: Must be a value from the retrieved host list.
        item_name: Must be a value from the retrieved item list.

    Returns:
        str: Item ids, times and values.
    """

    body_dict = {
        'jsonrpc': '2.0',
        'method': 'item.get',
        'params': {
            'host': host_name,
            'search': {
                'name': item_name,
            },
            'output': ['name', 'type', 'lastvalue', 'units'],
        },
        'id': 1,
        'auth': os.getenv('ZABBIX_API_TOKEN')
    }
    body_json = json.dumps(body_dict)

    try:
        response = requests.post(os.getenv('ZABBIX_API_URL'), headers=headers_dict, data=body_json)
        item_result = response.json()['result']
        print(item_result)
        if not item_result:
            return "The requested item is not monitored on the selected host."

        # Set type to int
        if item_result[0]['lastvalue'].isdigit():
            item_result[0]['type'] = 3

        body_dict = {
            'jsonrpc': '2.0',
            'method': 'history.get',
            'params': {
                'itemids': item_result[0]['itemid'],
                'history': item_result[0]['type'],
                'time_from': int(datetime.now().timestamp()) - 3600,
                'output': ['clock', 'value'],
            },
            'id': 1,
            'auth': os.getenv('ZABBIX_API_TOKEN')
        }
        body_json = json.dumps(body_dict)

        response = requests.post(os.getenv('ZABBIX_API_URL'), headers=headers_dict, data=body_json)
        print(response.json())
        history_result = response.json()['result']
        for item_value in history_result:
            item_value['clock'] = datetime.fromtimestamp(int(item_value['clock'])).strftime('%d. %B %Y, %H:%M')

        if history_result:
            return "Here is the requested item history: " + str(history_result)
        else:
            return "The requested item is not monitored on the selected host."
    except Exception as error:
        return "Error occurred while retrieving the item history: " + str(error)
