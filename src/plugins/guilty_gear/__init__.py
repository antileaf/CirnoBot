import nonebot
from nonebot import on_command

import datetime

from typing import Dict, List, Tuple, Set, Union

from ... import kit
from ...kit import nb as nbkit
from ...kit.nb import message as mskit

from .my_config import Config
from . import characters

global_config = nonebot.get_driver().config
config = Config.parse_obj(global_config)

__plugin_meta__ = kit.nb.plugin.metadata(
    name = '罪恶装备对位胜率',
    description = '查询各个角色的对位胜率',
    usage = '.gg 角色1 角色2：查询角色1对角色2的胜率\n.gg 角色：查询角色对位所有角色的胜率\n.gg list：查询角色列表',
    extra = {
        'command' : 'gg',
        'alias' : {'ggm', 'matchup', 'gg_matchup'}
    }
)


last_time : datetime.datetime = datetime.datetime.now()
win_rate : Dict[str, Dict[str, str]] = {}

async def update_table(event : Union[mskit.GroupMessageEvent, mskit.PrivateMessageEvent]):
    global last_time, win_rate

    now = datetime.datetime.now()
    if not win_rate or now.date() != last_time.date():
        await mskit.send_reply(message = '正在更新，请稍等……', event = event, at = False)

        last_time = now
        win_rate = characters.get_win_rate()


gg_matchup = on_command('matchup', aliases = __plugin_meta__.extra['alias'], priority = 5)

@gg_matchup.handle()
async def gg_matchup_handler(event : Union[mskit.GroupMessageEvent, mskit.PrivateMessageEvent], args : mskit.Message = mskit.params.CommandArg()):
    group_id = event.group_id if isinstance(event, mskit.GroupMessageEvent) else 0
    user_id = event.user_id
    
    args_list = str(args).split()

    name : List[str] = ['', '']
    cap : List[str] = ['', '']

    wrong_usage = False
    not_found = [False, False]
    list_all = False

    if len(args_list) == 1:
        if args_list[0] == 'list':
            list_all = True
        else:
            for i in range(1):
                name[i] = characters.get_name(str(args_list[i]))
                
                if name[i]:
                    cap[i] = characters.get_cap_short_name(name[i])
                else:
                    not_found[i] = True

    elif len(args_list) == 2:
        for i in range(2):
            if args_list[i] == 'list':
                wrong_usage = True
                break

            name[i] = characters.get_name(str(args_list[i]))
            
            if name[i]:
                cap[i] = characters.get_cap_short_name(name[i])
            else:
                not_found[i] = True

    else:
        wrong_usage = True

    if wrong_usage:
        await mskit.send_reply(message = '用法：' + __plugin_meta__.usage, event = event)

    elif list_all:
        await mskit.send_reply(message = '角色列表如下：\n' + '\n'.join([f'{k} ({v[1]})' for k, v in characters.tbl.items()]), event = event)
    
    elif not_found[0] or not_found[1]:
        await mskit.send_reply(message = '未找到角色 ' + ' 与 '.join([f'\"{args_list[i]}\"' for i in range(2) if not_found[i]]) + '\n如果需要，可以使用 .matchup list 查询角色列表', event = event)
    
    else:
        await update_table(event = event)

        # nonebot.logger.debug(f'win_rate: {win_rate}')
        # print(f'win_rate: {win_rate}', file = open('log.txt', 'w'))

        if name[1]:
            await mskit.send_reply(message = f'{name[0]} 对 {name[1]} 的胜率为：{win_rate[cap[0]][cap[1]]}', event = event)
        else:
            table : List[Tuple[str, str]] = [(characters.get_name(k), v) for k, v in win_rate[cap[0]].items()]
            
            table.sort(key = lambda x : (x[1], -characters.names.index(x[0])), reverse = True)

            await mskit.send_reply(message = f'{name[0]} 的对位胜率如下：\n' + '\n'.join([f'{i + 1}. vs {k}：{v}' for i, (k, v) in enumerate(table)]), event = event)