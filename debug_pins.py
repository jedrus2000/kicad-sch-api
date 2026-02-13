#!/usr/bin/env python3
"""Debug script to test RP2350 pin parsing."""

import logging
import sys
import sexpdata

# Enable debug logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(levelname)s - %(name)s - %(message)s",
    stream=sys.stdout
)

logger = logging.getLogger(__name__)

# Read and parse the library file
with open("rp2350_in_library.txt", "r") as f:
    library_content = f.read()

print("=" * 80)
print("Parsing RP2350B symbol from library file")
print("=" * 80)

parsed = sexpdata.loads(library_content, true=None, false=None, nil=None)

# Analyze the structure
print(f"\nTop level type: {type(parsed)}")
print(f"Top level first element: {parsed[0] if parsed else None}")
print(f"Top level second element (name): {parsed[1] if len(parsed) > 1 else None}")

# Find symbol units
pin_count = 0
unit_definitions = []

for item in parsed:
    if isinstance(item, list) and len(item) >= 2:
        if item[0] == sexpdata.Symbol("symbol"):
            unit_name = str(item[1]).strip('"')
            unit_definitions.append((unit_name, item))
            print(f"\nFound unit: {unit_name}")

            # Count pins in this unit
            unit_pins = 0
            for sub_item in item:
                if isinstance(sub_item, list) and len(sub_item) > 0:
                    if sub_item[0] == sexpdata.Symbol("pin"):
                        pin_count += 1
                        unit_pins += 1

                        # Debug first 3 pins
                        if pin_count <= 3:
                            print(f"\n  Pin {pin_count} raw structure:")
                            print(f"    Length: {len(sub_item)}")
                            for i, elem in enumerate(sub_item[:7]):  # Show first 7 elements
                                print(f"    [{i}]: {elem}")

            print(f"  Unit has {unit_pins} pins")

print(f"\n{'=' * 80}")
print(f"Total pins found: {pin_count}")
print(f"Total units found: {len(unit_definitions)}")

# Now test the actual library cache parser
print(f"\n{'=' * 80}")
print("Testing kicad_sch_api library cache parser")
print("=" * 80)

import os
os.environ.setdefault("KICAD_SYMBOL_DIR", "/big/Customers/ja/micro/kicad_projects/libraries:/home/andrzej/.local/share/kicad/9.0/3rdparty/symbols")

import kicad_sch_api as ksa

cache = ksa.library.cache.SymbolLibraryCache(enable_persistence=False)
cache.discover_libraries()

# Try to get the RP2350B symbol
symbol = cache.get_symbol("PCM_SparkFun-IC-Microcontroller:RP2350B")

if symbol:
    print(f"\n✓ Symbol found: {symbol.lib_id}")
    print(f"  Reference prefix: {symbol.reference_prefix}")
    print(f"  Description: {symbol.description}")
    print(f"  Units: {symbol.units}")
    print(f"  Pin count: {len(symbol.pins)}")

    if len(symbol.pins) == 0:
        print(f"\n✗ ERROR: No pins loaded!")
    else:
        print(f"\n✓ Pins loaded successfully")
        # Show first 3 pins
        for i, pin in enumerate(symbol.pins[:3]):
            print(f"\n  Pin {i+1}:")
            print(f"    Number: {pin.number}")
            print(f"    Name: {pin.name}")
            print(f"    Type: {pin.pin_type}")
            print(f"    Position: {pin.position}")
else:
    print(f"\n✗ Symbol not found in library!")
