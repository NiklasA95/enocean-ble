import re
import asyncio

from bleak import BleakClient

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
    try:
        commissioning_string = "30S123456789abc+Zabcdef1234567890abcdef1234567890+30Pabcdefghij+2Pabcd+S12345678"
        result = commission_device(commissioning_string)
        print("Commissioning successful:")
        print(result)

        async with BleakClient("97411DBA-427C-E532-765F-B0A216B30E1D") as client:
            print(await client.get_services())


    except ValueError as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())