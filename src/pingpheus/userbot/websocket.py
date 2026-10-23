import json
from collections.abc import Callable

import websockets

from .. import settings
from ..settings import logger
from ..shortcuts import get_channel_list


class SlackWebsocketClient:
    def __init__(self, xoxc_token, xoxd_token):
        self.xoxc_token = xoxc_token
        self.xoxd_token = xoxd_token

        self.event_listeners: list[tuple[str | None, Callable]] = []

    async def get_url(self) -> str:
        url = f"wss://wss-primary.slack.com/?token={self.xoxc_token}&sync_desync=1&slack_client=desktop&start_args=%3Fagent%3Dclient%26org_wide_aware%3Dtrue%26agent_version%3D1792581458%26eac_cache_ts%3Dtrue%26cache_ts%3D0%26name_tagging%3Dtrue%26only_self_subteams%3Dtrue%26connect_only%3Dtrue%26ms_latest%3Dtrue&no_query_on_subscribe=1&flannel=3&lazy_channels=1&gateway_server=T09V59WQY1E-2&enterprise_id=E09V59WQY1E&batch_presence_aware=1"
        return url

    async def get_additional_headers(self) -> dict[str, str]:
        additional_headers: dict[str, str] = {
            "cookie": f"d={self.xoxd_token}",
        }
        return additional_headers

    def onevent(self, arg: Callable | str) -> Callable:
        """
        Events can be one of `on_start`
        Events can also be any Slack event type.
        """

        if isinstance(arg, str):

            def innerfunc(func: Callable) -> Callable:
                self.event_listeners.append((arg, func))
                return func

            return innerfunc

        self.event_listeners.append((None, arg))
        return arg

    async def connect(self):
        url = await self.get_url()
        headers = await self.get_additional_headers()
        async with websockets.connect(url, additional_headers=headers) as websocket:
            for event, callable in self.event_listeners:
                if event == "on_startup" or event is None:
                    await callable(event="on_startup", websocket=websocket)
            while True:
                response = await websocket.recv()
                data = json.loads(response)
