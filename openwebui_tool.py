"""
title: Zabbix API
author: Tjaš Ajdovec
description: This tool lets the LLM interact with the Zabbix server, which is used for centralized device monitoring.
git_url: https://github.com/ta5946
version: 1.0.1
"""

# TODO Multiple tool calls in one prompt not available in Open WebUI version 5.0.3
# TODO Define more Zabbix API methods from https://www.zabbix.com/documentation/current/en/manual/api/reference

import requests
import json
from pydantic import BaseModel, Field


# Generic request function
def api_request(url, headers, body):
    try:
        response = requests.post(url, headers=headers, data=json.dumps(body))
        return response.json(), False
    except Exception as error:
        return {'Exception': str(error)}, True


def validate_prompt(prompt, max_length):
    if len(prompt) > max_length:
        print('Truncating response.')
        return prompt[:max_length]
    else:
        print('Valid response.')
        return prompt


# Tool class
class Tools:
    def __init__(self):
        self.valves = self.Valves()
        self.headers = {'Content-Type': 'application/json'}
        self.citation = True
        
    # Auth headers
    def _auth_headers(self):
        headers = self.headers.copy()
        if not self.valves.zabbix_api_token:
            raise ValueError(
                "Zabbix API token is not configured. "
                "Please set 'zabbix_api_token' in the tool configuration before making API calls."
            )
        headers["Authorization"] = f"Bearer {self.valves.zabbix_api_token}"
        return headers

    # Configuration class
    class Valves(BaseModel):
        zabbix_api_url: str = Field(
            default='',
            description='URL of the Zabbix API.',
        )

        zabbix_api_token: str = Field(
            default='',
            description='Authentication token for the Zabbix API.',
        )

        max_response_length: int = Field(
            default=4096,
            description='Maximum length of the API response.',
        )

    # Host list request
    async def get_host_list(self, __event_emitter__) -> str:
        """
        This function lets you retrieve the list of hosts monitored by Zabbix.
        Host is a device, such as desktop or virtual machine.
        :return: List of host ids, names and statuses.
        """
        body = {
            'jsonrpc': '2.0',
            'method': 'host.get',
            'params': {
                'output': ['host', 'status'],
            },
            'id': 1,
        }
        response, error = api_request(self.valves.zabbix_api_url, self._auth_headers(), body)

        if error:
            status = 'Error retrieving host list.'
        else:
            status = 'Processing host list response.'
        await __event_emitter__(
            {
                'type': 'status',
                'data': {'description': status, 'done': True},
            }
        )

        prompt = validate_prompt(f"""Describe the Zabbix API response you received to the user who requested it: {response}""", self.valves.max_response_length)
        return prompt

    # Problem list request
    async def get_problem_list(self, __event_emitter__) -> str:
        """
        This function lets you retrieve the list of current problems detected by Zabbix.
        Problem is a potential issue, such as high CPU utilization or unavailable SSH service.
        :return: List of problem descriptions.
        """
        body = {
            'jsonrpc': '2.0',
            'method': 'problem.get',
            'params': {
                'output': ['name'],
            },
            'id': 1,
        }
        response, error = api_request(self.valves.zabbix_api_url, self._auth_headers(), body)

        if error:
            status = 'Error retrieving problem list.'
        else:
            status = 'Processing problem list response.'
        await __event_emitter__(
            {
                'type': 'status',
                'data': {'description': status, 'done': True},
            }
        )

        prompt = validate_prompt(f"""Describe the Zabbix API response you received to the user who requested it: {response}""", self.valves.max_response_length)
        return prompt

    # Item list request
    async def get_item_list(self, host_name: str, __event_emitter__) -> str:
        """
        This function lets you retrieve the list of available items for a specified host monitored by Zabbix.
        Item is a monitored metric, such as CPU utilization or SSH response time.
        Host is a monitored device, such as desktop or virtual machine.
        :param host_name: Name of the host.
        :return: List of item ids and names for this host.
        """
        body = {
            'jsonrpc': '2.0',
            'method': 'item.get',
            'params': {
                'host': host_name,
                'output': ['name'],
            },
            'id': 1,
        }
        response, error = api_request(self.valves.zabbix_api_url, self._auth_headers(), body)

        if error:
            status = 'Error retrieving item list.'
        else:
            status = 'Processing item list response.'
        await __event_emitter__(
            {
                'type': 'status',
                'data': {'description': status, 'done': True},
            }
        )

        prompt = validate_prompt(f"""Describe the Zabbix API response you received to the user who requested it: {response}""", self.valves.max_response_length)
        return prompt

    # Item value request
    async def get_item_value(self, host_name: str, item_name: str, __event_emitter__) -> str:
        """
        This function lets you retrieve the item value for a specific host monitored by Zabbix.
        Item is a monitored metric, such as CPU utilization or SSH response time.
        Host is a monitored device, such as desktop or virtual machine.
        :param host_name: Name of the host.
        :param item_name: Name of the item.
        :return: Item name, value and units for this host.
        """
        body = {
            'jsonrpc': '2.0',
            'method': 'item.get',
            'params': {
                "host": host_name,
                "search": {
                    "name": item_name,
                },
                'output': ['name', 'lastvalue', 'units'],
            },
            'id': 1,
        }
        response, error = api_request(self.valves.zabbix_api_url, self._auth_headers(), body)

        if error:
            status = 'Error retrieving item value.'
        else:
            status = 'Processing item value response.'
        await __event_emitter__(
            {
                'type': 'status',
                'data': {'description': status, 'done': True},
            }
        )

        prompt = validate_prompt(f"""Describe the Zabbix API response you received to the user who requested it: {response}""", self.valves.max_response_length)
        return prompt
