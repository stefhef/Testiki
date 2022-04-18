import os
from typing import Any
from vk_api.utils import get_random_id
import vk_api
from until import chunkify

TOKEN = os.environ.get('TOKEN_VK')

vk_session = vk_api.VkApi(
    token=TOKEN)
vk = vk_session.get_api()


async def vk_send_message(text: Any, users_ids: list) -> None:
    for users_ids in chunkify(users_ids, 100):
        vk.messages.send(peer_ids=','.join(users_ids),
                         message=text,
                         random_id=get_random_id())
