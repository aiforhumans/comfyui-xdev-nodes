# XDev Nodes Debug Configuration
# This file controls startup debugging behavior for ComfyUI XDev Nodes

# Debug output settings
DEBUG_ENABLED = True
DEBUG_LEVEL = "INFO"  # Options: "ERROR", "WARN", "INFO", "DEBUG", "TRACE"

# Component-specific debugging
DEBUG_IMPORTS = True      # Show node import status
DEBUG_WEB = True          # Show web directory scanning
DEBUG_VALIDATION = True   # Show node validation details
DEBUG_SUMMARY = True      # Show startup summary

# Visual formatting
DEBUG_USE_COLORS = True   # ANSI color coding for better readability
DEBUG_USE_BANNER = True   # Show startup banner
DEBUG_USE_EMOJIS = True   # Use emoji indicators (✅❌⚠️)

# Performance monitoring
DEBUG_TIMING = False      # Show timing information for each step
DEBUG_MEMORY = False      # Show memory usage (requires psutil)

# Advanced debugging
DEBUG_TRACEBACK = False   # Show full tracebacks for errors
DEBUG_NODE_DETAILS = False # Show detailed node inspection