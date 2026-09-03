"""Process management and CPU scheduling module."""

from .models import Process
from .scheduler import schedule

__all__ = ["Process", "schedule"]
