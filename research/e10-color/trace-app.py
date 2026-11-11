#!/usr/bin/env python3
"""Index color-related symbols in a locally supplied Blutter ASM directory.

Offline only: no device/account input, no command dispatch, no app code copied.
Addresses are evidence locations, not proof that any frame is safe to transmit.
"""
import argparse
import hashlib
import json
import re
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('asm_root', type=Path)
args = parser.parse_args()
base = args.asm_root / 'flutter_charging_business_package/ble/device/t8l00'
files = {
    'controller': base / 't8l00_device_controller.dart',
    'color_command': base / 'cmd/lighting/light_transport_new_cmd.dart',
    'color_conversion': base / 'cmd/lighting/light_rgb_calculate_color.dart',
    'mqtt_envelope': base / 'cmd/base/abstract_cmd.dart',
}
result = {'schema': 1, 'device_commands_sent': False, 'files': {}}
for kind, path in files.items():
    text = path.read_text()
    symbols = []
    method = None
    for number, line in enumerate(text.splitlines(), 1):
        if line.startswith('  ') and not line.startswith('    ') and '{' in line and '(' in line:
            method = line.strip().split('(')[0].strip()
        addr = re.search(r'// \*\* addr: (0x[0-9a-f]+)', line)
        if addr and method:
            symbols.append({'method': method, 'address': addr[1], 'line': number})
        model = re.search(r'// (0x[0-9a-f]+): r\d+ = "(T8L20|T8L30)"', line)
        if model:
            symbols.append({'model': model[2], 'method': method, 'address': model[1], 'line': number})
    result['files'][kind] = {'path': str(path.relative_to(args.asm_root)),
                             'sha256': hashlib.sha256(text.encode()).hexdigest(),
                             'symbols': symbols}
print(json.dumps(result, indent=2))
