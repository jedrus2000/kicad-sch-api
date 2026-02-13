# manage_junctions 'list' Action Implementation

## Summary

Added `manage_junctions` MCP function with `list` action only to list all junctions in the current schematic with their properties.

## Changes Made

### 1. Added `manage_junctions()` Function
**File**: `/mcp_server/tools/consolidated_tools.py`

New async function (section 10, lines ~1530-1580):
- Lists all junctions in the current schematic
- Returns junction UUID, position, diameter, and color
- Accesses junctions from `schematic.junctions` collection
- Includes progress reporting support
- List-only tool (no add/remove functionality as requested)

### 2. Registered MCP Tool
**File**: `/mcp_server/server.py`

- Imported `manage_junctions` from consolidated_tools (line 36)
- Registered with `mcp.tool()(manage_junctions)` (line 343)
- Updated comment to reflect "10 consolidated CRUD tools"

## API Usage

### MCP Call
```python
result = await manage_junctions(action="list")
```

### Response Format
```python
{
    "success": True,
    "count": 61,
    "junctions": [
        {
            "uuid": "03506613-8a45-4c2d-9e1b-2d3f4a5b6c7d",
            "position": {"x": 123.19, "y": 109.22},
            "diameter": 0.0,
            "color": [0, 0, 0, 0]
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

## Junction Properties Returned

- **uuid**: Unique identifier for the junction
- **position**: Junction position `{x, y}` in mm
- **diameter**: Junction dot diameter in mm (default: 0.0, KiCAD uses default rendering size)
- **color**: RGBA color array `[r, g, b, a]` (default: `[0, 0, 0, 0]` - black/transparent)

## Test Results

Test schematic: `rocket_logger.kicad_sch`

```
✓ Successfully loaded schematic
✓ Found 61 junctions
✓ All junction properties correctly extracted
✓ UUID, position, diameter, color all working
```

### Sample Output
```
Junction 1:
  UUID: 03506613...
  Position: (123.19, 109.22)
  Diameter: 0.0
  Color: [0, 0, 0, 0]

Junction 2:
  UUID: 0b5e3bdc...
  Position: (182.88, 38.10)
  Diameter: 0.0
  Color: [0, 0, 0, 0]
```

## Use Cases

1. **Junction Analysis**: Analyze junction placement in a schematic
2. **Connectivity Mapping**: Map all wire connection points
3. **Design Review**: Check junction positions and verify proper connections
4. **Documentation**: Generate junction reports for schematics
5. **Debugging**: Inspect junction placement and connectivity points
6. **Cleanup Detection**: Find redundant or unnecessary junctions

## Testing

Test file: `test_list_junctions.py`

Run test:
```bash
uv run python test_list_junctions.py
```

## Files Modified

1. `/mcp_server/tools/consolidated_tools.py` - Added `manage_junctions()` function (section 10)
2. `/mcp_server/server.py` - Imported and registered tool
3. `/test_list_junctions.py` - Test script (new)

## Implementation Details

### Junction Collection Access

Junctions are accessed via the schematic's junction collection property:

```python
# Direct access to junction collection
junctions = list(schematic.junctions)

# Each junction is a Junction object with properties:
for junction in junctions:
    uuid = junction.uuid          # str
    position = junction.position  # Point (x, y)
    diameter = junction.diameter  # float
    color = junction.color       # Tuple[int, int, int, int]
```

### Color Format

Junction colors are RGBA tuples:
- Each component is an integer 0-255
- Format: `[red, green, blue, alpha]`
- Default: `[0, 0, 0, 0]` (black with zero alpha)
- Most junctions use default color

### Diameter Default

- KiCAD default diameter: 0.0 (uses internal default rendering size)
- Non-zero values explicitly set junction dot size
- Most junctions use 0.0 (default rendering)

### Error Handling

- Returns descriptive error messages
- Handles missing schematic gracefully
- Catches exceptions during junction iteration
- Safely handles missing or malformed junction data

## Design Decision: List-Only Tool

**Rationale for list-only implementation:**
- Junctions are typically created automatically by wire connections in KiCAD
- Manual junction addition is rare in typical workflows
- Users requested read-only access for analysis purposes
- Simpler API surface reduces complexity

**If add/remove needed later:**
- Can extend function to support "add" and "remove" actions
- Would use `schematic.junctions.add()` and similar methods
- API structure already supports future extensions

## Junction Purpose in KiCAD

Junctions serve critical functions in KiCAD schematics:

1. **Wire Connection Points**: Mark where 3+ wires meet
2. **T-Junction Indicators**: Show explicit wire connections at T-intersections
3. **Visual Clarity**: Distinguish between crossing and connecting wires
4. **ERC Validation**: Help electrical rule checking understand connectivity
5. **Netlist Generation**: Ensure proper net connectivity in output

**When KiCAD adds junctions automatically:**
- When 3 or more wires meet at a point
- At T-intersections where wires connect
- When explicitly added by user (right-click → Add Junction)

## Future Enhancements

Possible improvements if needed:
- Filter junctions by bounding box region
- Find junctions near specific coordinates
- Export junction list to CSV/JSON
- Calculate junction density statistics
- Add junction creation/removal actions (if requested)
- Highlight redundant junctions (2-wire junctions)
