"""Library to handle connection with EnOcean BLE devices."""
from __future__ import annotations

from enum import Enum

DEFAULT_RETRY_COUNT = 3
DEFAULT_RETRY_TIMEOUT = 1
DEFAULT_SCAN_TIMEOUT = 5

from .enum import StrEnum


class EnOceanBleModel(StrEnum):
    WALL_SWITCH = "WallSwitch"