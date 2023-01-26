import nonebot
from nonebot import get_driver, on_message
from nonebot.adapters import Bot, Message, Event

from typing import Dict, List, Tuple

from ..kit import message as message_kit

from .my_config import Config


global_config = get_driver().config
config = Config.parse_obj(global_config)


last_message : Dict[int, str] = dict()
repeat_count : Dict[int, int] = dict()

@on_message(rule = message_kit.is_group_message, priority = config.priority).handle()
async def repeater(bot : Bot, event : Event):
    nonebot.logger.debug('qwq? event.get_message() = ' + str(event.get_message()))

    _, group_id, user_id = message_kit.evaluate_group_message(event)
    
    if not group_id in last_message:
        last_message[group_id] = ''
        repeat_count[group_id] = 0
    
    msg = str(event.get_message())
    
    if msg == last_message[group_id]:
        repeat_count[group_id] += 1

        if repeat_count[group_id] == config.repeat_times:
            await bot.send_group_msg(group_id = group_id, message = event.get_message())
    
    else:
        last_message[group_id] = msg
        repeat_count[group_id] = 1

