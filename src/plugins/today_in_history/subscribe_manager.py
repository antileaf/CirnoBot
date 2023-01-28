from typing import List, Tuple, Set, Union

from ... import kit

class TIHSubscribe:
    def __init__(self, name : str):
        self.name = name
        self.db = kit.db.subscribe.Subscribe(name)
    
    def add(self, id : int):
        self.db.add((id, ''))
    
    def remove(self, id : int):
        self.db.remove((id, ''))
    
    def __contains__(self, id : int) -> bool:
        return {'id': id} in self.db
    
    def all(self) -> List[int]:
        return [id for id, _, _ in self.db.query({'content' : self.db.ANY_CONTENT})]

group = TIHSubscribe('today_in_history_group')
user = TIHSubscribe('today_in_history_user')

def subscribe(group_id : int = 0, user_id : int = 0) -> Tuple[bool, str]:
    if group_id and user_id:
        raise ValueError('Check what you are doing')
    
    id = group_id | user_id
    db = group if group_id else user

    if id in db:
        return False, '{}已经订阅过了'.format('本群' if group_id else '你')
    
    db.add(id)
    return True, '已成功{}订阅，将会在每天零点播报历史上的当天信息'.format('在本群' if group_id else '为你')

def unsubscribe(group_id : int = 0, user_id : int = 0) -> Tuple[bool, str]:
    if group_id and user_id:
        raise ValueError('Check what you are doing')
    
    id = group_id | user_id
    db = group if group_id else user

    if id not in db:
        return False, '{}还没有订阅过哦…'.format('本群' if group_id else '你')
    
    db.remove(id)
    return True, '已成功{}取消订阅'.format('在本群' if group_id else '为你')

def has_subscribed(group_id : int = 0, user_id : int = 0) -> bool:
    if group_id and user_id:
        raise ValueError('Check what you are doing')
    
    id = group_id | user_id
    db = group if group_id else user

    return id in db

async def check_permission(group_id : int, user_id : int) -> bool:
    import nonebot

    return str(user_id) in nonebot.get_bot().config.superusers or await kit.nb.group.is_group_admin_or_owner(group_id = group_id, user_id = user_id)