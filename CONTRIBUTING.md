# Contributing to XDev ComfyUI Nodes

🎉 Thank you for your interest in contributing to the XDev ComfyUI Nodes project! This guide will help you get started with contributing to our educational ComfyUI custom node framework.

## 🎯 Project Mission

XDev serves as a **starter kit and educational framework** for ComfyUI custom node development, demonstrating:
- Professional node development patterns
- Comprehensive input validation and error handling  
- Rich documentation and tooltip systems
- Production-ready testing and CI workflows

## 🚀 Quick Start for Contributors

### Prerequisites

- **Python 3.10+** (recommended: 3.11)
- **ComfyUI installation** for testing nodes
- **Git** for version control
- **Basic understanding** of ComfyUI workflows (helpful but not required)

### Development Setup

1. **Fork and Clone**
   ```bash
   git clone https://github.com/YOUR_USERNAME/comfyui-xdev-nodes.git
   cd comfyui-xdev-nodes
   ```

2. **Create Development Environment**
   ```bash
   # Optional: Create virtual environment
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   
   # Install in development mode
   pip install -e .
   ```

3. **Link to ComfyUI** (for testing)
   ```bash
   # Windows
   scripts/dev-link.ps1
   
   # Unix/Linux/Mac
   scripts/dev-link.sh
   ```

4. **Verify Setup**
   ```bash
   # Test imports
   python -c "import xdev_nodes; print('XDev nodes loaded successfully!')"
   
   # Run basic tests
   python -c "from xdev_nodes.nodes.basic import HelloString; print(HelloString().hello())"
   ```

## 📋 Types of Contributions

We welcome several types of contributions:

### 🐛 Bug Reports
- **Issues with existing nodes** (validation, error handling, performance)
- **Documentation errors** or unclear instructions  
- **Compatibility problems** with different ComfyUI versions
- **CI/testing failures** or environment issues

### ✨ Feature Enhancements
- **New example nodes** demonstrating ComfyUI patterns
- **Enhanced validation patterns** with better error messages
- **Documentation improvements** (tooltips, web docs, guides)
- **Testing infrastructure** improvements

### 📚 Documentation
- **Tutorial content** for ComfyUI node development
- **Code examples** and workflow demonstrations
- **API documentation** and pattern explanations
- **Translation contributions** for internationalization

### 🔧 Infrastructure
- **CI/CD improvements** (GitHub Actions, testing)
- **Development tooling** (linting, formatting, type checking)
- **Build and packaging** enhancements
- **Performance optimizations**

## 🛠️ Development Guidelines

### Code Style

We follow **professional Python standards** with specific patterns for ComfyUI:

```python
# Node structure example
class ExampleNode:
    """
    Brief description of node functionality.
    
    Demonstrates XDev patterns including validation, tooltips, and error handling.
    """
    
    @classmethod
    def INPUT_TYPES(cls) -> Dict[str, Dict[str, Any]]:
        return {
            "required": {
                "param": ("STRING", {
                    "default": "default_value",
                    "tooltip": "Clear description of parameter purpose and usage"
                })
            },
            "optional": {
                "validate_input": ("BOOLEAN", {
                    "default": True,
                    "tooltip": "Enable input validation with detailed error messages"
                })
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("result", "info")
    FUNCTION = "process"
    CATEGORY = "XDev/Category"
    DESCRIPTION = "Brief node description for UI"
    
    def process(self, param: str, validate_input: bool = True) -> Tuple[str, str]:
        """Process with validation and error handling."""
        try:
            if validate_input:
                validation = self._validate_inputs(param)
                if not validation["valid"]:
                    return (f"Error: {validation['error']}", "Validation failed")
            
            # Process logic here
            result = f"Processed: {param}"
            return (result, "Success")
            
        except Exception as e:
            return (f"Error: {str(e)}", f"Exception: {type(e).__name__}")
    
    def _validate_inputs(self, param: str) -> Dict[str, Any]:
        """Comprehensive input validation with detailed messages."""
        if not isinstance(param, str):
            return {
                "valid": False,
                "error": f"Expected string, got {type(param).__name__}"
            }
        return {"valid": True, "error": None}
```

