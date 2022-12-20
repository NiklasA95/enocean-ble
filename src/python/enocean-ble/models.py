"""Library to handle connection with EnOcean BLE."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from bleak.backends.device import BLEDevice


@dataclass
class EnOceanBleAdvertisement:
    """EnOcean BLE advertisement."""

    address: str
    data: dict[str, Any]
    device: BLEDevice
    rssi: int
    active: bool = False