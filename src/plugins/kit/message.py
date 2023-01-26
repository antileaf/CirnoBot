from nonebot.adapters import Message, Event, MessageSegment

from typing import List, Tuple

async def is_group_message(event : Event):
    return event.get_type() == 'message' and \
        event.get_session_id().startswith('group')

# 'group', group_id, user_id
def evaluate_group_message(event : Event) -> Tuple[str, int, int]:
    if not is_group_message(event):
        return ('', -1, -1)

    a : List[str | int] = list(event.get_session_id().split("_"))
    return str(a[0]), int(a[1]), int(a[2])