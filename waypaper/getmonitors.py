from typing import List

from screeninfo import get_monitors

def get_monitor_names() -> List[str]:
    """Obtain the list of plugged monitors"""
    connected_monitors: List[str] = []
    for m in get_monitors():
        connected_monitors.append(m.name)
    return connected_monitors
