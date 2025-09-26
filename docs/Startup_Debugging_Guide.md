# XDev Nodes Startup Debugging Guide

The ComfyUI XDev Nodes package includes comprehensive startup debugging to help with troubleshooting, development, and monitoring during ComfyUI initialization.

## 🚀 Quick Start

When you start ComfyUI with XDev Nodes installed, you'll see detailed, color-coded startup information like this:

```
[XDev-INIT]  • ============================================================
[XDev-INFO]  ℹ️ 🎯 ComfyUI XDev Nodes - Complete Development Toolkit
[XDev-INFO]  ℹ️ 📦 Version: 0.2.0 | 8 Professional Nodes
[XDev-INFO]  ℹ️ 🌐 Repository: github.com/aiforhumans/comfyui-xdev-nodes
[XDev-INIT]  • ============================================================
[XDev-LOAD]  • Starting node imports...
[XDev-INFO]  ℹ️ ✅ Basic nodes loaded: HelloString, AnyPassthrough
[XDev-REG]   • Building node mappings...
[XDev-VAL]   • ✅ All nodes passed validation
[XDev-INFO]  ℹ️ 📦 Total Nodes Registered: 8
[XDev-INFO]  ℹ️ 🚀 XDev Nodes ready for ComfyUI!
```

**Color Legend:**
- 🟣 **INIT** (Magenta) - Initialization and banners
- 🔵 **INFO** (Blue) - General information and status
- 🟦 **LOAD** (Cyan) - Loading operations
- 🟡 **REG** (Yellow) - Node registration
- 🟢 **VAL** (Green) - Validation results  
- 🔴 **ERROR** (Red) - Errors and failures
- ⚫ **DEBUG** (Gray) - Debug information

## ⚙️ Configuration

### Debug Configuration File

Edit `xdev_nodes/debug_config.py` to customize the debugging output:

```python
# Basic settings
DEBUG_ENABLED = True          # Master switch
DEBUG_LEVEL = "INFO"          # ERROR, WARN, INFO, DEBUG, TRACE

# Component debugging
DEBUG_IMPORTS = True          # Show node import status
DEBUG_WEB = True              # Show web asset scanning
DEBUG_VALIDATION = True       # Show node validation
DEBUG_SUMMARY = True          # Show startup summary

# Visual formatting
DEBUG_USE_COLORS = True       # ANSI color coding for better readability
DEBUG_USE_BANNER = True       # Show startup banner
DEBUG_USE_EMOJIS = True       # Use emoji indicators (✅❌⚠️)

# Performance monitoring
DEBUG_TIMING = False          # Show timing information
DEBUG_TRACEBACK = False       # Show full error tracebacks
```

### Debug Levels Explained

| Level | Description | Use Case |
|-------|-------------|----------|
| `ERROR` | Only critical errors | Production environments |
| `WARN` | Errors + warnings | Stable deployments |
| `INFO` | Normal startup info | Standard development |
| `DEBUG` | Detailed diagnostics | Active development |
| `TRACE` | Maximum verbosity | Troubleshooting issues |

## 🌈 Color Support

The debugging system uses ANSI color codes to make output more readable and visually organized:

### Color Categories
Each message type has its own color for quick visual scanning:

| Category | Color | Purpose | Example |
|----------|-------|---------|---------|
| **INIT** | 🟣 Magenta | Banners & initialization | `[XDev-INIT] • ============` |
| **INFO** | 🔵 Blue | General information | `[XDev-INFO] ℹ️ ✅ Nodes loaded` |
| **LOAD** | 🟦 Cyan | Loading operations | `[XDev-LOAD] • Starting imports...` |
| **REG** | 🟡 Yellow | Registration process | `[XDev-REG] • Building mappings...` |
| **VAL** | 🟢 Green | Validation results | `[XDev-VAL] • ✅ Validation passed` |
| **DEBUG** | ⚫ Gray | Debug information | `[XDev-DEBUG] 🔍 Detailed info` |
| **WARN** | 🟡 Yellow | Warnings | `[XDev-WARN] ⚠️ Missing asset` |
| **ERROR** | 🔴 Red | Errors & failures | `[XDev-ERROR] ❌ Import failed` |

### Terminal Compatibility
- ✅ **Windows Terminal** - Full color support
- ✅ **PowerShell** - Full color support  
- ✅ **VS Code Terminal** - Full color support
- ✅ **Most modern terminals** - Full color support
- ⚠️ **Legacy terminals** - May show escape codes instead of colors

