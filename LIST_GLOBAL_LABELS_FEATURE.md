# manage_global_labels 'list' Action Implementation

## Summary

Added `list` action to the `manage_global_labels` MCP function to list all global labels in the current schematic with their properties.

## Changes Made

### 1. Added `list` Action to `manage_global_labels()`
**File**: `/mcp_server/tools/consolidated_tools.py`

New action handling (lines 1388-1423):
- Lists all global labels in the current schematic
- Returns label text, UUID, position, rotation, shape, and size
- Accesses global labels from `schematic._data["global_label"]`
- Includes progress reporting support

### 2. Updated Function Documentation
**File**: `/mcp_server/tools/consolidated_tools.py`

- Updated docstring to include "list" in valid actions
- Updated error message to show "add, remove, list" as valid actions

### 3. Fixed Rotation Parameter Issue
**File**: `/mcp_server/tools/consolidated_tools.py`

- Removed unsupported `rotation` parameter from `add_global_label()` call
- API doesn't support rotation parameter in add method (always defaults to 0)

## API Usage

### MCP Call
```python
result = await manage_global_labels(action="list")
```

### Response Format
```python
{
    "success": True,
    "count": 4,
    "global_labels": [
        {
            "uuid": "6f8b73f3-8a45-4c2d-9e1b-2d3f4a5b6c7d",
            "text": "UART_TX",
            "position": {"x": 100.00, "y": 100.00},
            "rotation": 0,
            "shape": "output",
            "size": [1.27, 1.27]
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

## Global Label Properties Returned

- **uuid**: Unique identifier for the global label
- **text**: Label text content (signal name)
- **position**: Label position `{x, y}` in mm
- **rotation**: Label rotation in degrees (currently always 0)
- **shape**: Label shape type ("input", "output", "bidirectional", "tri_state", "passive")
- **size**: Font size `[width, height]` in mm

## Test Results

Test schematic: Created new schematic with 4 global labels

```
✓ Successfully created blank schematic
✓ Added 4 global labels (UART_TX, UART_RX, I2C_SDA, I2C_SCL)
✓ Listed all global labels
✓ All global label properties correctly extracted
✓ UUID, text, position, rotation, shape, size all working
```

### Sample Output
```
Global Label 1:
  UUID: 6f8b73f3...
  Text: UART_TX
  Position: (100.00, 100.00)
  Rotation: 0°
  Shape: output
  Size: [1.27, 1.27]

Global Label 2:
  UUID: 54218858...
  Text: UART_RX
  Position: (100.00, 110.00)
  Rotation: 0°
  Shape: input
  Size: [1.27, 1.27]
```

## Use Cases

1. **Global Signal Analysis**: Analyze project-wide signal connections
2. **Hierarchical Design Review**: Check global labels connecting sheet boundaries
3. **Net Extraction**: Extract all global net names from project
4. **Documentation**: Generate global signal reports for multi-sheet designs
5. **Connectivity Verification**: Verify global connections across hierarchical sheets

## Testing

Test files:
- `test_list_global_labels.py` - Basic list test with rocket_logger schematic (0 global labels)
- `test_global_labels_full.py` - Comprehensive test with add and list actions

Run tests:
```bash
uv run python test_list_global_labels.py
uv run python test_global_labels_full.py
```

## Files Modified

1. `/mcp_server/tools/consolidated_tools.py` - Added "list" action to `manage_global_labels()`
2. `/test_list_global_labels.py` - Basic test script (new)
3. `/test_global_labels_full.py` - Comprehensive test script (new)

## Implementation Details

### Data Structure Access

Global labels are stored in the raw schematic data structure:

```python
# Global labels are in _data["global_label"] (singular, not plural)
global_labels_data = schematic._data.get("global_label", [])

# Each label is a dictionary with structure:
{
    "uuid": "string",
    "text": "signal_name",
    "shape": "input/output/bidirectional/tri_state/passive",
    "at": [x, y, rotation],
    "effects": {"font": {"size": [1.27, 1.27]}}
}
```

### Shape Types

Valid global label shapes:
- **input**: Incoming signal
- **output**: Outgoing signal
- **bidirectional**: Bidirectional signal (e.g., I2C, SPI)
- **tri_state**: Tri-state signal
- **passive**: Passive connection

### Error Handling

- Returns descriptive error messages
- Handles missing schematic gracefully
- Catches exceptions during label iteration
- Safely handles missing size attribute or malformed data

## Known Limitations

1. **Rotation Not Supported on Add**: The `add_global_label()` API doesn't support rotation parameter (always defaults to 0)
2. **No Collection Property**: Unlike regular labels (`schematic.labels`), there's no direct `schematic.global_labels` property - must access via `_data`

## Differences from Regular Labels

| Feature | Regular Labels | Global Labels |
|---------|---------------|---------------|
| Scope | Local to sheet | Project-wide |
| Collection Property | `schematic.labels` | `schematic._data["global_label"]` |
| Shape Support | No | Yes (input/output/etc.) |
| Hierarchical Use | Within sheet only | Cross-sheet connections |
| Storage Key | `"labels"` | `"global_label"` (singular) |

## Future Enhancements

Possible improvements:
- Add rotation support to `add_global_label()` API
- Create `schematic.global_labels` property for consistency
- Filter by shape type (input/output/bidirectional)
- Filter by bounding box region
- Search for specific label text patterns
- Export to CSV/JSON with hierarchical context
