# RP2350 Parsing Issue - Resolution Summary

## Problem

The RP2350B component from SparkFun library was not having its pins parsed correctly when loading schematics. The component would load, but `component.pins` would be empty.

## Root Causes

### Issue 1: KiCAD Package Manager (PCM) Library Name Prefix

**Problem:** Schematics created with libraries installed via KiCAD Package Manager reference them with a `PCM_` prefix (e.g., `PCM_SparkFun-IC-Microcontroller:RP2350B`), but the actual library files don't have this prefix (e.g., `SparkFun-IC-Microcontroller.kicad_sym`).

**Solution:** Added fallback logic in `kicad_sch_api/library/cache.py` method `_load_symbol()` to try removing the `PCM_` prefix when a library is not found by exact name match.

```python
# Try to find the library, handling PCM-prefixed names
library_path = None
if library_name in self._library_index:
    library_path = self._library_index[library_name]
elif library_name.startswith("PCM_"):
    # Try without the PCM_ prefix (KiCAD Package Manager convention)
    alt_library_name = library_name[4:]  # Remove "PCM_" prefix
    if alt_library_name in self._library_index:
        logger.debug(f"🔧 LOAD: Found library without PCM prefix: {alt_library_name}")
        library_path = self._library_index[alt_library_name]
        # Update lib_id to use the non-prefixed library name
        lib_id = f"{alt_library_name}:{symbol_name}"
```

### Issue 2: Automatic Pin Loading with Lazy Loading

**Solution:** Component pins are now automatically loaded from the library cache when first accessed. This uses lazy loading - pins are only loaded when you access the `.pins` property, providing both good performance and a simple API.

**How it works:** When you access `component.pins` for the first time, the library automatically calls `update_from_library()` behind the scenes to load pin data from the symbol definition.

## How to Use

### Loading a Schematic and Accessing RP2350 Pins

```python
import kicad_sch_api as ksa

# 1. Set up environment to include SparkFun library paths
import os
os.environ["KICAD_SYMBOL_DIR"] = (
    "/usr/share/kicad/symbols:"
    "/home/user/.local/share/kicad/9.0/3rdparty/symbols"
)

# 2. Load schematic
sch = ksa.load_schematic('rocket_logger.kicad_sch')

# 3. Find RP2350 component
rp2350 = sch.components.filter(lib_id="PCM_SparkFun-IC-Microcontroller:RP2350B")[0]

# 4. Access pins - they're automatically loaded on first access (lazy loading)
print(f"Total pins: {len(rp2350.pins)}")

for pin in rp2350.pins:
    print(f"Pin {pin.number}: {pin.name} ({pin.pin_type})")

# 6. Get absolute pin positions (accounting for component rotation)
pin_pos = rp2350.get_pin_position('1')
print(f"Pin 1 absolute position: ({pin_pos.x}, {pin_pos.y})")
```

## Verification

The fix was verified with:
- **Component:** RP2350B (80-pin QFN package)
- **Library:** SparkFun-IC-Microcontroller.kicad_sym (installed via PCM)
- **Schematic:** rocket_logger.kicad_sch
- **Result:** All 81 pins (80 pins + EP pad) loaded successfully ✓

### Test Results

```
✓ Component found: U2
✓ Lib ID: PCM_SparkFun-IC-Microcontroller:RP2350B
✓ Pins loaded: 81
✓ Pin positions calculated correctly
✓ Pin types parsed correctly (power_in, bidirectional, etc.)
```

## Files Modified

- `kicad_sch_api/library/cache.py` - Added PCM_ prefix fallback logic in `_load_symbol()` method

## Testing

Run the comprehensive test:

```bash
python test_rp2350_final.py
```

Expected output: "✓ SUCCESS: RP2350 component parsing working correctly!"

## Notes

1. **Environment Setup:** Ensure `KICAD_SYMBOL_DIR` includes the path to SparkFun libraries (typically in `~/.local/share/kicad/9.0/3rdparty/symbols`)

2. **Performance:** Pins are loaded using lazy loading - they're only fetched from the library when you first access the `.pins` property. This avoids unnecessary library lookups while providing a simple API.

3. **Compatibility:** This fix works with all PCM-installed libraries, not just SparkFun.

4. **Pin Positions:** The library stores pins in symbol space (with normal Y-axis). The `get_pin_position()` method correctly transforms them to schematic space (inverted Y-axis) accounting for component rotation.

## Related Documentation

- KiCAD 9 File Format: https://dev-docs.kicad.org/en/file-formats/index.html
- Library Configuration: `docs/LIBRARY_CONFIGURATION.md`
- Coordinate System: See `CLAUDE.md` section "KiCAD Coordinate System"
