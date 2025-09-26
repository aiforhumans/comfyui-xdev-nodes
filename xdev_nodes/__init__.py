import sys
import traceback
import time
from pathlib import Path

# ═══════════════════════════════════════════════════════════════════════════════
# 🚀 ComfyUI XDev Nodes - Enhanced Startup Debug Logger
# ═══════════════════════════════════════════════════════════════════════════════

# Import debug configuration
try:
    from .debug_config import *
except ImportError:
    # Fallback defaults if config file missing
    DEBUG_ENABLED = True
    DEBUG_LEVEL = "INFO"
    DEBUG_IMPORTS = True
    DEBUG_WEB = True
    DEBUG_VALIDATION = True
    DEBUG_SUMMARY = True
    DEBUG_USE_BANNER = True
    DEBUG_USE_EMOJIS = True
    DEBUG_TIMING = False
    DEBUG_TRACEBACK = False

# Startup timing
_startup_time = time.time()

def debug_print(message, level="INFO", force=False):
    """Enhanced debug printing with configuration support and color coding"""
    if not DEBUG_ENABLED and not force:
        return
    
    # Level filtering
    level_priority = {"ERROR": 0, "WARN": 1, "INFO": 2, "DEBUG": 3, "TRACE": 4}
    if level_priority.get(level, 2) > level_priority.get(DEBUG_LEVEL, 2):
        return
    
    # ANSI color codes for different categories
    colors = {
        "INIT": "\033[95m",    # Magenta for initialization
        "INFO": "\033[94m",    # Blue for info
        "LOAD": "\033[96m",    # Cyan for loading
        "REG": "\033[93m",     # Yellow for registration
        "VAL": "\033[92m",     # Green for validation
        "ERROR": "\033[91m",   # Red for errors
        "WARN": "\033[93m",    # Yellow for warnings
        "DEBUG": "\033[90m",   # Gray for debug
        "TRACE": "\033[37m",   # White for trace
        "RESET": "\033[0m"     # Reset
    }
    
    # Timing information
    timing = ""
    if DEBUG_TIMING:
        elapsed = time.time() - _startup_time
        timing = f"[{elapsed:.3f}s] "
    
    # Emoji and formatting
    emoji_map = {"ERROR": "❌", "WARN": "⚠️", "INFO": "ℹ️", "DEBUG": "🔍", "TRACE": "📋"}
    emoji = emoji_map.get(level, "•") if DEBUG_USE_EMOJIS else ""
    
    # Apply color coding if enabled
    prefix = f"[XDev-{level}]"
    if hasattr(globals(), 'DEBUG_USE_COLORS') and DEBUG_USE_COLORS:
        # Use level-based coloring for the entire line
        color = colors.get(level, colors["INFO"])
        reset = colors["RESET"]
        
        # Format with consistent spacing (no extra spacing for color codes)
        formatted_message = f"{timing}{prefix:<12} {emoji} {message}" if emoji else f"{timing}{prefix:<12} {message}"
        colored_line = f"{color}{formatted_message}{reset}"
        print(colored_line)
    else:
        print(f"{timing}{prefix:<12} {emoji} {message}")

def debug_exception(operation, exception):
    """Enhanced exception logging"""
    debug_print(f"❌ Failed during {operation}: {exception}", "ERROR", force=True)
    if DEBUG_TRACEBACK:
        debug_print(f"Traceback: {traceback.format_exc()}", "ERROR", force=True)

def startup_banner():
    """Display startup banner with version info"""
    if not DEBUG_USE_BANNER:
        return
    
    debug_print("=" * 60, "INIT", force=True)
    debug_print("🎯 ComfyUI XDev Nodes - Complete Development Toolkit", "INFO", force=True)
    debug_print("📦 Version: 0.2.0 | 8 Professional Nodes", "INFO", force=True) 
    debug_print("🌐 Repository: github.com/aiforhumans/comfyui-xdev-nodes", "INFO", force=True)
    debug_print(f"🐍 Python: {sys.version.split()[0]} | Platform: {sys.platform}", "DEBUG")
    debug_print("=" * 60, "INIT", force=True)

