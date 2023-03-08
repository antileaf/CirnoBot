import nonebot
from nonebot import on_command, on_message
# from nonebot.adapters import Bot, Event
from nonebot.plugin import Plugin

from typing import Dict, List, Tuple, Set, Union
import datetime

from .my_config import Config

from ... import kit
from ...kit.nb import message as mskit


global_config = nonebot.get_driver().config
config = Config.parse_obj(global_config)

__plugin_meta__ = kit.nb.plugin.metadata(
    name = '我要妹子',
    description = '存储美图，或者随机返回一张本群或全局已存储美图',
    usage = f'回复某条图片消息，回复内容需包含 \".wymz\"',
    extra = {
        'command': 'wymz',
        'alias' : {'美图', '存图', 'meizi', 'maze'}
    }
)


def get_current_time_string() -> str:
    return datetime.datetime.now().strftime('%Y%m%d-%H%M%S')


woyaomeizi = on_message(priority=1, block=False)

@woyaomeizi.handle()
async def handle_woyaomeizi(event : mskit.GroupMessageEvent, bot : mskit.Bot):
    group_id = event.group_id
    user_id = event.user_id
    
    if not event.message.count('reply'):
        return
    
    if not any([event.message.count(value = '.' + keyword)
                for keyword in
                [__plugin_meta__.extra['command']] + __plugin_meta__.extra['alias']]):
        return
    
    id = event.message[0].data['id']
    rep = await bot.get_msg(message_id = id)

    if not rep.message.count('image'):
        await mskit.send_reply(message = '这里面没有图片哦', event = event)
        return
    
    success_count = 0
    fail_count = 0

    for image in rep.message['image']:
        url = image['url']

        if kit.net.save_image(url = url, path = f'./data/wymz/{group_id}/{get_current_time_string()}.jpg'):
            success_count += 1
        else:
            fail_count += 1
    
    if success_count > 0:
        await mskit.send_reply(message = f'已存储 {success_count} 张图片', event = event)
    
    if fail_count > 0:
        await mskit.send_reply(message = f'警告：有 {fail_count} 张图片存储失败', event = event)
