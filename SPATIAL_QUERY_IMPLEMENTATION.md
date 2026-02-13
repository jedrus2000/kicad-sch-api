# Spatial Query Tool Implementation - find_at_position

## Summary

Successfully implemented `find_at_position()` MCP tool for spatial queries in KiCAD schematics. This tool enables finding all schematic elements at or near a specific X,Y coordinate, bridging visual/spatial understanding with electrical connectivity.

## Feature Overview

### Purpose

In KiCAD schematics, **connections are position-based** - elements at the same X,Y coordinates are electrically connected. The `find_at_position()` tool provides a spatial query interface to discover:

- What elements exist at a specific coordinate
- What's connected at a junction point
- Which net a visual position corresponds to
- Wire routing endpoints and connectivity

This is complementary to `list_netlist()` (net-centric view) and helps LLMs understand schematics from spatial/visual context.

### Use Cases

1. **Visual debugging**: "What's at this position on the schematic?"
2. **Wire tracing**: "What does this wire connect to?"
3. **Junction analysis**: "What pins/wires meet at this junction?"
4. **Image-aware LLMs**: Convert visual coordinates from screenshots to electrical connectivity
5. **Interactive exploration**: Click on schematic locations to discover connectivity

## Implementation Details

### Function Signature

```python
async def find_at_position(
    x: float,
    y: float,
    tolerance: float = 0.5,
    ctx: Optional[Context] = None,
) -> dict:
```

**Parameters:**
- `x`: X coordinate in mm
- `y`: Y coordinate in mm
- `tolerance`: Search radius in mm (default: 0.5mm, suitable for user clicking)
- `ctx`: Optional MCP context for progress reporting

### Search Algorithm

The tool searches for elements within tolerance distance using Euclidean distance:

```python
distance = sqrt((element_x - x)² + (element_y - y)²)
if distance <= tolerance:
    # Element found
```

### Elements Searched

1. **Component Pins**
   - Finds pins at position (accounting for component rotation/mirroring)
   - Returns: component reference, pin number, pin name, electrical type, position
   - **Includes net name** via connectivity analysis

2. **Wire Endpoints**
   - Searches both start and end points of all wires
   - Returns: wire UUID, endpoint type (start/end), position, other end position, length, wire type

3. **Junctions**
   - Finds junction points (T-connections where 3+ wires meet)
   - Returns: junction UUID, position, diameter

4. **Labels**
   - Finds net labels at position
   - Returns: label UUID, text (net name), position, rotation, size

5. **Bus Entries**
   - Finds bus entry points (connections between wires and buses)
   - Returns: entry UUID, position, rotation, size

### Net Name Resolution

The tool performs **connectivity analysis** to provide net names for pins:

```python
from kicad_sch_api.core.connectivity import ConnectivityAnalyzer
analyzer = ConnectivityAnalyzer()
nets = analyzer.analyze(schematic, hierarchical=True)

# Maps pins to their nets
pin_to_net[f"{component_ref}.{pin_number}"] = net_name
```

This allows users to understand electrical connectivity from spatial queries.

## Return Format

```json
{
  "success": true,
  "query": {
    "x": 392.43,
    "y": 157.48,
    "tolerance": 2.0
  },
  "total_count": 2,
  "pins": [
    {
      "component": "#PWR021",
      "pin_number": "1",
      "pin_name": "~",
      "lib_id": "power:GND",
      "position": {"x": 392.43, "y": 157.48},
      "electrical_type": "power_input",
      "net": "GND"
    }
  ],
  "pin_count": 1,
  "wires": [
    {
      "uuid": "7ae505ef-...",
      "endpoint": "start",
      "position": {"x": 392.43, "y": 157.48},
      "other_end": {"x": 392.43, "y": 160.02},
      "length": 2.54,
      "wire_type": "wire"
    }
  ],
  "wire_endpoint_count": 1,
  "junctions": [],
  "junction_count": 0,
  "labels": [],
  "label_count": 0,
  "bus_entries": [],
  "bus_entry_count": 0,
  "message": "Found 2 element(s) at position (392.43, 157.48) with tolerance 2.0mm"
}
```

## Test Results

**Test File:** `test_find_at_position.py`

### Test 1: Power Symbol Position
- Query: (392.43, 157.48) with tolerance 2.0mm
- **Found**: 1 pin + 1 wire endpoint
- Pin: #PWR021.1 on net "GND" ✅
- Wire: Connected to pin ✅

### Test 2: Junction Point
- Query: (123.19, 109.22) with tolerance 0.5mm
- **Found**: 3 wire endpoints + 1 junction ✅
- Correctly identified T-connection point

### Test 3: Label Position
- Query: (392.43, 165.1) with tolerance 1.0mm
- **Found**: 1 label + 1 wire endpoint ✅
- Label: "PR2_INT" correctly found

### Test 4: Empty Location
- Query: (1000.0, 1000.0) with tolerance 0.5mm
- **Found**: 0 elements ✅
- Correctly identified no elements at distant location

## Files Modified

### 1. `/mcp_server/tools/connectivity_tools.py`
- **Added**: `find_at_position()` function (lines ~1143-1400)
- **Pattern**: Follows existing async MCP tool pattern
- **Features**: Progress reporting, error handling, connectivity analysis

