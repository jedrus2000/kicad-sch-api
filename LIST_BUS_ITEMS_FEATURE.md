# list_bus_wires and list_bus_entries Implementation

## Summary

Added `list_bus_wires` and `list_bus_entries` MCP functions to list bus-related elements in schematics. These complement the existing `add_bus_wire` and `add_bus_entry` functions.

## Changes Made

### 1. Added `list_bus_wires()` Function
**File**: `/mcp_server/tools/connectivity_tools.py`

New async function:
- Lists all bus wires (filtered from all wires where wire_type == BUS)
- Returns bus wire endpoints, length, orientation, UUID, and stroke width
- Bus wires are thicker lines representing groups of related signals
- Includes progress reporting support

### 2. Added `list_bus_entries()` Function
**File**: `/mcp_server/tools/connectivity_tools.py`

New async function:
- Lists all bus entries in the current schematic
- Returns bus entry position, size, rotation, UUID, and stroke properties
- Bus entries connect individual wires to bus wires
- Includes progress reporting support

### 3. Exported Functions
**File**: `/mcp_server/tools/__init__.py`

- Added `list_bus_wires` to imports from connectivity_tools
- Added `list_bus_entries` to imports from connectivity_tools
- Added both to `__all__` list

### 4. Registered MCP Tools
**File**: `/mcp_server/server.py`

- Imported `list_bus_wires` and `list_bus_entries` from connectivity_tools
- Registered with `mcp.tool()(list_bus_wires)` and `mcp.tool()(list_bus_entries)`
- Organized in bus tools section alongside add functions

## API Usage

### List Bus Wires

#### MCP Call
```python
result = await list_bus_wires()
```

#### Response Format
```python
{
    "success": True,
    "count": 2,
    "bus_wires": [
        {
            "uuid": "d8005aa6-8a45-4c2d-9e1b-2d3f4a5b6c7d",
            "start": {"x": 100.00, "y": 100.00},
            "end": {"x": 200.00, "y": 100.00},
            "length": 100.00,
            "is_horizontal": True,
            "is_vertical": False,
            "stroke_width": 0.0
        },
        ...
    ]
}
```

### List Bus Entries

#### MCP Call
```python
result = await list_bus_entries()
```

#### Response Format
```python
{
    "success": True,
    "count": 2,
    "bus_entries": [
        {
            "uuid": "8e1cded0-5a3e-4c2d-8f11-9b7e3d2c1a0b",
            "position": {"x": 150.00, "y": 100.00},
            "size": {"x": 2.54, "y": 2.54},
            "rotation": 0,
            "stroke_width": 0.0,
            "stroke_type": "default"
        },
        ...
    ]
}
```

### Error Response (Both Functions)
```python
{
    "success": False,
    "error": "NO_SCHEMATIC_LOADED",
    "message": "No schematic is currently loaded"
}
```

## Properties Returned

### Bus Wire Properties
- **uuid**: Unique identifier for the bus wire
- **start**: Start point coordinates `{x, y}` in mm
- **end**: End point coordinates `{x, y}` in mm
- **length**: Bus wire length in mm (calculated)
- **is_horizontal**: Boolean indicating if bus wire is horizontal
- **is_vertical**: Boolean indicating if bus wire is vertical
- **stroke_width**: Line width for rendering (default 0.0 uses KiCAD default thick line)

### Bus Entry Properties
- **uuid**: Unique identifier for the bus entry
- **position**: Entry position `{x, y}` in mm
- **size**: Entry size `{x, y}` in mm (default 2.54 x 2.54mm = 100 mil)
- **rotation**: Entry rotation in degrees (0, 90, 180, or 270)
- **stroke_width**: Line width for rendering (default 0.0)
- **stroke_type**: Stroke style (default "default")

## Test Results

### Basic Test (rocket_logger.kicad_sch)
```
✓ Successfully loaded schematic
✓ list_bus_wires() found 0 bus wires (expected - not all schematics use buses)
✓ list_bus_entries() found 0 bus entries (expected)
```

### Comprehensive Test (created schematic)
```
✓ Created blank schematic
✓ Added 2 bus wires (1 horizontal, 1 vertical)
✓ Added 2 bus entries (0° and 270° rotation)
✓ list_bus_wires() correctly retrieved 2 bus wires
✓ list_bus_entries() correctly retrieved 2 bus entries
✓ All properties correctly extracted
```

### Sample Output
```
Bus Wire 1:
  UUID: d8005aa6...
  Start: (100.00, 100.00)
  End: (200.00, 100.00)
  Length: 100.00 mm
  Horizontal: True
  Vertical: False

Bus Entry 1:
  UUID: 8e1cded0...
  Position: (150.00, 100.00)
  Size: (2.54, 2.54)
  Rotation: 0°
  Stroke Width: 0.0
```