# Display startup banner
startup_banner()

# ═══════════════════════════════════════════════════════════════════════════════
# 📦 Node Imports with Debug Logging
# ═══════════════════════════════════════════════════════════════════════════════

debug_print("Starting node imports...", "LOAD")

# Import tracking
_import_stats = {"success": 0, "failed": 0, "total": 0}

# Initialize node variables with None (fallback protection)
HelloString = None
AnyPassthrough = None
PickByBrightness = None
AppendSuffix = None
OutputDev = None
InputDev = None
VAERoundTrip = None
VAEPreview = None

# Basic Nodes
try:
    debug_print("🔄 Importing Basic nodes...", "DEBUG")
    from .nodes.basic import HelloString, AnyPassthrough
    debug_print("✅ Basic nodes loaded: HelloString, AnyPassthrough", "INFO")
    _import_stats["success"] += 1
except Exception as e:
    debug_exception("Basic nodes import", e)
    _import_stats["failed"] += 1

# Image Processing Nodes  
try:
    debug_print("🔄 Importing Image nodes...", "DEBUG")
    from .nodes.image import PickByBrightness
    debug_print("✅ Image nodes loaded: PickByBrightness", "INFO")
    _import_stats["success"] += 1
except Exception as e:
    debug_exception("Image nodes import", e)
    _import_stats["failed"] += 1

# Text Processing Nodes
try:
    debug_print("🔄 Importing Text nodes...", "DEBUG")
    from .nodes.text import AppendSuffix
    debug_print("✅ Text nodes loaded: AppendSuffix", "INFO")
    _import_stats["success"] += 1
except Exception as e:
    debug_exception("Text nodes import", e)
    _import_stats["failed"] += 1

# Development Nodes
try:
    debug_print("🔄 Importing Development nodes...", "DEBUG")
    from .nodes.dev_nodes import OutputDev, InputDev
    debug_print("✅ Development nodes loaded: OutputDev, InputDev", "INFO")
    _import_stats["success"] += 1
except Exception as e:
    debug_exception("Development nodes import", e)
    _import_stats["failed"] += 1

# VAE Tools
try:
    debug_print("🔄 Importing VAE tools...", "DEBUG")
    from .nodes.vae_tools import VAERoundTrip, VAEPreview
    debug_print("✅ VAE tools loaded: VAERoundTrip, VAEPreview", "INFO")
    _import_stats["success"] += 1
except Exception as e:
    debug_exception("VAE tools import", e)
    _import_stats["failed"] += 1

# Update total count
_import_stats["total"] = 5

# ═══════════════════════════════════════════════════════════════════════════════
# 🌐 Web Directory Configuration
# ═══════════════════════════════════════════════════════════════════════════════

# If you add frontend assets, keep this path relative to this package root.
WEB_DIRECTORY = "./web"

def scan_web_assets():
    """Enhanced web asset scanning with detailed reporting"""
    if not DEBUG_WEB:
        return
    
    debug_print("🌐 Scanning web assets...", "DEBUG")
    web_path = Path(__file__).parent / "web"
    
    if web_path.exists():
        debug_print(f"✅ Web directory found: {web_path}", "INFO")
        
        # JavaScript extensions
        js_path = web_path / "js" / "xdev.js"
        if js_path.exists():
            size_kb = js_path.stat().st_size / 1024
            debug_print(f"📄 JavaScript: {js_path.name} ({size_kb:.1f} KB)", "DEBUG")
        else:
            debug_print("⚠️  JavaScript extensions not found", "WARN")
        
        # Documentation files
        docs_path = web_path / "docs"
        if docs_path.exists() and docs_path.is_dir():
            doc_files = list(docs_path.glob("*.md"))
            debug_print(f"📚 Documentation: {len(doc_files)} files found", "INFO")
            for doc_file in doc_files:
                debug_print(f"   • {doc_file.name}", "TRACE")
        else:
            debug_print("⚠️  Documentation directory not found", "WARN")
            
        # Calculate total web assets size
        total_size = sum(f.stat().st_size for f in web_path.rglob("*") if f.is_file())
        debug_print(f"📊 Total web assets: {total_size / 1024:.1f} KB", "DEBUG")
        
    else:
        debug_print(f"❌ Web directory not found: {web_path}", "ERROR")

