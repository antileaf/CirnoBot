import nonebot
from nonebot import get_driver, on_message
# from nonebot.adapters import Bot, Message, Event

from typing import Dict, List, Tuple

from ... import kit
from ...kit.nb import message as mskit

from .my_config import Config


global_config = get_driver().config
config = Config.parse_obj(global_config)

__plugin_meta__ = kit.nb.plugin.metadata(
    name = '复读机',
    description = '',
    usage = f'在复读次数到达第 {config.repeat_times} 次时，加入复读。'
)

repeater = on_message(rule = mskit.is_group_message,
priority = config.priority)


last_message : Dict[int, str] = dict()
repeat_count : Dict[int, int] = dict()

@repeater.handle()
async def repeater_handler(bot : kit.nb.Bot, event : mskit.GroupMessageEvent):
    group_id, user_id = event.group_id, event.user_id
    
    if not group_id in last_message:
        last_message[group_id] = ''
        repeat_count[group_id] = 0
    
    msg = str(event.get_message())
    
    if msg == last_message[group_id]:
        repeat_count[group_id] += 1

        if repeat_count[group_id] == config.repeat_times:
            await bot.send(event = event, message = event.get_message())
    
    else:
        last_message[group_id] = msg
        repeat_count[group_id] = 1