### Testing Requirements

All contributions should include appropriate testing:

```python
# Example test for new nodes
def test_example_node():
    from xdev_nodes.nodes.category import ExampleNode
    
    node = ExampleNode()
    
    # Test normal operation
    result = node.process("test_input")
    assert result[0].startswith("Processed:")
    assert result[1] == "Success"
    
    # Test validation
    error_result = node.process(123)  # Invalid type
    assert "Error:" in error_result[0]
    assert "Validation failed" in error_result[1]
```

### Documentation Standards

- **Rich tooltips** for all input parameters
- **Comprehensive docstrings** for classes and methods
- **Web documentation** in `xdev_nodes/web/docs/` for complex nodes
- **Usage examples** in docstrings and documentation files

## 📝 Contribution Process

### 1. Planning Phase

**Before starting work:**
- 🔍 **Search existing issues** to avoid duplicates
- 💬 **Discuss major changes** in issues before implementation
- 📋 **Follow issue templates** for bug reports and feature requests
- ✅ **Get feedback** on your approach before coding

### 2. Development Phase

**While working:**
- 🌿 **Create feature branch** from `main`: `git checkout -b feature/your-feature-name`
- ✅ **Write tests first** (TDD approach recommended)
- 📚 **Document as you go** (tooltips, docstrings, web docs)
- 🧪 **Test locally** with ComfyUI before submitting

### 3. Submission Phase

