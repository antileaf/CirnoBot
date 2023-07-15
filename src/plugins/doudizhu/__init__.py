# -*- coding: utf-8 -*-

import nonebot
from nonebot import on_command
from nonebot.plugin import Plugin

from typing import Dict, List, Tuple, Set, Union

from .my_config import Config

from ... import kit
from ...kit.nb import message as mskit

from typing import Dict, List, Tuple, Set, Union
import random, math
import datetime

from .statistics import *

global_config = nonebot.get_driver().config
config = Config.parse_obj(global_config)

__plugin_meta__ = kit.nb.plugin.metadata(
    name = '斗地主',
    description = '打牌',
    usage = '你先别急',
    extra = {
        'command' : 'doudizhu',
        'alias' : {'doudizhu'}
    }
)

# 没有card类，用一个字符串取代之
# 方便起见，写一个类用于保存一手牌

def completed(s : str) -> str:
    t = ''
    for c in s:
        t += c
        if c == '1':
            t += '0'
    return t

def simplified(s : str) -> str:
    t = ''
    for i in range(len(s)):
        if i:
            if s[i] == '王' and (s[i - 1] == '大' or s[i - 1] == '小'):
                continue
            if s[i] == '0':
                if s[i - 1] == '1':
                    continue
                else:
                    return 'error'
            elif s[i] == '1':
                if i == len(s) - 1 or s[i + 1] != '0':
                    return 'error'

        c = s[i]
        if not c in '34567891JQKA2鬼王小大':
            return 'error'
        
        if c == '小':
            t += '鬼'
        elif c == '大':
            t += '王'
        else:
            t += c
        
    return t

def compare(a, b): # a < b
    if b == '王':
        return True
    if a == '王':
        return False
    if b == '鬼':
        return True
    if a == '鬼':
        return False
    
    s = '34567891JQKA2'
    return s.index(a) < s.index(b)

class Combination:
    def __init__(self, major : str, minor : str, typ : str):
        self.major = major
        self.minor = minor # 次要牌不参与比较大小，因此原样存储
        self.type = typ
        '''
        single, double, triple, triple1, triple2, 单张，对子，三张，三带一，三带二
        quadruple, quadruple2, quadruple22, 炸弹，四带二，四带两对
        serial, 2serial, 3serial, 3serial1, 3serial2, 顺子，连对，飞机，飞机带一张，飞机带两张
        rocket 火箭
        '''

    def __str__(self):
        if self.type == 'single':
            return self.major
        elif self.type == 'double':
            return self.major * 2
        elif self.type == 'triple' or self.type == 'triple1' or self.type == 'triple2':
            return self.major * 3 + self.minor
        elif self.type == 'quadruple' or self.type == 'quadruple2' or self.type == 'quadruple22':
            return self.major * 4 + self.minor
        elif self.type == 'serial':
            return self.major
        elif self.type == '2serial':
            return ''.join([c * 2 for c in self.major])
        elif self.type == '3serial' or self.type == '3serial1' or self.type == '3serial2':
            return ''.join([c * 3 for c in self.major]) + self.minor
        elif self.type == 'rocket':
            return self.major
    
    def check(self, other): # 判断other能否大过self
        if self.type == 'rocket':
            return 'smaller'

        if self.type != other.type:
            if other.type == 'quadruple' or other.type == 'rocket':
                return 'bigger'
            return 'different type'
        
        if 'serial' in self.type and len(self.major) != len(other.major):
            return 'different type'
        
        if compare(self.major[0], other.major[0]):
            return 'bigger'
        else:
            return 'smaller'



def handle(string : str): # 返回处理好的一手牌，或者'error'
    s = list(string)
    s.sort(key = lambda x : '34567891JQKA2鬼王'.find(x))
    s = ''.join(s)

    if len(s) == 1:
        return Combination(s, '', 'single')

    elif len(s) == 2:
        if s[0] == s[1]:
            return Combination(s[0], '', 'double')
        elif s[0] == '鬼' and s[1] == '王':
            return Combination(s, '', 'rocket')
        else:
            return 'error'
    
    elif len(s) == 3:
        if s[0] == s[1] and s[1] == s[2]:
            return Combination(s[0], '', 'triple')
        else:
            return 'error'

    elif len(s) == 4:
        if s[1] == s[2] and s[2] == s[3]:
            # s[0], s[3] = s[3], s[0]
            s = s[3] + s[1:3] + s[0]

        if s[0] == s[1] and s[1] == s[2]:
            if s[2] == s[3]:
                return Combination(s[0], '', 'quadruple')
            else:
                return Combination(s[0], s[3], 'triple1')
        else:
            return 'error'

    elif len(s) == 5:
        if s[2] == s[3] and s[3] == s[4]:
            # s[0], s[1], s[3], s[4] = s[3], s[4], s[0], s[1]
            s = s[3] + s[4] + s[2] + s[0] + s[1]

        if s[0] == s[1] and s[1] == s[2] and s[3] == s[4]:
            return Combination(s[0], s[3] * 2, 'triple2')
        
    elif len(s) == 6:
        if s[1] == s[2] and s[2] == s[3] and s[3] == s[4]:
            s = s[1:] + s[:1]
        if s[2] == s[3] and s[3] == s[4] and s[4] == s[5]:
            s = s[2:] + s[:2]
        if s[0] == s[1] and s[1] == s[2] and s[2] == s[3]:
            return Combination(s[0], s[4] + s[5], 'quadruple2')
    
    elif len(s) == 8:
        for i in range(2):
            if s[0] == s[1] and s[1] != s[2]:
                s = s[2:] + s[:2]
        
        if s[0] == s[1] and s[1] == s[2] and s[2] == s[3] and s[4] == s[5] and s[6] == s[7]:
            return Combination(s[0], s[4:], 'quadruple22')
        
    s = list(s)
    s.sort(key = lambda x : '34567891JQKA2鬼王'.find(x))
    s = ''.join(s)
        
    if s in '34567891JQKA' and len(s) >= 5:
        return Combination(s, '', 'serial')
    if s[0::2] == s[1::2]:
        t = ''.join(s[0::2])
        if t in '34567891JQKA' and len(t) >= 3:
            return Combination(t, '', '2serial')
    
    v = [0] * len('34567891JQKA2鬼王')
    for c in s:
        v['34567891JQKA2鬼王'.find(c)] += 1
    d = [[] for i in range(54)]
    for i in range(len(v)):
        d[v[i]].append('34567891JQKA2鬼王'[i])

    if len(d[3]) >= 2:
        k = ''.join(d[3])
        if not k in '34567891JQKA':
            return 'error'

        if len(s) == 3 * len(d[3]):
            return Combination(''.join(d[3]), '', '3serial')
        if len(s) == 4 * len(d[3]):
            return Combination(''.join(d[3]), ''.join([c if not c in d[3] else '' for c in s]), '3serial1')
        if len(s) == 3 * len(d[3]) + 2 * len(d[2]):
            return Combination(''.join(d[3]), ''.join([c * 2 for c in d[2]]), '3serial2')
    
    return 'error'

