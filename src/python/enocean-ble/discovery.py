"""Discover EnOcean BLE devices."""

from __future__ import annotations

import asyncio
import logging

import bleak
from bleak.backends.device import BLEDevice
from bleak.backends.scanner import AdvertisementData

from .adv_parser import parse_advertisement_data
from .const import DEFAULT_RETRY_COUNT, DEFAULT_RETRY_TIMEOUT, DEFAULT_SCAN_TIMEOUT
from .models import EnOceanBleAdvertisement

_LOGGER = logging.getLogger(__name__)
CONNECT_LOCK = asyncio.Lock()


class GetEnOceanBleDevices:
    """Scan for all EnOcean BLE devices and return by type."""

    def __init__(self, interface: int = 0) -> None:
        """Get EnOcean BLE devices devices class constructor."""
        self._interface = f"hci{interface}"
        self._adv_data: dict[str, EnOceanBleAdvertisement] = {}

    def detection_callback(
        self,
        device: BLEDevice,
        advertisement_data: AdvertisementData,
    ) -> None:
        """Callback for device detection."""
        discovery = parse_advertisement_data(device, advertisement_data)
        if discovery:
            self._adv_data[discovery.address] = discovery

    async def discover(
        self, retry: int = DEFAULT_RETRY_COUNT, scan_timeout: int = DEFAULT_SCAN_TIMEOUT
    ) -> dict:
        """Find EnOcean BLE devices and their advertisement data."""

        devices = None
        devices = bleak.BleakScanner(
            adapter=self._interface,
        )
        devices.register_detection_callback(self.detection_callback)

        async with CONNECT_LOCK:
            await devices.start()
            await asyncio.sleep(scan_timeout)
            await devices.stop()

        if devices is None:
            if retry < 1:
                _LOGGER.error(
                    "Scanning for EnOcean BLE devices failed. Stop trying", exc_info=True
                )
                return self._adv_data

            _LOGGER.warning(
                "Error scanning for EnOcean BLE devices. Retrying (remaining: %d)",
                retry,
            )
            await asyncio.sleep(DEFAULT_RETRY_TIMEOUT)
            return await self.discover(retry - 1, scan_timeout)

        return self._adv_data

    async def _get_devices_by_model(
        self,
        model: str,
    ) -> dict:
        """Get EnOcean BLE devices by type."""
        if not self._adv_data:
            await self.discover()

        return {
            address: adv
            for address, adv in self._adv_data.items()
            if adv.data.get("model") == model
        }

    async def get_wall_switches(self) -> dict[str, EnOceanBleAdvertisement]:
        """Return all EnOcean BLE wall switch devices with services data."""
        return await self._get_devices_by_model("c")

    async def get_device_data(
        self, address: str
    ) -> dict[str, EnOceanBleAdvertisement] | None:
        """Return data for specific device."""
        if not self._adv_data:
            await self.discover()

        return {
            device: adv
            for device, adv in self._adv_data.items()
            # MacOS uses UUIDs instead of MAC addresses
            if adv.data.get("address") == address
        }