# Scan web assets
scan_web_assets()

# ═══════════════════════════════════════════════════════════════════════════════
# 🗺️  Node Registration & Mapping
# ═══════════════════════════════════════════════════════════════════════════════

debug_print("Building node mappings...", "REG")

# Build node mappings only for successfully imported nodes
NODE_CLASS_MAPPINGS = {}
_available_nodes = []

# Add nodes that imported successfully
if HelloString is not None:
    NODE_CLASS_MAPPINGS["XDEV_HelloString"] = HelloString
    _available_nodes.append("HelloString")
if AnyPassthrough is not None:
    NODE_CLASS_MAPPINGS["XDEV_AnyPassthrough"] = AnyPassthrough
    _available_nodes.append("AnyPassthrough")
if PickByBrightness is not None:
    NODE_CLASS_MAPPINGS["XDEV_PickByBrightness"] = PickByBrightness
    _available_nodes.append("PickByBrightness")
if AppendSuffix is not None:
    NODE_CLASS_MAPPINGS["XDEV_AppendSuffix"] = AppendSuffix
    _available_nodes.append("AppendSuffix")
if OutputDev is not None:
    NODE_CLASS_MAPPINGS["XDEV_OutputDev"] = OutputDev
    _available_nodes.append("OutputDev")
if InputDev is not None:
    NODE_CLASS_MAPPINGS["XDEV_InputDev"] = InputDev
    _available_nodes.append("InputDev")
if VAERoundTrip is not None:
    NODE_CLASS_MAPPINGS["XDEV_VAERoundTrip"] = VAERoundTrip
    _available_nodes.append("VAERoundTrip")
if VAEPreview is not None:
    NODE_CLASS_MAPPINGS["XDEV_VAEPreview"] = VAEPreview
    _available_nodes.append("VAEPreview")

debug_print(f"📝 Successfully registered {len(NODE_CLASS_MAPPINGS)} nodes: {', '.join(_available_nodes)}", "INFO")

NODE_DISPLAY_NAME_MAPPINGS = {
    "XDEV_HelloString": "Hello String (XDev)",
    "XDEV_AnyPassthrough": "Any Passthrough (XDev)",
    "XDEV_PickByBrightness": "Pick Image by Brightness (XDev)",
    "XDEV_AppendSuffix": "Append Suffix (XDev)",
    "XDEV_OutputDev": "Output Dev (XDev)",
    "XDEV_InputDev": "Input Dev (XDev)",
    "XDEV_VAERoundTrip": "VAE Round-Trip (XDev)",
    "XDEV_VAEPreview": "VAE Preview (XDev)",
}

# ═══════════════════════════════════════════════════════════════════════════════
# 🔍 Registration Validation & Summary
# ═══════════════════════════════════════════════════════════════════════════════

