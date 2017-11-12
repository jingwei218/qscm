from channels.routing import route
from demo9 import consumers


channel_routing = [
    route("websocket.connect", consumers.ws_connect),
    route('push-msg', consumers.push_message),
]
