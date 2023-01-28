import nonebot
from nonebot import on_command
from nonebot.plugin import Plugin

import json, httpx, datetime

nonebot.require('nonebot_plugin_apscheduler')
from nonebot_plugin_apscheduler import scheduler

from typing import Dict, List, Tuple, Set, Union

from ... import kit
from ...kit.nb import message as mskit

from .my_config import Config
from . import subscribe_manager

global_config = nonebot.get_driver().config
config = Config.parse_obj(global_config)

__plugin_meta__ = kit.nb.plugin.metadata(
    name = '历史上的今天',
    description = '随机获得一张二次元美图',
    usage = '.today 历史上的今天\n.today subscribe 订阅每日推送\n.today unsubscribe 取消订阅\n.today check 检查订阅状态',
    extra = {'alias' : {'历史上的今天'}}
)

# 以下部分复制于 AquamarineCyan/nonebot-plugin-today-in-history、
# 参见：https://github.com/AquamarineCyan/nonebot-plugin-today-in-history/blob/master/nonebot_plugin_today_in_history/__init__.py
def text_handle(text: str):
    text = text.replace("<\/a>", "")
    text = text.replace("\n", "")

    # 去除html标签
    while True:
        address_head = text.find("<a target=")
        address_end = text.find(">", address_head)
        if address_head == -1 or address_end == -1:
            break
        text_middle = text[address_head:address_end + 1]
        text = text.replace(text_middle, "")

    # 去除api返回内容中不符合json格式的部分
    # 去除key:desc值
    address_head: int = 0
    while True:
        address_head = text.find('"desc":', address_head)
        address_end = text.find('"cover":', address_head)
        if address_head == -1 or address_end == -1:
            break
        text_middle = text[address_head + 8:address_end - 2]
        address_head = address_end
        text = text.replace(text_middle, "")

    # 去除key:title中多引号
    address_head: int = 0
    while True:
        address_head = text.find('"title":', address_head)
        address_end = text.find('"festival"', address_head)
        if address_head == -1 or address_end == -1:
            break
        text_middle = text[address_head + 9:address_end - 2]
        if '"' in text_middle:
            text_middle = text_middle.replace('"', " ")
            text = text[:address_head + 9] + \
                text_middle + text[address_end - 2:]
        address_head = address_end

    data = json.loads(text)
    return data


last_date = datetime.date.today()
history_str = ''

async def get_history_info() -> bool:
    global history_str

    if history_str and datetime.date.today() == last_date:
        return True # 今天已经更新过了

    async with httpx.AsyncClient() as client:
        month = datetime.date.today().strftime("%m")
        day = datetime.date.today().strftime("%d")
        url = f"https://baike.baidu.com/cms/home/eventsOnHistory/{month}.json"

        r = await client.get(url)
        if r.status_code != 200:
            return False
        
        r.encoding = "unicode_escape"
        data = text_handle(r.text)
        today = f"{month}{day}"

        s = f"历史上的今天 {month.lstrip('0')}月{day.lstrip('0')}日：\n"
        len_max = len(data[month][month + day])
        for i in range(0, len_max):
            str_year = data[month][today][i]["year"]
            str_title = data[month][today][i]["title"]
            if i == len_max - 1:
                s = s + f"{str_year}年 {str_title}"  # 去除段末空行
            else:
                s = s + f"{str_year}年 {str_title}\n"

        history_str = s
        return True


@scheduler.scheduled_job('cron', hour = 0, minute = 0)
async def daily_update():
    await get_history_info()

    for group_id in subscribe_manager.group.all():
        await mskit.send_group_message(group_id = group_id, message = history_str)
    
    for user_id in subscribe_manager.user.all():
        await mskit.send_private_message(user_id = user_id, message = history_str)


today_in_history = on_command('today', aliases = __plugin_meta__.extra['alias'])

@today_in_history.handle()
async def tih_handler(event : Union[mskit.GroupMessageEvent, mskit.PrivateMessageEvent], args : mskit.Message = mskit.params.CommandArg()):
    group_id = event.group_id if isinstance(event, mskit.GroupMessageEvent) else 0
    user_id = event.user_id
    
    args_list = args.extract_plain_text().split()

    wrong_usage = False

    if len(args_list) > 1:
        wrong_usage = True

    elif len(args_list) == 1:
        cmd = args_list[0]

        if cmd == 'subscribe' or cmd == 'unsubscribe':
            if group_id and not await subscribe_manager.check_permission(group_id = group_id, user_id = user_id):
                flag, msg = False, '只有超级用户或管理员可以操作群订阅'
            
            else:
                if cmd == 'subscribe':
                    flag, msg = subscribe_manager.subscribe(group_id = group_id, user_id = 0 if group_id else user_id)
                elif cmd == 'unsubscribe':
                    flag, msg = subscribe_manager.unsubscribe(group_id = group_id, user_id = 0 if group_id else user_id)
                else:
                    msg = '我谔谔'
        
        elif cmd == 'check':
            flag = subscribe_manager.has_subscribed(group_id = group_id, user_id = 0 if group_id else user_id)
            msg = '{}{}订阅历史上的今天'.format('本群' if group_id else '你', '已' if flag else '尚未')
        else:
            wrong_usage = True
            msg = '我谔谔'
        
        if not wrong_usage:
            await mskit.send_reply(message = msg, event = event)
        
    elif len(args_list) == 0:
        flag = await get_history_info()
        
        if flag:
            await mskit.send_reply(message = history_str, event = event)
        else:
            await mskit.send_reply(message = '出错了，请稍后再试或联系管理', event = event)

    
    if wrong_usage:
        await mskit.send_reply(message = '参数有误，用法如下：\n' + __plugin_meta__.usage, event = event)