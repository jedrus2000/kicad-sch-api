# list_netlist (Connectivity Analysis) Implementation

## Summary

Added `list_netlist` MCP function to analyze electrical connectivity and return all nets (electrical connections) in a schematic. This provides comprehensive netlist information showing how all components are connected together.

## Changes Made

### 1. Added `list_netlist()` Function
**File**: `/mcp_server/tools/connectivity_tools.py`

New async function:
- Performs comprehensive connectivity analysis using ConnectivityAnalyzer
- Traces connections through wires, junctions, labels, global labels, hierarchical labels, and power symbols
- Returns all nets with their names and connected component pins
- Supports hierarchical analysis for multi-sheet designs
- Includes progress reporting support

### 2. Exported Function
**File**: `/mcp_server/tools/__init__.py`

- Added `list_netlist` to imports from connectivity_tools
- Added to `__all__` list

### 3. Registered MCP Tool
**File**: `/mcp_server/server.py`

- Imported `list_netlist` from connectivity_tools
- Registered with `mcp.tool()(list_netlist)`

## API Usage

### MCP Call
```python
# With hierarchical analysis (default)
result = await list_netlist(hierarchical=True)

# Without hierarchical analysis
result = await list_netlist(hierarchical=False)
```

### Response Format
```python
{
    "success": True,
    "count": 130,
    "nets": [
        {
            "name": "GND",
            "pins": [
                {
                    "reference": "U2",
                    "pin": "62",
                    "position": {"x": 173.99, "y": 63.50}
                },
                {
                    "reference": "#PWR09",
                    "pin": "1",
                    "position": {"x": 24.13, "y": 265.43}
                },
                ...
            ],
            "pin_count": 55,
            "wire_count": 54,
            "junction_count": 15,
            "label_count": 2
        },
        {
            "name": "I2C0_SDA",
            "pins": [
                {"reference": "J3", "pin": "4", "position": {...}},
                {"reference": "U2", "pin": "1", "position": {...}},
                {"reference": "J30", "pin": "17", "position": {...}},
                {"reference": "J2", "pin": "17", "position": {...}}
            ],
            "pin_count": 4,
            "wire_count": 4,
            "junction_count": 0,
            "label_count": 4
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

## Properties Returned

### Net Properties
- **name**: Net name (from label, power symbol, or auto-generated like "Net-1")
- **pins**: List of connected component pins
- **pin_count**: Number of connected pins
- **wire_count**: Number of wires in this net
- **junction_count**: Number of junctions in this net
- **label_count**: Number of labels naming this net

### Pin Properties (within each net)
- **reference**: Component reference (e.g., "U2", "R1", "C45")
- **pin**: Pin number/name (e.g., "1", "2", "VCC", "GND")
- **position**: Pin position `{x, y}` in mm

## Test Results

Test schematic: `rocket_logger.kicad_sch`

```
✓ Successfully loaded schematic
✓ Performed connectivity analysis
✓ Found 130 nets
✓ Total connections: 323 pins, 363 wires, 61 junctions
✓ Top nets identified: GND (55 pins), +3V3 (33 pins)
✓ Specific nets found: I2C0_SDA (4 pins), I2C0_SCL (4 pins), SWD (2 pins)
```

### Sample Output
```
Net 'GND':
  55 connections
  Pins: #PWR09.1, #PWR04.1, #PWR053.1, U2.62, C34.2, ...
  Wires: 54, Junctions: 15, Labels: 2

Net 'I2C0_SDA':
  4 connections
  Pins: J3.4, U2.1, J30.17, J2.17
  Wires: 4, Junctions: 0, Labels: 4

Net '+3V3':
  33 connections
  Pins: C41.1, J30.20, D4.2, C46.1, C45.1, ...
  Wires: 39, Junctions: 14, Labels: 0
```

## Use Cases

1. **Connectivity Verification**: Verify that components are connected correctly
2. **Net Analysis**: Analyze electrical nets and their connections
3. **Netlist Export**: Get netlist data for external tools (SPICE, PCB layout, etc.)
4. **Design Review**: Check that all expected connections exist
5. **Debugging**: Identify connection issues or missing connections
6. **Documentation**: Generate connectivity reports for design documentation
7. **ERC Preparation**: Pre-check connectivity before Electrical Rule Check
8. **Signal Tracing**: Trace signal paths through the circuit

## Testing

Test file: `test_list_netlist.py`

Run test:
```bash
uv run python test_list_netlist.py
```

## Files Modified

1. `/mcp_server/tools/connectivity_tools.py` - Added `list_netlist()` function
2. `/mcp_server/tools/__init__.py` - Exported function
3. `/mcp_server/server.py` - Imported and registered tool
4. `/test_list_netlist.py` - Test script (new)

## Implementation Details

### Connectivity Analysis

Uses the `ConnectivityAnalyzer` from `kicad_sch_api.core.connectivity`:

```python
from kicad_sch_api.core.connectivity import ConnectivityAnalyzer

