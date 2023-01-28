import nonebot
from nonebot import on_command
# from nonebot.adapters import Bot, Event
from nonebot.plugin import Plugin

from typing import Dict, List, Tuple, Set, Union

from .my_config import Config

from ... import kit
from ...kit.nb import message as mskit


global_config = nonebot.get_driver().config
config = Config.parse_obj(global_config)

__plugin_meta__ = kit.nb.plugin.metadata(
    name = '帮助',
    description = '获取插件描述与用法',
    usage = f'%help 插件 id（注意不是中文名）以查询插件帮助，或者 %help list 以查询所有可用的帮助'
)


def generate_availiable_helps() -> str:
    return '\n'.join([plugin.name + (f'（{plugin.metadata.name}）' if plugin.metadata else '') for plugin in nonebot.get_loaded_plugins()])


def generate_help_message(plugin : Plugin) -> str:
    message = plugin.name

    if plugin.metadata:
        md = plugin.metadata

        if md.name:
            message += f'\n名称：{md.name}'
        if md.description:
            message += f'\n描述：{md.description}'
        if md.usage:
            message += f'\n用法：{md.usage}'
        if 'alias' in md.extra:
            message += '\n别名：{}'.format(' '.join(list(md.extra['alias'])))
    
    else:
        message = f'插件 \"{message}\" 未提供帮助信息'
    
    return message


cirno_help = on_command('help', aliases = {'帮助', 'man'})

@cirno_help.handle()
async def cirno_help_handler(matcher : kit.nb.matcher.Matcher, event : Union[mskit.GroupMessageEvent, mskit.PrivateMessageEvent], args : mskit.Message = mskit.params.CommandArg()):
    group_id = event.group_id if isinstance(event, mskit.GroupMessageEvent) else 0
    user_id = event.user_id

    args_list = str(args).split()

    if len(args_list) == 1:
        name = str(args_list[0])

        if name == 'list':
            await mskit.send_reply(message = '可用的帮助：\n' + generate_availiable_helps(), event = event)
        else:
            plugin = nonebot.get_plugin(name)
            if not plugin:
                await mskit.send_reply(message = f'没有找到插件 \"{name}\"。\n可用的帮助：\n' + generate_availiable_helps(), event = event)
            else:
                await mskit.send_reply(message = generate_help_message(plugin), event = event)

    else:
        await mskit.send_reply(message = '用法：' + __plugin_meta__.usage, event = event)
    
    # !!! block !!!
    matcher.stop_propagation()