**When submitting:**
- ✅ **Run validation checks** (see Checklist below)
- 📝 **Follow PR template** with detailed description
- 🔗 **Link related issues** using keywords (Fixes #123)
- 👀 **Request review** from maintainers

### Pull Request Checklist

Before submitting your PR, verify:

#### Code Quality
- [ ] Code follows XDev patterns (validation, tooltips, error handling)
- [ ] All new nodes include comprehensive input validation
- [ ] Rich tooltips provided for all parameters
- [ ] Proper error handling with graceful degradation
- [ ] Type hints used throughout

#### Testing
- [ ] New functionality includes tests
- [ ] All existing tests still pass
- [ ] Manual testing performed with ComfyUI
- [ ] Edge cases and error conditions tested

#### Documentation  
- [ ] Docstrings added/updated for new code
- [ ] Web documentation created for complex nodes
- [ ] README updated if needed
- [ ] Examples provided for new features

#### Compatibility
- [ ] Backward compatibility maintained (no breaking changes to existing node IDs)
- [ ] Works with ComfyUI 1.0+ (check `pyproject.toml` requirements)
- [ ] Cross-platform compatibility considered (Windows/Linux/Mac)

## 🎯 Specific Contribution Areas

### Adding New Example Nodes

We're particularly interested in nodes that demonstrate:

1. **Advanced ComfyUI Features**
   - Lazy evaluation patterns
   - Custom data types
   - List processing capabilities
   - Node expansion techniques

2. **Professional Patterns**
   - Complex input validation scenarios
   - Multi-format data handling (torch/numpy/python fallbacks)
   - Performance optimization techniques
   - Internationalization examples

3. **Educational Value**
   - Clear, well-documented implementations
   - Progressive complexity (basic → intermediate → advanced)
   - Common use-case demonstrations
   - Best practice showcases

### Documentation Improvements

Help improve our educational mission:

- **Tutorial Content**: Step-by-step node development guides
- **Pattern Documentation**: Detailed explanations of XDev patterns
- **Video Tutorials**: Screen recordings of development process
- **Troubleshooting Guides**: Common issues and solutions

### Infrastructure Enhancements

Technical improvements welcome:

- **CI/CD**: Enhanced GitHub Actions workflows
- **Testing**: Expanded test coverage and validation
- **Tooling**: Development experience improvements
- **Performance**: Optimization and benchmarking

## 🤝 Community Guidelines

### Communication

- 💬 **Be respectful** and constructive in all interactions
- 🆘 **Ask for help** when needed - we're here to support contributors
- 📖 **Share knowledge** - help others learn ComfyUI development
- 🔍 **Search first** before asking questions that may already be answered

### Code Review Process

- 👀 **Reviews are learning opportunities** for everyone
- ✅ **Address feedback constructively** and promptly
- 🔄 **Iterate and improve** based on suggestions
- 🎉 **Celebrate contributions** - every improvement matters!

### Recognition

We value all contributions:
- 🏆 **Contributors** listed in README and release notes
- 📈 **Growth mindset** - we help contributors develop skills
- 🎓 **Learning focus** - educational value prioritized
- 🌟 **Quality over quantity** - well-crafted contributions appreciated

## 🔧 Advanced Development

### Custom Node Development

For complex custom nodes, follow the XDev enhancement patterns:

```python
# Enhanced validation example
def _validate_inputs(self, param1, param2) -> Dict[str, Any]:
    """Comprehensive validation with specific error messages."""
    
    # Type validation
    if not isinstance(param1, str):
        return {
            "valid": False,
            "error": f"Parameter 1 must be string, got {type(param1).__name__}. "
                    "Convert input to string format."
        }
    
    # Range validation  
    if len(param1) > 10000:
        return {
            "valid": False,
            "error": f"Parameter 1 too long ({len(param1)} chars). "
                    "Maximum supported length is 10,000 characters."
        }
    
    # Business logic validation
    if param2 not in ["option1", "option2", "option3"]:
        return {
            "valid": False,
            "error": f"Invalid option '{param2}'. "
                    "Must be one of: option1, option2, option3"
        }
    
    return {"valid": True, "error": None}
```

### Web Documentation

Create comprehensive guides in `xdev_nodes/web/docs/`:

```markdown
# Node Name (XDev) - Enhanced Documentation

## Overview
Brief description with key features...

## Features
- ✨ Feature 1: Description
- 🛡️ Feature 2: Description  

## Parameters
Detailed parameter tables...

## Usage Examples
Multiple real-world scenarios...

## Advanced Features
In-depth technical details...

## Troubleshooting
Common issues and solutions...
```

## 🚨 Getting Help

### Resources

- 📖 **Documentation**: Start with README and web docs
- 💡 **Examples**: Check existing nodes for patterns
- 🔧 **Development**: Use dev-link scripts for local testing
- 📋 **Issues**: Search existing issues before creating new ones

### Support Channels

- 🐛 **Bug Reports**: Use GitHub issues with reproduction steps
- 💬 **Questions**: GitHub Discussions for general help
- 🚀 **Feature Ideas**: GitHub Issues with feature request template
- 📧 **Direct Contact**: Maintainer contact in README

### Quick Debug Tips

```bash
# Test node imports
python -c "from xdev_nodes.nodes.basic import HelloString; print('OK')"

# Validate node structure
python -c "
from xdev_nodes.nodes.basic import HelloString
node = HelloString()
print('INPUT_TYPES:', hasattr(node, 'INPUT_TYPES'))
print('RETURN_TYPES:', hasattr(node, 'RETURN_TYPES'))
print('FUNCTION:', hasattr(node, node.FUNCTION if hasattr(node, 'FUNCTION') else 'missing'))
"

# Test in ComfyUI
# 1. Use dev-link scripts
# 2. Restart ComfyUI
# 3. Check for XDev nodes in node menu
# 4. Load example workflows from workflows/
```

---

## 🎉 Thank You!

Your contributions help make ComfyUI custom node development more accessible and professional for everyone. Whether you're fixing a typo, adding a feature, or helping other developers learn, every contribution matters!

**Happy coding!** 🚀