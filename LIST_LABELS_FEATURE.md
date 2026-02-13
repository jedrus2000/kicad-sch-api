# manage_labels 'list' Action Implementation

## Summary

Added `list` action to the `manage_labels` MCP function to list all labels in the current schematic with their properties.

## Changes Made

### 1. Added `list` Action to `manage_labels()`
**File**: `/mcp_server/tools/consolidated_tools.py`

New action handling (lines 636-669):
- Lists all labels in the current schematic
- Returns label text, UUID, position, rotation, and size
- Follows same pattern as other list operations
- Includes progress reporting support

### 2. Updated Function Documentation
**File**: `/mcp_server/tools/consolidated_tools.py`

- Updated docstring to include "list" in valid actions
- Updated error message to show "add, remove, list" as valid actions

## API Usage

### MCP Call
```python
result = await manage_labels(action="list")
```

### Response Format
```python
{
    "success": True,
    "count": 153,
    "labels": [
        {
            "uuid": "00198920-5a3e-4c2d-8f11-9b7e3d2c1a0b",
            "text": "PR2_INT",
            "position": {"x": 392.43, "y": 165.10},
            "rotation": 180.0,
            "size": 1.27
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

## Label Properties Returned

- **uuid**: Unique identifier for the label
- **text**: Label text content
- **position**: Label position `{x, y}` in mm
- **rotation**: Label rotation in degrees (0, 90, 180, 270)
- **size**: Font size in mm (may be None)

## Test Results

Test schematic: `rocket_logger.kicad_sch`

```
✓ Successfully loaded schematic
✓ Found 153 labels
✓ All label properties correctly extracted
✓ UUID, text, position, rotation, size all working
```

### Sample Output
```
Label 1:
  UUID: 00198920...
  Text: PR2_INT
  Position: (392.43, 165.10)
  Rotation: 180.0°
  Size: 1.27

Label 2:
  UUID: 00b0e232...
  Text: VREG_LX
  Position: (143.51, 86.36)
  Rotation: 0.0°
  Size: 1.27
```

## Use Cases

1. **Label Analysis**: Analyze label placement and naming in a schematic
2. **Net Name Extraction**: Extract all net names from labels
3. **Documentation**: Generate label reports for schematics
4. **Connectivity Mapping**: Map labels to wire connections
5. **Design Review**: Check label consistency and positioning

## Testing

Test file: `test_list_labels.py`

Run test:
```bash
uv run python test_list_labels.py
```

## Files Modified

1. `/mcp_server/tools/consolidated_tools.py` - Added "list" action to `manage_labels()`
2. `/test_list_labels.py` - Test script (new)

## Implementation Details

### Integration with Existing manage_labels Function

The "list" action integrates seamlessly with existing "add" and "remove" actions:

```python
elif action == "list":
    try:
        labels = list(schematic.labels)
        label_list = []
        for label in labels:
            label_data = {
                "uuid": str(label.uuid),
                "text": label.text,
                "position": {"x": label.position.x, "y": label.position.y},
                "rotation": label.rotation,
                "size": label.size if hasattr(label, 'size') else None,
            }
            label_list.append(label_data)
        return {"success": True, "count": len(labels), "labels": label_list}
    except Exception as e:
        return {
            "success": False,
            "error": "LIST_LABELS_ERROR",
            "message": f"Failed to list labels: {str(e)}",
        }
```

### Error Handling

- Returns descriptive error messages
- Handles missing schematic gracefully
- Catches exceptions during label iteration
- Safely handles missing size attribute

## Future Enhancements

Possible improvements:
- Filter labels by text pattern (regex support)
- Filter by bounding box region
- Group labels by connected net
- Export label list to CSV/JSON
- Search for specific label text
- Sort by position or text