async def check_and_create(group_id : int, user_id : int):
    if check_user(group_id, user_id):
        return
    
    info = await nonebot.get_bot().get_group_member_info(group_id = group_id, user_id = user_id)

    name = info['card']
    if name == '':
        name = info['nickname']
    if name == '':
        name = str(user_id)
    
    create_user(group_id, user_id, name)
    

class Player:
    def __init__(self):
        self.hand = ''
        self.type = '未知'
        self.bujiao = False
        self.pub = False
    
    def check(self, s):
        t = self.hand[:]
        for c in s:
            if not c in t:
                return False
            p = t.find(c)
            t = t[:p] + t[p + 1:]
        return True
    
    def play(self, s):
        t = self.hand[:]
        for c in s:
            if not c in t:
                return False
            p = t.find(c)
            t = t[:p] + t[p + 1:]
        self.hand = t
    
    def join(self, s):
        self.hand += s
        self.sort()
    
    def sort(self):
        self.hand = ''.join(sorted(list(self.hand), key = lambda x : '34567891JQKA2鬼王'.index(x)))
    
    def get_hand(self):
        return completed(' '.join(list(self.hand)))

class Game:
    def __init__(self):
        self.players : List[int] = []
        self.tbl : Dict[int, Player] = dict()
        self.cur : int = 0
        self.cur_player : int = 0
        self.last_step : Combination | None = None
        self.last_player : int = 0
        self.state : str = ''
        self.deck : str = ''
        self.score : int = 0
        self.first_cnt : int = 0

    def next_player(self):
        self.cur = (self.cur + 1) % len(self.players)
        self.cur_player = self.players[self.cur]

    def prepare(self):
        random.shuffle(self.players)

        for i in self.players:
            self.tbl[i] = Player()

        deck_list = list('鬼王' + '34567891JQKA2' * 4)
        random.shuffle(deck_list)
        self.deck = ''.join(deck_list)

        for i in range(17):
            for j in self.players:
                self.tbl[j].join(self.deck[0])
                self.deck = self.deck[1:]
        
        # 剩下三张底牌
        self.cur = random.randint(0, 2)
        self.cur_player = self.players[self.cur]
        self.last_player = self.cur_player

        self.score = 10

        return random.choice(list(self.tbl[self.cur_player].hand)) # 从抽中明牌者开始叫地主
    
    def clear(self):
        self.players = []
        self.tbl.clear()

games : Dict[int, Game] = dict()

last_time = datetime.datetime.now()

def update_time():
    global last_time

    last_time = datetime.datetime.now()

def check_time() -> bool:
    return last_time + datetime.timedelta(minutes = 5) <= datetime.datetime.now()


# @on_plugin('loading')
# def initialize():
#     load_stat()

#     update_time()


@on_command('开始游戏', aliases = {'开始', '开局', 'ks'}, rule = mskit.is_group_message).handle()
async def kaiju(event : mskit.GroupMessageEvent):
    group_id = event.group_id
    user_id = event.user_id

    # if not group_id:
    #     await session.send('请在群聊中使用斗地主功能')
    #     return
    
    if user_id == 80000000:
        await mskit.send_reply(message = '请解除匿名后再使用斗地主功能', event = event, at = False)
        return
    
    if not group_id in games or not user_id in games[group_id].players:
        await mskit.send_reply(message = '你没有加入当前游戏', event = event)
        return
    
    g = games[group_id]

    if len(g.players) < 3:
        await mskit.send_reply(message = '人数不足，无法开始', event = event)
        return

    if g.state:
        await mskit.send_reply(message = '游戏已开始', event = event)
        return
    
    card = g.prepare()
    for i in g.players:
        await mskit.send_private_message(user_id = i, message = g.tbl[i].get_hand())

    g.state = 'jdz'
    s = '游戏已开始！\n玩家列表：'
    for i in g.players:
        s = s + ' ' + mskit.at(i)
    s = s + '\n' + mskit.at(g.cur_player) + ' 抽到了明牌' + completed(card) + '，请决定是否叫地主'
    await mskit.send_reply(message = s, event = event, at = False)

    update_time()


