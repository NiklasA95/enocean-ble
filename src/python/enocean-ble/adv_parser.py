"""Library to handle connection with Switchbot."""
from __future__ import annotations

import logging
from collections.abc import Callable
from functools import lru_cache
from typing import Any, TypedDict

from bleak.backends.device import BLEDevice
from bleak.backends.scanner import AdvertisementData

from .adv_parsers.wall_switch import process_wall_switch
from .const import EnOceanBleModel
from .models import EnOceanBleAdvertisement

_LOGGER = logging.getLogger(__name__)

SERVICE_DATA_ORDER = (
    "0000fd3d-0000-1000-8000-00805f9b34fb",
    "00000d00-0000-1000-8000-00805f9b34fb",
)
MFR_DATA_ORDER = (2409, 89)


class EnOceanBleSupportedType(TypedDict):
    """Supported type of EnOcean BLE."""

    modelName: EnOceanBleModel
    modelFriendlyName: str
    func: Callable[[bytes, bytes | None], dict[str, bool | int]]
    manufacturer_id: int | None
    manufacturer_data_length: int | None


SUPPORTED_TYPES: dict[str, EnOceanBleSupportedType] = {
    "d": {
        "modelName": EnOceanBleModel.WALL_SWITCH,
        "modelFriendlyName": "Wall Switch",
        "func": process_wall_switch,
        "manufacturer_id": 2409,
        "manufacturer_data_length": 13,
    }
}

_ENOCEAN_BLE_MODEL_TO_CHAR = {
    model_data["modelName"]: model_chr
    for model_chr, model_data in SUPPORTED_TYPES.items()
}

MODELS_BY_MANUFACTURER_DATA: dict[int, list[tuple[str, EnOceanBleSupportedType]]] = {
    mfr_id: [] for mfr_id in MFR_DATA_ORDER
}
for model_chr, model in SUPPORTED_TYPES.items():
    if "manufacturer_id" in model:
        mfr_id = model["manufacturer_id"]
        MODELS_BY_MANUFACTURER_DATA[mfr_id].append((model_chr, model))


def parse_advertisement_data(
    device: BLEDevice,
    advertisement_data: AdvertisementData,
    model: EnOceanBleModel | None = None,
) -> EnOceanBleAdvertisement | None:
    """Parse advertisement data."""
    service_data = advertisement_data.service_data

    _service_data = None
    for uuid in SERVICE_DATA_ORDER:
        if uuid in service_data:
            _service_data = service_data[uuid]
            break

    _mfr_data = None
    _mfr_id = None
    for mfr_id in MFR_DATA_ORDER:
        if mfr_id in advertisement_data.manufacturer_data:
            _mfr_id = mfr_id
            _mfr_data = advertisement_data.manufacturer_data[mfr_id]
            break

    if _mfr_data is None and _service_data is None:
        return None

    try:
        data = _parse_data(
            _service_data,
            _mfr_data,
            _mfr_id,
            model,
        )
    except Exception as err:  # pylint: disable=broad-except
        _LOGGER.exception(
            "Failed to parse advertisement data: %s: %s", advertisement_data, err
        )
        return None

    if not data:
        return None

    return EnOceanBleAdvertisement(
        device.address, data, device, advertisement_data.rssi, bool(_service_data)
    )


@lru_cache(maxsize=128)
def _parse_data(
    _service_data: bytes | None,
    _mfr_data: bytes | None,
    _mfr_id: int | None = None,
    _enocean_ble_model: EnOceanBleModel | None = None,
) -> dict[str, Any] | None:
    """Parse advertisement data."""
    _model = chr(_service_data[0] & 0b01111111) if _service_data else None

    if _enocean_ble_model and _enocean_ble_model in _ENOCEAN_BLE_MODEL_TO_CHAR:
        _model = _ENOCEAN_BLE_MODEL_TO_CHAR[_enocean_ble_model]

    if not _model and _mfr_id and _mfr_id in MODELS_BY_MANUFACTURER_DATA:
        for model_chr, model_data in MODELS_BY_MANUFACTURER_DATA[_mfr_id]:
            if model_data.get("manufacturer_data_length") == len(_mfr_data):
                _model = model_chr
                break

    if not _model:
        return None

    _isEncrypted = bool(_service_data[0] & 0b10000000) if _service_data else False
    data = {
        "rawAdvData": _service_data,
        "data": {},
        "model": _model,
        "isEncrypted": _isEncrypted,
    }

    type_data = SUPPORTED_TYPES.get(_model)
    if type_data:
        model_data = type_data["func"](_service_data, _mfr_data)
        if model_data:
            data.update(
                {
                    "modelFriendlyName": type_data["modelFriendlyName"],
                    "modelName": type_data["modelName"],
                    "data": model_data,
                }
            )

    return data