To disable colors: Set `DEBUG_USE_COLORS = False` in `debug_config.py`

## 🔍 Output Components

### 1. Startup Banner
Shows version, repository info, and system details:
```
[XDev-INFO]  🎯 ComfyUI XDev Nodes - Complete Development Toolkit
[XDev-INFO]  📦 Version: 0.2.0 | 8 Professional Nodes
[XDev-DEBUG] 🐍 Python: 3.11.0 | Platform: win32
```

### 2. Import Tracking
Monitors node loading with success/failure reporting:
```
[XDev-INFO]  ✅ Development nodes loaded: OutputDev, InputDev
[XDev-ERROR] ❌ Failed during VAE tools import: ImportError
```

### 3. Web Asset Scanning  
Checks for JavaScript extensions and documentation:
```
[XDev-INFO]  ✅ Web directory found: /path/to/web
[XDev-DEBUG] 📄 JavaScript: xdev.js (2.3 KB)
[XDev-INFO]  📚 Documentation: 8 files found
```

### 4. Node Registration
Shows successful node mappings and validation:
```
[XDev-INFO]  📝 Successfully registered 8 nodes: HelloString, AnyPassthrough...
[XDev-VAL]   ✅ Node mapping consistency validated
[XDev-VAL]   ✅ All nodes passed validation
```

### 5. Startup Summary
Comprehensive overview of the initialization process:
```
[XDev-INFO]  📊 Import Statistics:
[XDev-INFO]     ✅ Successful: 5/5
[XDev-INFO]     ❌ Failed: 0/5
[XDev-INFO]  📦 Total Nodes Registered: 8
[XDev-INFO]  🚀 XDev Nodes ready for ComfyUI!
```

## 🛠️ Troubleshooting

### Common Issues

**No debug output appearing:**
- Check `DEBUG_ENABLED = True` in `debug_config.py`
- Verify ComfyUI is loading the package correctly

**Too much/little output:**
- Adjust `DEBUG_LEVEL` (ERROR < WARN < INFO < DEBUG < TRACE)
- Toggle specific components with `DEBUG_IMPORTS`, `DEBUG_WEB`, etc.

**Import failures:**
- Look for ❌ symbols in the output
- Set `DEBUG_TRACEBACK = True` for detailed error information
- Check node dependencies and Python environment

**Missing nodes in ComfyUI:**
- Verify nodes show ✅ status during import
- Check the "Total Nodes Registered" count matches expected (8)
- Look for validation failures in the debug output

### Debug for Specific Scenarios

**Development Setup:**
```python
DEBUG_LEVEL = "DEBUG"
DEBUG_TIMING = True
DEBUG_VALIDATION = True
```

**Production Environment:**
```python
DEBUG_LEVEL = "ERROR"
DEBUG_SUMMARY = False
DEBUG_USE_BANNER = False
```

**Troubleshooting Problems:**
```python
DEBUG_LEVEL = "TRACE"
DEBUG_TRACEBACK = True
DEBUG_NODE_DETAILS = True
```

## 📊 Performance Monitoring

When `DEBUG_TIMING = True`, you'll see timing information:
```
[0.023s] [XDev-INFO] ✅ Basic nodes loaded (0.008s)
[0.045s] [XDev-INFO] ✅ VAE tools loaded (0.015s)
```

This helps identify slow-loading components during startup.

## 🎯 Integration with ComfyUI

The debugging system is designed to:
- **Not interfere** with ComfyUI's normal operation  
- **Provide immediate feedback** during startup
- **Help diagnose issues** with custom node loading
- **Monitor performance** of the initialization process
- **Validate proper registration** of all nodes

## 💡 Tips & Best Practices

1. **Keep INFO level** for normal development work
2. **Use DEBUG level** when adding new nodes or features  
3. **Enable TRACE level** only when troubleshooting specific issues
4. **Disable debugging** in production for cleaner console output
5. **Check web assets** if you're developing frontend extensions
6. **Monitor import statistics** to catch partial loading issues

## 🔗 Related Files

- `xdev_nodes/__init__.py` - Main debugging implementation
- `xdev_nodes/debug_config.py` - Configuration settings
- `test_debug_levels.py` - Debug level demonstration script

The debugging system helps ensure all 8 XDev nodes (HelloString, AnyPassthrough, PickByBrightness, AppendSuffix, OutputDev, InputDev, VAERoundTrip, VAEPreview) load correctly and are ready for use in ComfyUI workflows.