## Use Cases

### Bus Wires
1. **Bus Analysis**: Analyze data bus routing in a schematic
2. **Multi-Signal Tracking**: Track groups of related signals (address bus, data bus, etc.)
3. **Design Review**: Check bus wire placement and connections
4. **Documentation**: Generate bus routing reports
5. **Connectivity Mapping**: Map high-level signal groups

### Bus Entries
1. **Signal Branching**: Analyze where individual signals branch from buses
2. **Bus Interface Points**: Map all connection points between wires and buses
3. **Design Verification**: Verify bus entry placement and rotation
4. **Documentation**: Document bus interface connections
5. **Debugging**: Inspect bus entry configurations

## Testing

Test files:
- `test_list_bus_items.py` - Basic test with rocket_logger schematic (0 bus items)
- `test_bus_items_full.py` - Comprehensive test with add and list operations

Run tests:
```bash
uv run python test_list_bus_items.py
uv run python test_bus_items_full.py
```

## Files Modified

1. `/mcp_server/tools/connectivity_tools.py` - Added `list_bus_wires()` and `list_bus_entries()` functions
2. `/mcp_server/tools/__init__.py` - Exported new functions
3. `/mcp_server/server.py` - Imported and registered tools
4. `/test_list_bus_items.py` - Basic test script (new)
5. `/test_bus_items_full.py` - Comprehensive test script (new)

## Implementation Details

### Bus Wire Filtering

Bus wires are filtered from the main wire collection:

```python
from kicad_sch_api.core.types import WireType

# Get all wires
all_wires = list(schematic.wires)

# Filter for bus wires only
bus_wires = [w for w in all_wires if w.wire_type == WireType.BUS]
```

**Key insight:** Bus wires are stored in the same collection as regular wires, distinguished by their `wire_type` property.

### Bus Entry Collection Access

Bus entries have their own dedicated collection:

```python
# Direct access to bus entry collection
bus_entries = list(schematic.bus_entries)

# Each bus entry is a BusEntry object
for entry in bus_entries:
    uuid = entry.uuid           # str
    position = entry.position   # Point (x, y)
    size = entry.size          # Point (x, y) - default 2.54, 2.54
    rotation = entry.rotation   # int (0, 90, 180, 270)
    stroke_width = entry.stroke_width  # float
    stroke_type = entry.stroke_type    # str
```

### Bus Concepts in KiCAD

**Bus Wires:**
- Represent groups of related signals (e.g., D[0..7] for 8-bit data bus)
- Displayed as thick lines in schematic
- Named with bracket notation: `DATA[0..7]`, `ADDR[0..15]`
- Cannot directly connect to component pins (need bus entries)

**Bus Entries:**
- Connect individual wires to/from bus wires
- Show which specific signal from the bus is being used
- Diagonal line connecting wire to bus
- Rotation determines entry direction (0°, 90°, 180°, 270°)
- Default size is 2.54mm (100 mil)

**Example Bus Usage:**
```
    DATA[0]  ──┐
    DATA[1]  ──┤
    DATA[2]  ──┤  DATA[0..7]  ═══════════
    DATA[3]  ──┤
    ...
```

### Error Handling

- Returns descriptive error messages
- Handles missing schematic gracefully
- Catches exceptions during iteration
- Safely handles missing or malformed data
- Validates wire type during filtering

## Bus Design Patterns

### Common Bus Applications

1. **Microprocessor Data Buses**: 8-bit, 16-bit, or 32-bit data buses
2. **Address Buses**: Memory and I/O addressing
3. **GPIO Groups**: Related GPIO pins grouped together
4. **Communication Interfaces**: SPI, I2C bus representation
5. **Memory Interfaces**: DDR, SDRAM bus connections

### When to Use Buses

**Use buses when:**
- You have 4+ related signals
- Signals follow a naming pattern (e.g., D0-D7)
- Schematic becomes cluttered with parallel wires
- Want to show high-level signal grouping

**Don't use buses when:**
- Only 2-3 related signals (just draw wires)
- Signals aren't truly related
- Adding complexity without benefit

## Future Enhancements

Possible improvements:
- Filter bus wires by bounding box region
- Parse bus names and extract bit ranges (e.g., "DATA[0..7]")
- Find bus entries connected to specific bus wires
- Export bus topology to CSV/JSON
- Calculate bus wire statistics (total length, entry count)
- Validate bus entry connections
