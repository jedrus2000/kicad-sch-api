import kicad_sch_api as ksa
import logging
import os
import sys

from kicad_sch_api.core.types import PinType

os.environ.setdefault("KICAD_SYMBOL_DIR", "/usr/share/kicad/symbols:/big/Customers/ja/micro/kicad_projects/libraries:/home/andrzej/.local/share/kicad/9.0/3rdparty/symbols")

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stdout
)

sch = ksa.load_schematic('/big/Customers/ja/micro/kicad_projects/rocket_logger/rocket_logger.kicad_sch')

#u = sch.components.filter(lib_id="PCM_SparkFun-IC-Microcontroller:RP2350B")
#print(f"Found {len(u)} RP2350B component(s)")

# Pins are automatically loaded on first access (lazy loading)
#print(f"\nTotal pins (auto-loaded): {len(u[0].pins)}")
#print("\nFirst 10 pins:")
#for pin in u[0].pins[:10]:
#    print(f"  Pin {pin.number:>3}: {pin.name}")

#pins = sch.components.get_pins_info("U2")
#for pin in pins:
#    if pin.electrical_type == PinType.POWER_IN:
#        print(pin)
pins = sch.components.find_pins_by_type("U2", "power_in")
print(pins)