@on_command('结束游戏', aliases = {'结束', 'js'}, rule = mskit.is_group_message).handle()
async def jieshu(event : mskit.GroupMessageEvent):
    group_id = event.group_id
    user_id = event.user_id

    # if not group_id:
    #     await session.send('请在群聊中使用斗地主功能')
    #     return
    
    if not check_time() and user_id != 1094054222:
        await mskit.send_reply(message = '无操作 5 分钟后才能使用此功能', event = event)
        return

    if not group_id in games:
        await mskit.send_reply(message = '游戏未开始', event = event)
        return
    
    games[group_id].clear()
    games.pop(group_id)
    await mskit.send_reply(message = '结束成功', event = event)

    update_time()


@on_command('改名', aliases = {'rename', 'gm'}, rule = mskit.is_group_message).handle()
async def gaiming(event : mskit.GroupMessageEvent, args : mskit.Message = mskit.params.CommandArg()):
    group_id = event.group_id
    user_id = event.user_id

    args_list = str(args).split()
    
    # if not group_id:
    #     await session.send('请在群聊中使用斗地主功能')
    #     return

    if user_id == 80000000:
        await mskit.send_reply(message = '请解除匿名后再使用斗地主功能', event = event, at = False)
        return
    
    if len(args_list) != 1:
        await mskit.send_reply(message = '用法：改名 + 你想要的名字(不要有空格)', event = event)
        return
    
    await check_and_create(group_id, user_id)

    change_name(group_id, user_id, args_list[0])
    
    await mskit.send_reply(message = '修改成功', event = event)


@on_command('改分', rule = mskit.is_group_message).handle()
async def gaifen(event : mskit.GroupMessageEvent, args : mskit.Message = mskit.params.CommandArg()):
    group_id = event.group_id
    user_id = event.user_id

    args_list = str(args).split()
    
    # if not group_id:
    #     await session.send('请在群聊中使用斗地主功能')
    #     return

    invalid = (len(args_list) == 2)
    name, new_mmr = '', 0
    try:
        name, new_mmr = args_list[0], int(args_list[1])
    except:
        invalid = True

    if user_id == 80000000:
        await mskit.send_reply(message = '请解除匿名后再使用斗地主功能', event = event, at = False)
        return
    
    if user_id != 1094054222:
        await mskit.send_reply(message = '只有绿可以使用此功能', event = event)
        return
    
    if invalid:
        await mskit.send_reply(message = '用法： 改分 + 名字/QQ + 分数', event = event)
        return
    
    u = get_userid(group_id, name)

    if not u:
        await mskit.send_reply(message = '未找到对应用户', event = event)
        return
    elif u == -1:
        await mskit.send_reply(message = '找到多个用户，请重新输入', event = event)
        return
    
    change_mmr(group_id, u, new_mmr)

    await mskit.send_reply(message = '修改成功', event = event)


@on_command('查询', aliases = {'cx'}, rule = mskit.is_group_message).handle()
async def chaxun(event : mskit.GroupMessageEvent, args : mskit.Message = mskit.params.CommandArg()):
    group_id = event.group_id
    user_id = event.user_id

    args_list = str(args).split()

    if user_id == 80000000:
        await mskit.send_reply(message = '请解除匿名后再查询', event = event, at = False)
        return
    
    # if not group_id:
    #     await mskit.send_reply(message = '请在群聊中使用斗地主功能')
    #     return
    
    if len(args_list) > 1:
        await mskit.send_reply(message = '用法： 查询\n 或： 查询 + QQ/at/名字', event = event)
        return

    name = args_list[0] if len(args_list) == 1 else ''
    
    u = get_userid(group_id, name) if name != '' else user_id

    if not u:
        s = '没有找到符合条件的用户，请重试'
    elif u == -1:
        s = '匹配到多个用户，请重新选择关键词'
    elif not check_exist(group_id, u):
        s = ('该用户' if u != user_id else '你') + '在本群还没有游戏记录'
    else:
        s = (get_name(group_id, u) if u != user_id else '你') + '的MMR： ' + str(get_mmr(group_id, u))

        s += '\n' + get_stat(group_id, u)

    await mskit.send_reply(message = s, event = event)


@on_command('更新', aliases = {'refresh', 'update', 'upd'}, rule = mskit.is_group_message).handle()
async def gengxin(event : mskit.GroupMessageEvent):
    group_id = event.group_id
    user_id = event.user_id

    if user_id != 1094054222:
        await mskit.send_reply(message = '只有绿可以使用此功能', event = event, at = (user_id != 80000000))
        return

    s = '此功能已弃用，请勿使用'

    await mskit.send_reply(message = s, event = event)