def validate_node_registration():
    """Validate node registration and display summary"""
    debug_print("Validating node registrations...", "VAL")
    
    # Check mapping consistency
    class_keys = set(NODE_CLASS_MAPPINGS.keys())
    display_keys = set(NODE_DISPLAY_NAME_MAPPINGS.keys())
    
    if class_keys == display_keys:
        debug_print("✅ Node mapping consistency validated", "VAL")
    else:
        missing_display = class_keys - display_keys
        missing_class = display_keys - class_keys
        if missing_display:
            debug_print(f"❌ Missing display names: {missing_display}", "ERROR")
        if missing_class:
            debug_print(f"❌ Missing class mappings: {missing_class}", "ERROR")
    
    # Validate node classes
    failed_nodes = []
    for node_id, node_class in NODE_CLASS_MAPPINGS.items():
        try:
            # Check required attributes
            if not hasattr(node_class, 'INPUT_TYPES'):
                failed_nodes.append(f"{node_id}: Missing INPUT_TYPES")
            elif not hasattr(node_class, 'RETURN_TYPES'):
                failed_nodes.append(f"{node_id}: Missing RETURN_TYPES")
            elif not hasattr(node_class, 'FUNCTION'):
                failed_nodes.append(f"{node_id}: Missing FUNCTION")
            else:
                # Validate INPUT_TYPES method
                input_types = node_class.INPUT_TYPES()
                if not isinstance(input_types, dict):
                    failed_nodes.append(f"{node_id}: INPUT_TYPES not dict")
        except Exception as e:
            failed_nodes.append(f"{node_id}: Exception during validation: {e}")
    
    if failed_nodes:
        debug_print(f"❌ Node validation failures:", "ERROR")
        for failure in failed_nodes:
            debug_print(f"   • {failure}", "ERROR")
    else:
        debug_print("✅ All nodes passed validation", "VAL")
    
    return len(failed_nodes) == 0

# Run validation
validation_passed = validate_node_registration()

# ═══════════════════════════════════════════════════════════════════════════════
# 📊 Startup Summary
# ═══════════════════════════════════════════════════════════════════════════════

def startup_summary():
    """Display comprehensive startup summary"""
    if not DEBUG_SUMMARY:
        return
        
    total_time = time.time() - _startup_time
    
    debug_print("=" * 60, "INFO", force=True)
    debug_print("🎯 XDev Nodes Startup Summary", "INFO", force=True)
    debug_print("=" * 60, "INFO", force=True)
    
    # Import statistics
    debug_print(f"📊 Import Statistics:", "INFO")
    debug_print(f"   ✅ Successful: {_import_stats['success']}/{_import_stats['total']}", "INFO")
    debug_print(f"   ❌ Failed: {_import_stats['failed']}/{_import_stats['total']}", "INFO")
    if DEBUG_TIMING:
        debug_print(f"   ⏱️  Total time: {total_time:.3f}s", "INFO")
    
    # Node categories
    categories = {
        "Basic Nodes": ["XDEV_HelloString", "XDEV_AnyPassthrough"],
        "Text Processing": ["XDEV_AppendSuffix"],
        "Image Processing": ["XDEV_PickByBrightness"],
        "Development Tools": ["XDEV_OutputDev", "XDEV_InputDev"],
        "VAE Operations": ["XDEV_VAERoundTrip", "XDEV_VAEPreview"]
    }
    
    debug_print("", "INFO")
    for category, nodes in categories.items():
        debug_print(f"📂 {category}:", "INFO")
        for node in nodes:
            display_name = NODE_DISPLAY_NAME_MAPPINGS.get(node, "Unknown")
            status = "✅" if node in NODE_CLASS_MAPPINGS else "❌"
            debug_print(f"   {status} {node} → {display_name}", "INFO")
    
    debug_print("", "INFO")
    debug_print(f"📦 Total Nodes Registered: {len(NODE_CLASS_MAPPINGS)}", "INFO")
    debug_print(f"🌐 Web Assets: {'Available' if (Path(__file__).parent / 'web').exists() else 'Not Found'}", "INFO")
    debug_print(f"✅ Validation: {'Passed' if validation_passed else 'Failed'}", "INFO")
    debug_print("", "INFO")
    debug_print("🚀 XDev Nodes ready for ComfyUI!", "INFO", force=True)
    debug_print("   💡 Testing: InputDev → YourNode → OutputDev", "DEBUG")
    debug_print("   🔄 VAE workflows: VAELoader → InputDev(LATENT) → VAERoundTrip", "DEBUG")
    debug_print("=" * 60, "INFO", force=True)

# Display startup summary
startup_summary()

# ═══════════════════════════════════════════════════════════════════════════════
# 📋 Export Definitions
# ═══════════════════════════════════════════════════════════════════════════════

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS", "WEB_DIRECTORY"]