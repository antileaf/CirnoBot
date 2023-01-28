import nonebot

from nonebot.adapters.onebot.v11 import MessageEvent as MessageEvent
from nonebot.adapters.onebot.v11 import GroupMessageEvent as GroupMessageEvent
from nonebot.adapters.onebot.v11 import PrivateMessageEvent as PrivateMessageEvent
from nonebot.adapters.onebot.v11 import Message as Message
from nonebot.adapters.onebot.v11 import MessageSegment as MessageSegment
from nonebot.adapters.onebot.v11 import MessageSegment as ms

import json

async def is_group_admin_or_owner(user_id : int, group_id : int) -> bool:
    info = dict(await nonebot.get_bot().get_group_member_info(group_id = group_id, user_id = user_id, no_cache = True)) # ['data']
    
    return info['role'] == 'owner' or info['role'] == 'admin'