### 2. `/mcp_server/tools/__init__.py`
- **Added**: Import `find_at_position` from connectivity_tools
- **Added**: Export in `__all__` list

### 3. `/mcp_server/server.py`
- **Added**: Import `find_at_position`
- **Added**: Register tool with `mcp.tool()(find_at_position)`

## Implementation Approach

### 1. Distance Calculation
Simple Euclidean distance for spatial queries:
```python
def is_within_tolerance(px: float, py: float) -> bool:
    import math
    distance = math.sqrt((px - x) ** 2 + (py - y) ** 2)
    return distance <= tolerance
```

### 2. Comprehensive Search
Iterate through all element types:
- Components → get pin positions via `get_pins_info()`
- Wires → check both start and end points
- Junctions → check position
- Labels → check position
- Bus entries → check position

### 3. Net Resolution
Optional connectivity analysis to enrich results:
```python
try:
    analyzer = ConnectivityAnalyzer()
    nets = analyzer.analyze(schematic, hierarchical=True)
    # Build pin -> net mapping
    for net in nets:
        for pin in net.pins:
            pin_to_net[f"{pin.reference}.{pin.pin_number}"] = net.name
except Exception:
    # Continue without net names if analysis fails
    pass
```

### 4. Structured Output
Group results by element type with counts for easy consumption.

## Performance Characteristics

- **Time Complexity**: O(n) where n = total elements in schematic
- **Typical Runtime**: <100ms for rocket_logger (96 components, 41 power symbols, many wires)
- **Scalability**: Efficient for typical schematics (<1000 components)

For large schematics, could be optimized with spatial indexing (e.g., quadtree), but not needed for current use cases.

## Design Decisions

### 1. Default Tolerance = 0.5mm ✅
- KiCAD default grid: 1.27mm (50 mil)
- 0.5mm catches elements within half a grid square
- Suitable for user clicking/selection
- Can be tightened to 0.1mm for exact matching

### 2. Include Net Names ✅
- Runs connectivity analysis to provide net names for pins
- Critical for understanding electrical connectivity
- Graceful fallback if analysis fails (net = None)

### 3. Check Both Wire Endpoints ✅
- Users may click on either end of a wire
- Returns both endpoints separately with distinct info
- Shows which end was found and where other end connects

### 4. Grouped Results ✅
- Separate arrays for each element type (pins, wires, junctions, labels, bus_entries)
- Includes individual counts (pin_count, wire_endpoint_count, etc.)
- Total count for quick overview
- Easier for LLMs to parse and understand

### 5. Comprehensive Element Coverage ✅
- Covers all connection-related elements
- Does NOT include: text boxes (non-electrical), sheets (hierarchical structure)
- Focus on electrical connectivity at spatial location

## Integration with MCP Server

The tool integrates seamlessly with the existing MCP server:

1. **Follows established patterns**: Same async structure, error handling, progress reporting as other tools
2. **Compatible with Claude Desktop**: Registered via FastMCP framework
3. **Complementary to existing tools**:
   - `list_netlist()`: Net-centric connectivity view
   - `find_at_position()`: Spatial/position-centric view
   - `get_component_pins()`: Component-centric pin info

## Benefits for LLMs

### 1. Visual Understanding
LLMs can now map visual/spatial information to electrical connectivity:
- User: "What's at coordinate (125, 88)?"
- LLM: Query → discover junction with 3 wires + 2 pins on net "VCC"

### 2. Interactive Exploration
Enables conversational schematic exploration:
- User: "Is there anything at position X,Y?"
- User: "What connects to this junction?"
- User: "What net is this wire on?"

### 3. Image Analysis Integration
Future capability: LLMs with vision could:
1. Analyze schematic screenshot
2. Identify visual position of element
3. Query `find_at_position()` to get electrical data
4. Bridge visual → electrical understanding

### 4. Debugging Support
Help users debug connectivity issues:
- "Why aren't these pins connected?" → Query positions to see if junction is missing
- "What's connected at this point?" → Discover all elements at junction

## Future Enhancements (Not Implemented)

### 1. Spatial Indexing
For very large schematics (>1000 components), could add:
- Quadtree or R-tree spatial index
- Pre-compute element bounding boxes
- Faster queries at cost of memory

### 2. Range Queries
Extend to search rectangular regions:
```python
find_in_rectangle(x1, y1, x2, y2) -> elements
```

### 3. Nearest Element
Find closest element even if outside tolerance:
```python
find_nearest(x, y, element_type="pin") -> closest_element
```

### 4. Connection Path Tracing
Follow wire connections from position:
```python
trace_from_position(x, y) -> connected_elements
```

## Conclusion

✅ **Implementation Complete**

The `find_at_position()` tool successfully provides spatial query capabilities for KiCAD schematics, enabling:

- Position-based element discovery
- Electrical connectivity from visual context
- Junction and connection point analysis
- Net name resolution from coordinates

**Status**: Fully functional, tested, and integrated into MCP server

**Testing**: All 4 test scenarios pass successfully with correct results

**Performance**: Efficient for typical schematics (<100ms query time)

**Integration**: Seamlessly works with existing MCP tools and connectivity analyzer

---

*Implementation completed: 2026-02-13*
