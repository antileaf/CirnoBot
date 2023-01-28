import nonebot
from nonebot import on_command
from nonebot.plugin import Plugin

import datetime

from typing import Dict, List, Tuple, Set, Union

from .my_config import Config

from ... import kit
from ...kit.nb import message as mskit


global_config = nonebot.get_driver().config
config = Config.parse_obj(global_config)

__plugin_meta__ = kit.nb.plugin.metadata(
    name = '涩图',
    description = '随机获得一张二次元美图',
    usage = '.setu',
    extra = {'alias' : {'涩图', '色图', '美图', '图'}}
)


last_time : Dict[int, datetime.datetime] = dict()

setu = on_command('setu', aliases = {'涩图', '色图', '美图', '图'}, priority = config.priority)

@setu.handle()
async def setu_handler(event : Union[mskit.GroupMessageEvent, mskit.PrivateMessageEvent]):
    group_id = event.group_id if isinstance(event, mskit.GroupMessageEvent) else 0
    user_id = event.user_id
    
    if user_id in last_time:
        if last_time[user_id] + datetime.timedelta(seconds = config.sep) > datetime.datetime.now():
            await mskit.send_reply(message = f'{config.sep} 秒内只能看一张图哦…', event = event)
            return
    
    last_time[user_id] = datetime.datetime.now()

    await mskit.send_reply(message = mskit.ms.image(file = 'https://1mg.obfs.dev/', cache = False), event = event)