@on_command('修改', aliases = {'change', 'modify'}, rule = mskit.is_group_message).handle()
async def xiugai(event : mskit.GroupMessageEvent, args : mskit.Message = mskit.params.CommandArg()):
    global mmr_tbl

    group_id = event.group_id
    user_id = event.user_id

    if user_id != 1094054222:
        await mskit.send_reply(message = '只有绿可以使用此功能', event = event, at = (user_id != 80000000))
        return
    
    s = '此功能已弃用，请使用改分/改名命令'

    await mskit.send_reply(message = s, event = event)


@on_command('重置', aliases = {'clear'}, rule = mskit.is_group_message).handle()
async def chongzhi(event : mskit.GroupMessageEvent):
    global mmr_tbl

    group_id = event.group_id
    user_id = event.user_id

    if user_id != 1094054222:
        await mskit.send_reply(message = '只有绿可以使用此功能', event = event, at = (user_id != 80000000))
        return
    
    # if not group_id:
    #     await session.send('请在群聊中使用斗地主功能')
    #     return
    
    clear_group(group_id)

    await mskit.send_reply(message = '重置成功', event = event)

    update_time()
    

@on_command('排行榜', aliases = {'ranklist', 'rank', '排名', '榜', 'ph'}, rule = mskit.is_group_message).handle()
async def paihangbang(event : mskit.GroupMessageEvent, args : mskit.Message = mskit.params.CommandArg()):
    
    group_id = event.group_id
    user_id = event.user_id

    if user_id == 80000000:
        await mskit.send_reply(message = '请解除匿名后再查询', event = event, at = False)
        return
    
    # if not group_id:
    #     await session.send('请在群聊中使用斗地主功能')
    #     return
    
    a = get_ranklist(group_id)

    if not a:
        s = '本群还没有人玩过斗地主'
    else:
        s = '排行榜：'

        for o in a:
            try:
                info = await nonebot.get_bot().get_group_member_info(group_id = group_id, user_id = o[0])
            except: # 这个人退群了
                del_user(group_id, o[0])

                continue

            t = info['card']
            if t == '':
                t = info['nickname']
            if t == '':
                t = str(o[0])
            
            if t == o[1]:
                t = ''
            else:
                t = '(' + t + ')'

            s = s + '\n' + str(a.index(o) + 1) + '. ' + o[1] + t + '： ' + str(o[2])
    
    await mskit.send_reply(message = s, event = event)


@on_command('加入游戏', aliases = {'加入', 'jr', '上桌', 'sz'}, rule = mskit.is_group_message).handle()
async def jiaru(event : mskit.GroupMessageEvent):

    group_id = event.group_id
    user_id = event.user_id

    # if not group_id:
    #     await session.send('请在群聊中使用斗地主功能')
    #     return
    
    if user_id == 80000000:
        await mskit.send_reply(message = '请解除匿名后再使用斗地主功能', event = event, at = False)
        return
    
    if not group_id in games:
        games[group_id] = Game()
        
    g = games[group_id]

    if user_id in g.players:
        await mskit.send_reply(message = '你已经加入过了', event = event)
        return

    if g.tbl:
        await mskit.send_reply(message = '游戏已开始，无法加入', event = event)
        return
    
    if len(g.players) == 3:
        await mskit.send_reply(message = '人数已满，无法加入', event = event)
        return
    
    await check_and_create(group_id, user_id)
    
    g.players.append(user_id)

    s = '加入成功，当前共有%d人\n为正常进行游戏，请加bot为好友，bot会自动同意' % len(g.players)

    await mskit.send_reply(message = s, event = event)

    update_time()


@on_command('退出游戏', aliases = {'退出', '下桌', 'tc', 'xz'}, rule = mskit.is_group_message).handle()
async def tuichu(event : mskit.GroupMessageEvent):
    group_id = event.group_id
    user_id = event.user_id

    # if not group_id:
    #     await session.send('请在群聊中使用斗地主功能')
    #     return
    
    if user_id == 80000000:
        await mskit.send_reply(message = '请解除匿名后再使用斗地主功能', event = event, at = False)
        return
    
    if not group_id in games or not user_id in games[group_id].players:
        await mskit.send_reply(message = '你没有加入当前游戏', event = event)
        return
    
    g = games[group_id]
    
    if g.tbl:
        await mskit.send_reply(message = '游戏已开始，无法退出', event = event)
        return
        
    g.players.remove(user_id)

    await mskit.send_reply(message = '退出成功，当前还剩%d人' % len(g.players), event = event)

    if not g.players:
        games.pop(group_id)
    
    update_time()


@on_command('叫地主', aliases = {'叫', 'j', 'jdz'}, rule = mskit.is_group_message).handle()
async def jiaodizhu(event : mskit.GroupMessageEvent):
    group_id = event.group_id
    user_id = event.user_id

    # if not group_id:
    #     await session.send('请在群聊中使用斗地主功能')
    #     return
    
    if user_id == 80000000:
        await mskit.send_reply(message = '请解除匿名后再使用斗地主功能', event = event, at = False)
        return
    
    if not group_id in games or not user_id in games[group_id].players:
        await mskit.send_reply(message = '你没有加入当前游戏', event = event)
        return
    
    g = games[group_id]

    if not g.state:
        await mskit.send_reply(message = '游戏未开始', event = event)
        return
    
    if g.state == 'qdz':
        await mskit.send_reply(message = '现在是抢地主环节', event = event)
        return
    
    if g.state == 'started':
        return
    
    if g.cur_player != user_id:
        await mskit.send_reply(message = '还没有轮到你叫地主', event = event)
        return
    
    await mskit.send_reply(message = '选择叫地主', event = event)
    g.last_player = g.cur_player
    # g.tbl[g.cur_player].bujiao = True
    g.state = 'qdz'
    g.next_player()
    await mskit.send_reply('请 ' + mskit.at(g.cur_player) + ' 选择是否抢地主', event = event, at = False)

    update_time()


