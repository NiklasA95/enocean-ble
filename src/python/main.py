import re
import asyncio

from bleak import BleakScanner

def commission_device(commissioning_string):
    if not commissioning_string:
        raise ValueError('The commissioning string must be a non-empty string.')

    match = re.match(r'^30S([0-9a-fA-F]{12})\+Z([0-9a-fA-F]{32})\+30P([^\+]{10})\+2P([^\/+]{4,})\+', commissioning_string)
    
    if not match:
        raise ValueError("The commissioning string is invalid.")

    cdata = {
        'address': match.group(1).lower(),
        'security_key': match.group(2).lower(),
        'ordering_code': match.group(3),
        'step_code_revision': match.group(4)[:2] + '-' + match.group(4)[2:4],
        'serial': ''  # QR code only
    }

    first_match = re.search(r'\+S([0-9a-fA-F]+)', commissioning_string)
    if first_match:
        v = first_match.group(1)
        if len(v) >= 8:
            cdata['serial'] = v

    return cdata
        

async def main():
    stop_event = asyncio.Event()
    result = None

    try:
        commissioning_string = "30SE2150002E87A+Z86E7570162493D787396E2B4522C8040+30PS3221-A215+2PDD07+S01546701113804"
        result = commission_device(commissioning_string)
        print("Commissioning successful:")
        print(result)

    except ValueError as e:
        print(f"Error: {e}")

    def on_detection(device, advertising_data):
        if device.address == result.address:
            print()
            print(device)
            print("-" * len(str(device)))
            print(advertising_data)

        pass

    async with BleakScanner(on_detection):
        ...
        # Important! Wait for an event to trigger stop, otherwise scanner
        # will stop immediately.
        await stop_event.wait()

if __name__ == "__main__":
    asyncio.run(main())