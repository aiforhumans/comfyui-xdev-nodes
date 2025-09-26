# Node Anatomy

A minimal node defines:
- `INPUT_TYPES` (classmethod) → declares required/optional/hidden inputs
- `RETURN_TYPES` (tuple of datatypes) → output sockets in order
- `FUNCTION` (str) → method name executed
- `CATEGORY` (str) → where it appears in the menu

See `xdev_nodes/nodes/*.py` for examples.