@on_command('不叫', aliases = {'bujiao', 'bj'}, rule = mskit.is_group_message).handle()
async def bujiao(event : mskit.GroupMessageEvent):
    group_id = event.group_id
    user_id = event.user_id

    # if not group_id:
    #     await session.send('请在群聊中使用斗地主功能')
    #     return
    
    if user_id == 80000000:
        await mskit.send_reply(message = '请解除匿名后再使用斗地主功能', event = event, at = False)
        return
    
    if not group_id in games or not user_id in games[group_id].players:
        await mskit.send_reply(message = '你没有加入当前游戏', event = event)
        return
    
    g = games[group_id]

    if not g.state:
        await mskit.send_reply(message = '游戏未开始', event = event)
        return
    
    if g.state == 'qdz':
        await mskit.send_reply(message = '现在是抢地主环节', event = event)
        return
    
    if g.state == 'started':
        return
    
    if g.cur_player != user_id:
        await mskit.send_reply(message = '还没有轮到你叫地主', event = event)
        return

    g.tbl[user_id].bujiao = True
    await mskit.send_reply(message = '选择不叫地主', event = event)
    g.next_player()

    if g.cur_player == g.last_player:

        s = '以下是各位玩家的手牌：'
        for i in g.tbl:
            s = s + '\n' + mskit.at(i) + '： ' + g.tbl[i].get_hand()
        s = s + '\n底牌是：' + ' '.join(g.deck)
        await mskit.send_reply(s, event = event, at = False)

        await mskit.send_reply('由于无人叫地主，本局流局，请重新加入并开始游戏', event = event, at = False)

        g.clear()
        games.pop(group_id)

        return

    await mskit.send_reply('请 ' + mskit.at(g.cur_player) + ' 选择是否叫地主', event = event, at = False)

    update_time()


@on_command('抢地主', aliases = {'抢', 'qiang', 'qdz', 'q'}, rule = mskit.is_group_message).handle()
async def qiangdizhu(event : mskit.GroupMessageEvent):
    group_id = event.group_id
    user_id = event.user_id

    # if not group_id:
    #     await session.send('请在群聊中使用斗地主功能')
    #     return
    
    if user_id == 80000000:
        await mskit.send_reply(message = '请解除匿名后再使用斗地主功能', event = event, at = False)
        return
    
    if not group_id in games or not user_id in games[group_id].players:
        await mskit.send_reply(message = '你没有加入当前游戏', event = event)
        return
    
    g = games[group_id]

    if not g.state:
        await mskit.send_reply(message = '游戏未开始', event = event)
        return
    
    if g.state == 'jdz':
        await mskit.send_reply(message = '还没到抢地主环节', event = event)
        return
    
    if g.state == 'started':
        return
    
    if g.cur_player != user_id:
        await mskit.send_reply(message = '还没有轮到你抢地主', event = event)
        return

    g.score *= 2

    await mskit.send_reply(message = '选择抢地主，分数翻倍\n当前分数：' + str(g.score), event = event)
    g.tbl[user_id].bujiao = True
    g.last_player = user_id

    ok = True
    for i in g.players:
        if not g.tbl[i].bujiao:
            ok = False
    if ok:
        dizhu = g.last_player

        g.tbl[dizhu].type = '地主'
        for i in g.tbl:
            if i != dizhu:
                g.tbl[i].type = '农民'
        
        await mskit.send_reply(mskit.at(dizhu) + ' 成为了地主！\n底牌是：' + \
                           ' '.join(map(completed, list(g.deck))), event = event, at = False)
        g.tbl[dizhu].join(g.deck)
        await mskit.send_private_message(user_id = dizhu, message = g.tbl[dizhu].get_hand())
        # g.deck = ''

        g.state = 'started'

        await mskit.send_reply('请地主 ' + mskit.at(dizhu) + ' 开始出牌', event = event, at = False)
        g.cur_player = g.last_player = dizhu
        g.cur = g.players.index(dizhu)

        update_time()

        return

    g.next_player()
    while g.tbl[g.cur_player].bujiao:
        g.next_player()

    await mskit.send_reply('请 ' + mskit.at(g.cur_player) + ' 选择是否抢地主', event = event, at = False)

    update_time()


