# Lazy Loading Implementation for Component Pins

## Summary

Implemented automatic lazy loading for component pins to improve API usability while maintaining performance.

## Changes Made

### 1. Updated Component Class (`kicad_sch_api/collections/components.py`)

Modified the `pins` property to automatically load pins from the library on first access:

```python
@property
def pins(self) -> List[SchematicPin]:
    """List of component pins (lazy loaded from library on first access)."""
    if not self._data.pins:
        self.update_from_library()
    return self._data.pins
```

### 2. Updated Documentation (`RP2350_PARSING_FIX.md`)

- Documented the lazy loading behavior
- Updated usage examples to show automatic pin loading
- Clarified performance characteristics

## Benefits

✅ **Better UX**: Users no longer need to remember to call `update_from_library()`
✅ **Same Performance**: Pins are only loaded when accessed (lazy loading)
✅ **Backwards Compatible**: Existing code that calls `update_from_library()` still works
✅ **Intuitive API**: `component.pins` "just works"

## Usage

### Before (Manual Loading)
```python
sch = ksa.load_schematic('circuit.kicad_sch')
component = sch.components.filter(lib_id="Device:R")[0]
component.update_from_library()  # Required manual call
print(f"Pins: {len(component.pins)}")
```

### After (Automatic Lazy Loading)
```python
sch = ksa.load_schematic('circuit.kicad_sch')
component = sch.components.filter(lib_id="Device:R")[0]
print(f"Pins: {len(component.pins)}")  # Automatically loaded on first access
```

## Testing

Test file: `test.py`

**Results:**
- ✅ Lazy loading works correctly
- ✅ PCM library prefix handling works
- ✅ 81 pins loaded for RP2350B component
- ✅ Pin data accessible without manual calls

## Implementation Notes

- Lazy loading only happens once per component
- Library lookup is cached by the `SymbolLibraryCache`
- If library symbol is not found, pins remain empty (no error thrown)
- Manual calls to `update_from_library()` still work (can force reload)

## Files Modified

1. `/big/Customers/ja/kicad-sch-api/kicad_sch_api/collections/components.py` - Added lazy loading to `pins` property
2. `/big/Customers/ja/kicad-sch-api/RP2350_PARSING_FIX.md` - Updated documentation
3. `/big/Customers/ja/kicad-sch-api/test.py` - Updated test to demonstrate lazy loading

## Related Issues

- RP2350 parsing issue - resolved with PCM library prefix handling
- Poor UX for pin loading - resolved with lazy loading implementation
