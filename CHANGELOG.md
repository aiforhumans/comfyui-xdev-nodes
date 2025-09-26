# Changelog

All notable changes to ComfyUI XDev Nodes will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.0] - 2024-12-26

### Added
- **Complete Development Toolkit**: Expanded from 4 to 8 professional nodes
- **VAE Tools**: New `VAERoundTrip` and `VAEPreview` nodes for complete VAE workflow testing
  - VAERoundTrip: Full LATENT→DECODE→ENCODE→LATENT cycle with quality analysis
  - VAEPreview: Quick latent visualization with comprehensive analysis
- **Universal Testing Infrastructure**: Enhanced development nodes
  - OutputDev: Universal debugging output accepting all 18 ComfyUI types
  - InputDev: Test data generator for 12 core ComfyUI types
- **Advanced Type Compatibility**: Complete support for all ComfyUI data types
- **Professional Workflows**: Example chains for VAE testing and type validation
- **Enhanced Documentation**: Comprehensive README with all 8 nodes documented

### Changed
- Updated project description to reflect complete toolkit nature
- Enhanced README with comprehensive node documentation and use cases
- Bumped version to 0.2.0 for major feature additions

### Technical
- All nodes follow ComfyUI official patterns (validated against ComfyUI source)
- Proper type definitions matching VAEDecode/VAEEncode standards
- Professional error handling and graceful fallbacks
- Memory analysis and performance monitoring capabilities

## [0.1.1] - 2024-12-19

### Added
- Comprehensive GitHub standards implementation
- Professional development patterns and validation
- Enhanced documentation system
- Security guidelines and best practices

## [1.0.0] - 2024-12-19

### Added
- **Professional Enhancement**: Complete overhaul to professional-grade ComfyUI node framework
- **Comprehensive Input Validation**: Detailed type checking with informative error messages for all nodes
- **Rich Tooltip Documentation**: Professional-grade help text and parameter descriptions
- **Enhanced Error Handling**: Graceful degradation and fallback implementations
- **Multiple Output Patterns**: Enhanced return types with metadata and processing information
- **GitHub Standards**: Complete CONTRIBUTING.md, CODE_OF_CONDUCT.md, SECURITY.md implementation
- **Advanced PickByBrightness**: Multiple algorithms (average, luminance, perceived, channel_max) with robust fallbacks
- **Professional AppendSuffix**: Multiline support, comprehensive validation, processing statistics
- **Enhanced HelloString**: Validation framework demonstration with professional patterns
- **Type-Safe AnyPassthrough**: Comprehensive type checking and processing metadata
- **Web Documentation System**: Rich markdown documentation for all nodes
- **Security Best Practices**: ComfyUI-specific security guidelines and safe coding patterns

### Enhanced
- **HelloString (XDev)**: Added comprehensive input validation framework and professional error handling
- **AnyPassthrough (XDev)**: Enhanced with type validation, null handling, and processing statistics
- **AppendSuffix (XDev)**: Added multiline text support, validation patterns, and character counting
- **PickByBrightness (XDev)**: Multiple brightness algorithms, torch/numpy/python fallbacks, enhanced outputs

### Technical Improvements
- Smart caching with proper `IS_CHANGED` implementation
- Robust fallback patterns for missing dependencies
- Professional error handling without workflow crashes
- Resource management and performance optimization
- Comprehensive test coverage with validation scenarios

### Documentation
- Enhanced README with professional formatting and feature highlights
- Web-based help system with detailed node documentation
- Contribution guidelines with development patterns
- Security policy with ComfyUI-specific considerations
- Code of conduct with educational community focus

### Infrastructure
- GitHub Actions CI/CD pipeline with comprehensive testing
- Professional development scripts (dev-link.ps1, dev-link.sh)
- Code quality tools (ruff, pytest) with proper configuration
- Issue and PR templates for structured contributions

## [0.1.0] - 2024-12-01

### Added
- Initial release with basic ComfyUI node patterns
- Basic node examples: HelloString, AnyPassthrough, AppendSuffix, PickByBrightness
- Minimal ComfyUI integration patterns
- Basic CI/CD pipeline
- Simple documentation and examples

### Features
- **HelloString**: Basic static string output
- **AnyPassthrough**: Simple value passthrough
- **AppendSuffix**: Basic string concatenation
- **PickByBrightness**: Simple brightness-based image selection

### Infrastructure
- Basic pyproject.toml configuration
- Simple test suite
- GitHub Actions workflow
- Example workflows for testing

---

## Version History Summary

| Version | Release Date | Key Features | Breaking Changes |
|---------|--------------|--------------|------------------|
| **1.0.0** | 2024-12-19 | Professional patterns, validation, GitHub standards | Enhanced APIs (backward compatible) |
| **0.1.0** | 2024-12-01 | Initial basic patterns | N/A (initial release) |

---

## Migration Guide

### Upgrading from 0.1.x to 1.0.x

**✅ Backward Compatible**: All existing workflows continue to work unchanged.

**🎉 New Features Available**:
- Enhanced validation provides better error messages
- Rich tooltips improve user experience
- Additional output metadata available (optional)
- Multiple algorithms for PickByBrightness

**🔧 Optional Enhancements**:
```python
# New validation patterns available
if hasattr(node, '_validate_inputs'):
    validation = node._validate_inputs(**inputs)
    if not validation['valid']:
        # Handle validation errors gracefully

# Enhanced PickByBrightness algorithms
# Old: mode parameter (still works)
# New: algorithm parameter for more options
```

---

## Development Notes

### Version Numbering
- **MAJOR**: Breaking changes to node APIs or ComfyUI compatibility
- **MINOR**: New features, enhanced functionality (backward compatible)
- **PATCH**: Bug fixes, documentation updates, minor improvements

### Release Process
1. Update version in `pyproject.toml`
2. Update `CHANGELOG.md` with new version
3. Create GitHub release with tag `v{version}`
4. CI automatically runs tests and validation
5. ComfyUI Manager picks up new version

### Compatibility Promise
- **Node IDs**: Never change existing node IDs (breaks workflows)
- **Core Inputs/Outputs**: Maintain backward compatibility
- **ComfyUI Integration**: Follow ComfyUI's API evolution
- **Dependencies**: Maintain fallback patterns for optional dependencies

---

## Contributors

- [@aiforhumans](https://github.com/aiforhumans) - Project creator and maintainer
- Community contributors - See [GitHub Contributors](https://github.com/aiforhumans/comfyui-xdev-nodes/contributors)

---

## Support

- 🐛 **Bug Reports**: [GitHub Issues](https://github.com/aiforhumans/comfyui-xdev-nodes/issues)
- 💡 **Feature Requests**: [GitHub Issues](https://github.com/aiforhumans/comfyui-xdev-nodes/issues)
- 📖 **Documentation**: [README](README.md) | [Web Docs](xdev_nodes/web/docs/)
- 🛡️ **Security**: [Security Policy](SECURITY.md)
- 🤝 **Contributing**: [Contributing Guidelines](CONTRIBUTING.md)

---

*This changelog follows [Keep a Changelog](https://keepachangelog.com/) format for clear communication of changes.*