@on_command('不抢', aliases = {'buqiang', 'bq'}, rule = mskit.is_group_message).handle()
async def buqiang(event : mskit.GroupMessageEvent):
    group_id = event.group_id
    user_id = event.user_id

    # if not group_id:
    #     await session.send('请在群聊中使用斗地主功能')
    #     return
    
    if user_id == 80000000:
        await mskit.send_reply(message = '请解除匿名后再使用斗地主功能', event = event, at = False)
        return
    
    if not group_id in games or not user_id in games[group_id].players:
        await mskit.send_reply(message = '你没有加入当前游戏', event = event)
        return
    
    g = games[group_id]

    if not g.state:
        await mskit.send_reply(message = '游戏未开始', event = event)
        return
    
    if g.state == 'jdz':
        await mskit.send_reply(message = '还没到抢地主环节', event = event)
        return
    
    if g.state == 'started':
        return
    
    if g.cur_player != user_id:
        await mskit.send_reply(message = '还没有轮到你抢地主', event = event)
        return

    await mskit.send_reply(message = '选择不抢地主', event = event)
    g.tbl[user_id].bujiao = True

    ok = True
    for i in g.players:
        if not g.tbl[i].bujiao:
            ok = False
    if ok:
        dizhu = g.last_player

        g.tbl[dizhu].type = '地主'
        for i in g.tbl:
            if i != dizhu:
                g.tbl[i].type = '农民'
        
        await mskit.send_reply(mskit.at(dizhu) + ' 成为了地主！\n底牌是：' + \
                           ' '.join(map(completed, list(g.deck))), event = event, at = False)
        g.tbl[dizhu].join(g.deck)
        await mskit.send_private_message(user_id = dizhu, message = g.tbl[dizhu].get_hand())
        # g.deck = ''

        g.state = 'started'

        await mskit.send_reply('请地主 ' + mskit.at(dizhu) + ' 开始出牌', event = event, at = False)
        g.cur_player = g.last_player = dizhu
        g.cur = g.players.index(dizhu)

        update_time()

        return

    g.next_player()
    while g.tbl[g.cur_player].bujiao:
        g.next_player()

    await mskit.send_reply('请 ' + mskit.at(g.cur_player) + ' 选择是否抢地主', event = event, at = False)

    update_time()


@on_command('出', aliases = {'出牌', 'chu', 'c'}, rule = mskit.is_group_message).handle()
async def chu(event : mskit.GroupMessageEvent, args : mskit.Message = mskit.params.CommandArg()):
    global mmr_tbl, tmp_tbl

    group_id = event.group_id
    user_id = event.user_id

    args_list = str(args).split()

    # if not group_id:
    #     await session.send('请在群聊中使用斗地主功能')
    #     return
    
    if user_id == 80000000:
        await mskit.send_reply(message = '请解除匿名后再使用斗地主功能', event = event, at = False)
        return
    
    if not group_id in games or not user_id in games[group_id].players:
        await mskit.send_reply(message = '你没有加入当前游戏', event = event)
        return
    
    g = games[group_id]

    if g.state != 'started':
        await mskit.send_reply(message = '游戏未开始或未开始出牌', event = event)
        return
    
    if g.cur_player != user_id:
        await mskit.send_reply(message = '还没有轮到你出牌', event = event)
        return
    
    if len(args_list) != 1:
        await mskit.send_reply(message = '用法：出/chu/c + 你要出的牌(顺序随意，不要有空格)', event = event)
        return
    
    s = simplified(args_list[0])
    if s == 'error':
        await mskit.send_reply(message = '输入不合法', event = event)
        return

    v = handle(s)
    if v == 'error':
        await mskit.send_reply(message = '牌型不合法', event = event)
        return
    
    if not g.tbl[user_id].check(s):
        await mskit.send_reply(message = '你没有这些牌', event = event)
        return
    
    if g.last_player != user_id:
        assert g.last_step
        t = g.last_step.check(v)
        if t == 'different type':
            await mskit.send_reply(message = '牌型不符', event = event)
        elif t == 'smaller':
            await mskit.send_reply(message = '这牌盖不过刚才出的牌', event = event)
        if t != 'bigger':
            return
    
    update_time()

    if not g.first_cnt:
        g.first_cnt = len(s)
        
    g.tbl[user_id].play(s)

    t = ''
    if v.type == 'quadruple':
        t = '炸弹分数翻倍'
        g.score *= 2
    elif v.type == '3serial' or v.type == '3serial1' or v.type == '3serial2':
        t = '飞机分数翻%d倍' % len(v.major)
        g.score *= len(v.major)
    elif v.type == 'rocket':
        t = '火箭分数翻四倍'
        g.score *= 4
    
    if t:
        t = '\n' + t + '，当前分数：' + str(g.score)

    if not g.tbl[user_id].hand:
        await mskit.send_reply(message = '打出了：' + completed(str(v)) + t, event = event)
        await mskit.send_reply(message = '已经出完了所有牌！', event = event)
        
        s = ''
        for i in g.players:
            if g.tbl[i].type == g.tbl[user_id].type:
                if s:
                    s = s + '和'
                s = s + ' ' + mskit.at(i)
        
        await mskit.send_reply(message = g.tbl[user_id].type + s + ' 获得了胜利！', event = event, at = False)

        s = '以下是其他玩家的剩余手牌：'
        for i in g.players:
            if g.tbl[i].hand:
                s = s + '\n' + mskit.at(i) + ' ：' + g.tbl[i].get_hand()
                
        await mskit.send_reply(message = s, event = event, at = False)

        won = g.tbl[user_id].type == '地主'
        
        master = 0
        for i in g.players:
            if g.tbl[i].type == '地主':
                master = i
                break

        if won:
            spring = (sum([len(g.tbl[i].hand) for i in g.players]) == 2 * 17)
        else:
            spring = (len(g.tbl[master].hand) == 20 - g.first_cnt)
        
        delta = calc_delta(group_id, g.players, master, won, g.score)

        s = ''
        multiple = 1

        if spring:
            s = ('反' if not won else '') + '春天，分数最终翻2倍！\n'

            multiple *= 2
        
        cnt = sum([int(g.tbl[i].pub) for i in g.tbl])
        if cnt:
            s = s + '本局共有%d位玩家明牌，明牌玩家分数最终翻%d倍！\n' % (cnt, 2 ** cnt)
            multiple *= 2 ** cnt

        for i in g.tbl:
            if g.tbl[i].pub:
                delta[i] *= multiple

        s = s + '以下是各位玩家的MMR升降情况：'

        old, new = dict(), dict()

        for i in g.players:
            old[i] = get_mmr(group_id, i)
            new[i] = old[i] + delta[i]
            
            t = str(delta[i])
            if delta[i] >= 0:
                t = '+' + t

            s = s + '\n' + mskit.at(i) + '： %d -> %d (%s)' % (old[i], new[i], t)

        await mskit.send_reply(message = s, event = event, at = False)

        for i in g.players:
            update(group_id, i, i == master, (i == master) == won, save = False)
            change_mmr(group_id, i, new[i], save = False)
        
        save_stat()

        g.clear()
        games.pop(group_id)

        return

    
    s = g.tbl[user_id].type + ' ' + mskit.at(user_id) + ' 打出了：' + completed(str(v)) + '，还剩%d张牌' % len(g.tbl[user_id].hand)

    if g.tbl[user_id].pub:
        s = s + '\n剩余手牌：' + g.tbl[user_id].get_hand()

    await mskit.send_reply(message = s + t, event = event, at = False)

    await mskit.send_private_message(user_id = user_id, message = g.tbl[user_id].get_hand())

    g.last_step = v
    g.last_player = user_id

    g.next_player()

    s = '轮到 ' + g.tbl[g.cur_player].type + ' ' + mskit.at(g.cur_player) + ' 出牌，上一次出牌是 '+ g.tbl[g.last_player].type + ' ' + mskit.at(user_id) \
        + ' 出的：' + completed(str(v))
    await mskit.send_reply(message = s, event = event, at = False)


