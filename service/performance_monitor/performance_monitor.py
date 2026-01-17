# -*- coding: utf-8 -*-
"""Performance monitoring utility for tracking simulation ticks."""

import time
from collections import deque


class PerformanceMonitor:
    """Monitors simulation performance and prints tick count periodically."""
    
    def __init__(self, interval: float = 5.0):
        """
        Initialize the performance monitor.
        
        Args:
            interval: Time in seconds between tick reports (default: 5.0)
        """
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
            print(f"Tick: {tick_number}")
            self.last_print_time = current_time
            self.last60sec.append(tick_number)
            print(f"Ticks in last 60 sec: {self.last60sec[-1] - self.last60sec[0] if len(self.last60sec) > 1 else 0}")
