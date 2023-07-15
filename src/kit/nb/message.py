import nonebot

from nonebot.adapters import Event, MessageSegment, Bot

from nonebot.adapters.onebot.v11 import MessageEvent as MessageEvent
from nonebot.adapters.onebot.v11 import GroupMessageEvent as GroupMessageEvent
from nonebot.adapters.onebot.v11 import PrivateMessageEvent as PrivateMessageEvent
from nonebot.adapters.onebot.v11 import Message as Message
from nonebot.adapters.onebot.v11 import MessageSegment as MessageSegment
from nonebot.adapters.onebot.v11 import MessageSegment as ms

import nonebot.params as params

from typing import List, Tuple, Set, Union

def at(user_id : int) -> MessageSegment:
    return ms.at(user_id)

async def is_group_message(event : Event) -> bool:
    return isinstance(event, GroupMessageEvent)

    # return event.get_type() == 'message' and \
    #     event.get_session_id().startswith('group')

# group_id, user_id
# def evaluate_group_message(event : GroupMessageEvent) -> Tuple[int, int]:

#     return (event.group_id, event.user_id)

    # a : List[str | int] = list(event.get_session_id().split("_"))
    # return str(a[0]), int(a[1]), int(a[2])
    

async def send_reply(message : Union[Message, MessageSegment, str], event : Event, at : bool = True):
    if at and isinstance(event, GroupMessageEvent) and event.user_id != 80000000:
        message = ms.at(event.user_id) + ' ' + message

    await nonebot.get_bot().send(event = event, message = message)


async def send_private_message(user_id : int, message : Union[Message, MessageSegment, str]):
    await nonebot.get_bot().send_private_msg(user_id = user_id, message = message)

async def send_group_message(group_id : int, message : Union[Message, MessageSegment, str]):
    await nonebot.get_bot().send_group_msg(group_id = group_id, message = message)