@on_command('过', aliases = {'pass', '不出', 'g', 'bc', 'p', 'by', '不要', 'ybq', '要不起'}, rule = mskit.is_group_message).handle()
async def buchu(event: mskit.GroupMessageEvent):
    group_id = event.group_id
    user_id = event.user_id

    # if not group_id:
    #     await session.send('请在群聊中使用斗地主功能')
    #     return
    
    if user_id == 80000000:
        await mskit.send_reply(message = '请解除匿名后再使用斗地主功能', event = event, at = False)
        return
    
    if not group_id in games or not user_id in games[group_id].players:
        await mskit.send_reply(message = '你没有加入当前游戏', event = event)
        return
    
    g = games[group_id]

    if g.state != 'started':
        await mskit.send_reply(message = '游戏未开始或未开始出牌', event = event)
        return
    
    if g.cur_player != user_id:
        await mskit.send_reply(message = '还没有轮到你出牌', event = event)
        return
    
    if g.last_player == user_id:
        await mskit.send_reply(message = '现在不能过牌', event = event)
        return

    update_time()
    
    g.next_player()

    s = g.tbl[user_id].type + ' ' + mskit.at(user_id) + '选择不出牌，还剩%d张牌' % len(g.tbl[user_id].hand)

    if g.tbl[user_id].pub:
        s = s + '\n剩余手牌：' + g.tbl[user_id].get_hand()

    await mskit.send_reply(message = s, event = event, at = False)
    
    s = '轮到 ' + g.tbl[g.cur_player].type + ' ' + mskit.at(g.cur_player) + ' 出牌，上一次出牌是 ' + g.tbl[g.last_player].type + ' ' + mskit.at(g.last_player) \
        + ' 出的：' + completed(str(g.last_step))
    await mskit.send_reply(message = s, event = event, at = False)


@on_command('明牌', aliases = {'mp'}, rule = mskit.is_group_message).handle()
async def mingpai(event: mskit.GroupMessageEvent):
    group_id = event.group_id
    user_id = event.user_id

    # if not group_id:
    #     await session.send('请在群聊中使用斗地主功能')
    #     return
    
    if user_id == 80000000:
        await mskit.send_reply(message = '请解除匿名后再使用斗地主功能', event = event, at = False)
        return
    
    if not group_id in games:
        await mskit.send_reply(message = '本群还没有人使用斗地主功能', event = event)
        return
    
    g = games[group_id]

    if not user_id in g.tbl:
        await mskit.send_reply(message = '你没有加入当前游戏', event = event)
        return
    
    if g.state != 'started':
        await mskit.send_reply(message = '只有公布底牌后才能明牌哦~', event = event)
        return
    
    if g.tbl[user_id].pub:
        await mskit.send_reply(message = '你已经明牌过了', event = event)
        return
    
    if g.last_step:
        await mskit.send_reply(message = '已经开始出牌了，不能明牌', event = event)
        return
    
    g.tbl[user_id].pub = True
    
    s = '明牌成功，最终分数翻倍！剩余手牌如下：\n' + g.tbl[user_id].get_hand()

    await mskit.send_reply(message = s, event = event)

    update_time()