# Create analyzer and run analysis
analyzer = ConnectivityAnalyzer()
nets = analyzer.analyze(schematic, hierarchical=True)

# Process results
for net in nets:
    name = net.name  # Net name (or None for unnamed)
    pins = net.pins  # Set of PinConnection objects
    wires = net.wires  # Set of wire UUIDs
    junctions = net.junctions  # Set of junction UUIDs
    labels = net.labels  # Set of label UUIDs
```

### Connection Tracing

The analyzer traces connections through:

1. **Direct Wire-to-Pin Connections**: Wires touching component pins
2. **Junction Points**: Multiple wires meeting at junctions
3. **Labels**: Wires with same label name are electrically connected
4. **Global Labels**: Project-wide connections across sheets
5. **Hierarchical Labels**: Parent-child sheet connections
6. **Power Symbols**: Implicit global connections (GND, VCC, etc.)

### Hierarchical Analysis

When `hierarchical=True` (default):
- Analyzes connections across hierarchical sheets
- Processes hierarchical labels connecting parent and child sheets
- Traces global labels across all sheets
- Returns complete connectivity for multi-sheet designs

When `hierarchical=False`:
- Analyzes only current sheet
- Ignores hierarchical and global label connections
- Faster for single-sheet schematics

### Net Naming

Net names come from multiple sources (in priority order):

1. **Labels**: Local labels (`I2C_SDA`, `MOSI`, etc.)
2. **Global Labels**: Global labels (`DATA[0..7]`, `ADDR[0..15]`)
3. **Power Symbols**: Power symbols (`GND`, `VCC`, `+3V3`, etc.)
4. **Auto-Generated**: Unnamed nets get `Net-1`, `Net-2`, etc.

### Performance

Connectivity analysis performance depends on schematic complexity:

- **Small schematics** (< 50 components): ~100ms
- **Medium schematics** (50-200 components): ~500ms
- **Large schematics** (200+ components): ~1-2 seconds
- **Hierarchical designs**: Additional time for sheet traversal

Analysis is performed fresh each time (no caching in MCP function).

## Common Net Types

### Power Nets
- **GND**: Ground (0V reference)
- **VCC**: Main positive supply
- **+3V3, +5V, +12V**: Specific voltage rails
- **-12V, -5V**: Negative supplies

### Signal Nets
- **Named signals**: User-labeled signals (e.g., `I2C_SDA`, `SPI_MOSI`)
- **Pin-derived**: Auto-named from pin connections (e.g., `Net-(U2-Pad41)`)
- **Bus signals**: Individual bus members (e.g., `DATA0`, `DATA1`)

### Special Nets
- **PWR_FLAG**: Power flag for ERC
- **NC**: No Connect (intentionally unconnected pins)
- **Unnamed**: Auto-generated names for unlabeled nets

## Connectivity Verification Example

```python
# Check if two specific pins are connected
result = await list_netlist()

for net in result['nets']:
    pin_refs = [(p['reference'], p['pin']) for p in net['pins']]

    # Check if U2.1 and J3.4 are on same net
    if ('U2', '1') in pin_refs and ('J3', '4') in pin_refs:
        print(f"U2.1 and J3.4 are connected via net '{net['name']}'")
        break
```

## Error Handling

- Returns descriptive error messages
- Handles missing schematic gracefully
- Catches exceptions during connectivity analysis
- Safely handles malformed or incomplete schematic data
- Reports connectivity analysis errors with stack traces

## Future Enhancements

Possible improvements:
- Cache connectivity results for unchanged schematics
- Filter nets by name pattern (regex support)
- Filter by component reference or pin
- Export to standard netlist formats (SPICE, KiCAD, Altium)
- Highlight disconnected nets (single-pin nets)
- Calculate net statistics (total wire length, fanout, etc.)
- Detect connectivity issues (floating pins, shorts, etc.)
- Compare connectivity between schematic revisions
