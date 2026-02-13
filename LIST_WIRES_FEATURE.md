# list_wires MCP Feature Implementation

## Summary

Added `list_wires` function to the MCP server to list all wires in the current schematic with their properties.

## Changes Made

### 1. Added `list_wires()` Function
**File**: `/mcp_server/tools/connectivity_tools.py`

New async function that:
- Lists all wires in the current schematic
- Returns wire endpoints, length, orientation, UUID, and type
- Follows same pattern as `list_components()`
- Includes progress reporting support

### 2. Exported Function
**File**: `/mcp_server/tools/__init__.py`

- Added `list_wires` to imports from `connectivity_tools`
- Added `list_wires` to `__all__` list

### 3. Registered MCP Tool
**File**: `/mcp_server/server.py`

- Imported `list_wires` from connectivity_tools
- Registered with `mcp.tool()(list_wires)`

## API Usage

### MCP Call
```python
result = await list_wires()
```

### Response Format
```python
{
    "success": True,
    "count": 363,
    "wires": [
        {
            "uuid": "04863d50-ea6c-4f0e-908d-18fa2dc2946a",
            "start": {"x": 209.55, "y": 137.16},
            "end": {"x": 234.95, "y": 137.16},
            "length": 25.40,
            "is_horizontal": True,
            "is_vertical": False,
            "wire_type": "wire",
            "stroke_width": 0.0
        },
        ...
    ]
}
```

### Error Response
```python
{
    "success": False,
    "error": "NO_SCHEMATIC_LOADED",
    "message": "No schematic is currently loaded"
}
```

## Wire Properties Returned

- **uuid**: Unique identifier for the wire
- **start**: Start point coordinates `{x, y}` in mm
- **end**: End point coordinates `{x, y}` in mm
- **length**: Wire length in mm (calculated)
- **is_horizontal**: Boolean indicating if wire is horizontal
- **is_vertical**: Boolean indicating if wire is vertical
- **wire_type**: Type of wire (usually "wire")
- **stroke_width**: Line width for rendering

## Test Results

Test schematic: `rocket_logger.kicad_sch`

```
✓ Successfully loaded schematic
✓ Found 363 wires
✓ All wire properties correctly extracted
✓ Boolean values for is_horizontal/is_vertical work correctly
```

### Sample Output
```
Wire 1:
  UUID: 04863d50...
  Start: (209.55, 137.16)
  End: (234.95, 137.16)
  Length: 25.40 mm
  Horizontal: True
  Vertical: False
  Type: wire
```

## Use Cases

1. **Wire Analysis**: Analyze wire routing in a schematic
2. **Connectivity Mapping**: Map all electrical connections
3. **Layout Review**: Check wire lengths and orientations
4. **Documentation**: Generate wire reports for schematics
5. **Debugging**: Inspect wire placement and connectivity

## Testing

Test file: `test_list_wires.py`

Run test:
```bash
uv run python test_list_wires.py
```

## Files Modified

1. `/mcp_server/tools/connectivity_tools.py` - Added `list_wires()` function
2. `/mcp_server/tools/__init__.py` - Exported `list_wires`
3. `/mcp_server/server.py` - Imported and registered tool
4. `/test_list_wires.py` - Test script (new)

## Implementation Details

### Method vs Property Handling

Fixed an issue where `is_horizontal` and `is_vertical` are methods in the Wire class:

```python
# Check if callable and call it
"is_horizontal": wire.is_horizontal() if callable(wire.is_horizontal) else wire.is_horizontal,
"is_vertical": wire.is_vertical() if callable(wire.is_vertical) else wire.is_vertical,
```

This ensures compatibility whether they're methods or properties.

## Future Enhancements

Possible improvements:
- Filter wires by type (wire, bus)
- Filter by bounding box region
- Group wires by connected net
- Export wire list to CSV/JSON
- Calculate total wire length statistics