@on_command('状态', aliases = {'zhuangtai', 'stat', 'status', 'zt'}, rule = mskit.is_group_message).handle()
async def zhuangtai(event: mskit.GroupMessageEvent):
    group_id = event.group_id
    user_id = event.user_id

    # if not group_id:
    #     await session.send('请在群聊中使用斗地主功能')
    #     return
    
    if user_id == 80000000:
        await mskit.send_reply(message = '请解除匿名后再使用斗地主功能', event = event, at = False)
        return
    
    if not group_id in games:
        await mskit.send_reply(message = '本群还没有人使用斗地主功能', event = event)
        return
    
    g = games[group_id]

    if not g.state:
        s = '斗地主未开始，当前等待中的玩家有：'
        for i in g.players:
            s = s + '\n' + mskit.at(i)
        
        await mskit.send_reply(message = s, event = event)

    elif g.state == 'jdz' or g.state == 'qdz':
        s = '斗地主已开始，当前玩家和MMR如下：'
        for i in g.players:
            s = s + '\n' + mskit.at(i) + ' MMR：%d' % get_mmr(group_id, i)
        
        s = s + '\n当前状态：等待 ' + mskit.at(g.cur_player) + ' ' + ('叫' if g.state == 'jdz' else '抢') + '地主'
        
        await mskit.send_reply(message = s, event = event)
    
    else:
        s = '斗地主已开始，当前玩家、手牌张数和MMR如下：'
        for i in g.players:
            s = s + '\n' + g.tbl[i].type + ' ' + mskit.at(i) + '：%d张 MMR：%d' % (len(g.tbl[i].hand), get_mmr(group_id, i))

            if g.tbl[i].pub:
                s = s + '\n剩余手牌：' + g.tbl[i].get_hand()
        
        s = s + '\n底牌是：' + ' '.join(map(completed, list(g.deck)))
        
        s = s + '\n当前状态：等待 ' + mskit.at(g.cur_player) + ' 出牌'

        if g.cur_player != g.last_player:
            s = s + '\n上一次出牌是 ' + mskit.at(g.last_player) + ' 出的：' + completed(str(g.last_step))
        
        s = s + '\n当前分数：' + str(g.score)
        
        await mskit.send_reply(message = s, event = event)


@on_command('记牌', aliases = {'jp'}, rule = mskit.is_group_message).handle()
async def jipai(event: mskit.GroupMessageEvent):
    group_id = event.group_id
    user_id = event.user_id

    # if not group_id:
    #     await session.send('请在群聊中使用斗地主功能')
    #     return
    
    if user_id == 80000000:
        await mskit.send_reply(message = '请解除匿名后再使用斗地主功能', event = event, at = False)
        return
    
    if not group_id in games:
        await mskit.send_reply(message = '本群还没有人使用斗地主功能', event = event)
        return
    
    g = games[group_id]

    if not g.state or g.state != 'started':
        s = '游戏未开始或未开始出牌'
    
    else:
        cs = ''
        for i in g.players:
            cs += g.tbl[i].hand
        
        dic = dict()
        for c in cs:
            if not c in dic:
                dic[c] = 0
            
            dic[c] += 1
        
        s = '当前还剩下的牌有：\n'

        for c in '34567891JQKA2鬼王':
            if c in dic:
                if s[-1] != '\n':
                    s += ' '

                s += completed(c) * dic[c]
    
    await mskit.send_reply(message = s, event = event)


@on_command('ob', aliases = {'观战'}).handle()
async def ob(event: mskit.MessageEvent):
    group_id = event.group_id if isinstance(event, mskit.GroupMessageEvent) else 695683445
    user_id = event.user_id
    
    if user_id == 80000000:
        await mskit.send_reply(message = '请解除匿名后再使用斗地主功能', event = event, at = False)
        return
    
    if not group_id in games or not games[group_id].state:
        await mskit.send_reply(message = '斗地主未开始', event = event)
        return
    
    g = games[group_id]
    if user_id in g.tbl:
        await mskit.send_reply(message = '你已在当前游戏中', event = event)

    s = ''
    if g.state == 'jdz' or g.state == 'qdz':
        s = '当前正在' + ('抢' if g.state == 'qdz' else '叫') + '地主\n'
    
    s = s + '各位玩家的手牌如下：'
    for i in g.tbl:
        name = get_name(group_id, i)

        async def get_group_card(group_id : int, user_id : int, subst : bool = False):
            info = await nonebot.get_bot().get_group_member_info(group_id = group_id, user_id = user_id)

            s = info['card']
            if s:
                return s
            elif subst:
                s = info['nickname']

            return s if s else str(user_id)
        
        card = get_group_card(group_id, i, True)

        t = name
        if card != name:
            t = t + '(%s)' % card
        
        if g.state == 'started':
            t = g.tbl[i].type + ' ' + t

        s = s + '\n' + t + '：' + g.tbl[i].get_hand() + '，共%d张' % len(g.tbl[i].hand)
    
    if g.state == 'jdz' or g.state == 'qdz':
        s = s + '\n' + '底牌是：' + completed(' '.join(g.deck))
    
    if isinstance(event, mskit.PrivateMessageEvent):
        await mskit.send_reply(message = s, event = event)
    else:
        try:
            await mskit.send_private_message(user_id = user_id, message = s)
        except:
            await mskit.send_reply(message = '请先加bot为好友', event = event)
        else:
            await mskit.send_reply(message = '信息已发送至私聊中，请查收', event = event)
