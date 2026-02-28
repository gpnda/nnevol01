# -*- coding: utf-8 -*-
"""Performance monitoring utility for tracking simulation ticks."""

import time
import sys
from collections import deque
from service.logger.logger import logme
from service.debugger.debugger import debug

def get_full_size(obj, seen=None, exclude_attr_names=None):
    """Рекурсивно считает размер объекта вместе с содержимым."""
    if seen is None:
        seen = set()
    if exclude_attr_names is None:
        exclude_attr_names = set()

    obj_id = id(obj)
    if obj_id in seen:
        return 0
    seen.add(obj_id)

    size = sys.getsizeof(obj)

    if isinstance(obj, dict):
        for k, v in obj.items():
            size += get_full_size(k, seen, exclude_attr_names)
            size += get_full_size(v, seen, exclude_attr_names)

    elif hasattr(obj, '__dict__'):
        for attr_name, attr_value in obj.__dict__.items():
            if attr_name in exclude_attr_names:
                continue
            size += get_full_size(attr_value, seen, exclude_attr_names)

    # NEW: поддержка объектов со __slots__
    elif hasattr(obj, '__slots__'):
        slots = obj.__slots__
        if isinstance(slots, str):
            slots = (slots,)
        for slot_name in slots:
            if slot_name in exclude_attr_names:
                continue
            if hasattr(obj, slot_name):
                size += get_full_size(getattr(obj, slot_name), seen, exclude_attr_names)

    elif hasattr(obj, '__iter__') and not isinstance(obj, (str, bytes, bytearray)):
        try:
            for item in obj:
                size += get_full_size(item, seen, exclude_attr_names)
        except TypeError:
            pass

    return size

class PerformanceMonitor:
    """Monitors simulation performance and prints tick count periodically."""
    
    def __init__(self, app, interval: float = 5.0):
        """
        Initialize the performance monitor.
        
        Args:
            interval: Time in seconds between tick reports (default: 5.0)
        """
        self.app = app
        self.interval = interval
        self.last_print_time = time.time()
        self.last60sec = deque(maxlen=12) # хранит время тиков за последние 60 секунд. 20 записей с интервалом в 5 секунд.
    
    def tick(self, tick_number: int) -> None:
        """
        Record a simulation tick and print tick number every 5 seconds.
        
        Args:
            tick_number: The current simulation tick number
        """
        current_time = time.time()
        elapsed = current_time - self.last_print_time
        
        if elapsed >= self.interval:
            self.last_print_time = current_time
            self.last60sec.append(tick_number)
            print(f"Tick: {tick_number}. ticks in last 60 sec: {self.last60sec[-1] - self.last60sec[0] if len(self.last60sec) > 1 else 0}")
            print("Memory usage:")
            print(f"       Application: {get_full_size(self.app):,} bytes")
            print(f"            Renderer: {get_full_size(self.app.renderer, exclude_attr_names={'app', 'world'}):,} bytes")
            print(f"                 RenderState: {get_full_size(self.app.renderer.last_render_state):,} bytes")
            print(f"            Experiment: {get_full_size(self.app.experiment):,} bytes")
            print(f"            World: {get_full_size(self.app.world):,} bytes")
            print(f"                 World.creatures: {get_full_size(self.app.world.creatures):,} bytes")
            print(f"                 Creatures count: {len(self.app.world.creatures)}")
            print(f"                 Per creature: {int(get_full_size(self.app.world.creatures)/len(self.app.world.creatures)):,} bytes")
            print(f"       logme: {get_full_size(logme):,} bytes")
            print(f"       debug: {get_full_size(debug):,} bytes")
            print(f"debug._debug_data: {get_full_size(debug._debug_data):,} bytes")

