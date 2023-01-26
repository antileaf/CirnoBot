import nonebot

from typing import Dict, List, Tuple, Set, Union

from .my_config import Config

from ... import kit
from ...kit import request as rqkit
# from ...kit import message as mskit


global_config = nonebot.get_driver().config
config = Config.parse_obj(global_config)

__plugin_meta__ = kit.plugin.metadata(
    name = '自动加好友',
    description = '自动同意好友请求',
    usage = ''
)


friend_request = nonebot.on_request(rule = lambda event : isinstance(event, rqkit.FriendRequestEvent), priority = 114)

@friend_request.handle()
async def friend_request_handler(bot : kit.Bot, event : rqkit.FriendRequestEvent):
    await event.approve(bot = bot)
    
    await bot.send_private_msg(message = f'已添加好友 {event.user_id}', user_id = config.notice_qq)