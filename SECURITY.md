# Security Policy

## Supported Versions

We actively maintain and provide security updates for the following versions:

| Version | Supported          | ComfyUI Compatibility |
| ------- | ------------------ | -------------------- |
| 1.0.x   | :white_check_mark: | >= 1.0.0            |
| < 1.0   | :x:                | Various              |

## Reporting a Vulnerability

We take security vulnerabilities seriously. If you discover a security vulnerability in XDev ComfyUI Nodes, please report it responsibly by following these steps:

### Reporting Process

1. **DO NOT** create a public GitHub issue for security vulnerabilities
2. **DO** report security issues by emailing: **security@aiforhumans.dev** (if available)
3. **OR** report via GitHub's private vulnerability reporting:
   - Go to the repository's Security tab
   - Click "Report a vulnerability"
   - Fill out the private advisory form

### Information to Include

When reporting a vulnerability, please provide:

- **Description**: Clear description of the vulnerability
- **Steps to Reproduce**: Detailed steps to reproduce the issue
- **Impact Assessment**: Potential impact and attack scenarios
- **Affected Versions**: Which versions are affected
- **Proof of Concept**: Code, screenshots, or logs demonstrating the issue
- **Suggested Fix**: If you have ideas for remediation

### Response Timeline

- **Initial Response**: Within 24-48 hours of report
- **Triage**: Within 1 week - we'll assess severity and impact
- **Progress Updates**: Weekly updates on investigation and fix development
- **Resolution**: Timeline depends on severity and complexity
- **Public Disclosure**: After fix is released (coordinated disclosure)

## Security Considerations for ComfyUI Custom Nodes

### Critical Security Risks

ComfyUI custom nodes run with full system privileges and pose significant security risks:

#### 1. Arbitrary Code Execution
- Custom nodes can execute any Python code
- Malicious nodes can compromise the entire system
- **Mitigation**: Only install nodes from trusted sources

#### 2. File System Access
- Unrestricted read/write/delete access to file system
- Can access sensitive files outside ComfyUI directory
- **Mitigation**: Run ComfyUI with limited user privileges

#### 3. Network Access
- Nodes can make arbitrary network requests
- Risk of data exfiltration or malicious downloads
- **Mitigation**: Use network firewalls and monitoring

#### 4. Dependency Injection
- Malicious dependencies via requirements.txt
- Supply chain attacks through PyPI packages
- **Mitigation**: Pin dependency versions, use virtual environments

### XDev Specific Security Measures

Our nodes implement several security best practices:

#### Input Validation
```python
def _validate_inputs(self, **kwargs) -> Dict[str, Any]:
    """Comprehensive input validation with detailed error reporting."""
    for param_name, param_value in kwargs.items():
        if not isinstance(param_value, expected_type):
            return {
                "valid": False,
                "error": f"Invalid {param_name}: expected {expected_type.__name__}, got {type(param_value).__name__}"
            }
    return {"valid": True, "error": None}
```

#### Safe File Handling
```python
def safe_file_path(self, filepath: str) -> str:
    """Validate file paths to prevent directory traversal."""
    # Prevent directory traversal attacks
    if '..' in filepath or filepath.startswith('/') or ':' in filepath:
        raise ValueError("Invalid file path detected")
    
    # Restrict to allowed directories
    allowed_base = os.path.abspath("./allowed_directory")
    full_path = os.path.abspath(filepath)
    if not full_path.startswith(allowed_base):
        raise ValueError("File path outside allowed directory")
    
    return full_path
```

#### Resource Management
```python
def process_with_limits(self, data):
    """Process data with memory and time limits."""
    import resource
    import signal
    
    # Set memory limit (1GB)
    resource.setrlimit(resource.RLIMIT_AS, (1024*1024*1024, 1024*1024*1024))
    
    # Set timeout (30 seconds)
    signal.alarm(30)
    
    try:
        return self.process(data)
    finally:
        signal.alarm(0)  # Clear timeout
```

### Security Guidelines for Developers

#### Safe Coding Practices

1. **Input Sanitization**
   - Validate all user inputs
   - Use parameterized queries for any database operations
   - Sanitize file paths to prevent directory traversal

2. **Dependency Management**
   - Pin exact dependency versions in requirements.txt
   - Regularly audit dependencies for vulnerabilities
   - Use minimal required permissions

3. **Error Handling**
   - Don't expose sensitive information in error messages
   - Log security events appropriately
   - Fail securely when errors occur

4. **Resource Limits**
   - Implement timeouts for long-running operations
   - Set memory limits to prevent DoS attacks
   - Validate file sizes and processing limits

#### Code Review Checklist

- [ ] Input validation for all user-provided data
- [ ] File path sanitization and directory restrictions
- [ ] Network request validation and rate limiting
- [ ] Memory and CPU usage limits
- [ ] Error messages don't expose sensitive data
- [ ] Dependencies are pinned and from trusted sources
- [ ] No hardcoded secrets or credentials
- [ ] Proper exception handling

### Users: Protecting Your System

#### Installation Security

1. **Trusted Sources Only**
   - Install nodes only from reputable developers
   - Review source code when possible
   - Check for community feedback and reviews

2. **Environment Isolation**
   - Use virtual environments for ComfyUI
   - Run with limited user privileges (not as admin/root)
   - Consider containerization (Docker) for isolation

3. **System Hardening**
   - Keep ComfyUI and Python updated
   - Use firewall to limit network access
   - Regular security scans and updates

#### Monitoring and Detection

- Monitor file system changes in ComfyUI directory
- Watch for unexpected network connections
- Check process execution and resource usage
- Regular backup of important workflows and models

### Emergency Response

If you suspect a security compromise:

1. **Immediate Actions**
   - Stop ComfyUI immediately
   - Disconnect from network if possible
   - Backup current state for analysis

2. **Investigation**
   - Check system logs for suspicious activity
   - Scan for modified files or new processes
   - Review recently installed custom nodes

3. **Recovery**
   - Remove suspicious custom nodes
   - Restore from clean backups if needed
   - Update all software and dependencies
   - Change any potentially compromised credentials

## Vulnerability Disclosure Policy

### Coordinated Disclosure

We follow responsible disclosure principles:

1. **Private Reporting**: Report vulnerabilities privately first
2. **Investigation Period**: Allow reasonable time for investigation and fix
3. **Coordinated Release**: Public disclosure after fix is available
4. **Credit**: Security researchers receive appropriate recognition

### Disclosure Timeline

- **Day 0**: Vulnerability reported privately
- **Day 1-7**: Initial triage and assessment
- **Day 7-30**: Investigation and fix development
- **Day 30-60**: Testing and validation of fix
- **Day 60+**: Public disclosure and release

We may request extended timelines for complex vulnerabilities requiring coordination with upstream projects (ComfyUI, PyTorch, etc.).

## Security Updates

### Notification Channels

Stay informed about security updates:

- **GitHub Security Advisories**: Automatic notifications for repository watchers
- **Release Notes**: Security fixes highlighted in CHANGELOG.md
- **README**: Security status and latest secure version information

### Update Process

When security updates are released:

1. **Review**: Read security advisory and assess impact
2. **Test**: Test update in safe environment first
3. **Update**: Update to latest secure version promptly
4. **Verify**: Confirm update addresses the vulnerability
5. **Monitor**: Watch for any issues post-update

## Additional Resources

### Security Tools and Best Practices

- **Static Analysis**: Use tools like `bandit` for Python security scanning
- **Dependency Scanning**: Regular checks with `safety` or `pip-audit`
- **Code Review**: Security-focused code reviews for all changes
- **Testing**: Include security test cases in automated testing

### Learning Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Python Security Guidelines](https://python-security.readthedocs.io/)
- [Secure Coding Practices](https://wiki.sei.cmu.edu/confluence/display/seccode)
- [ComfyUI Security Considerations](https://github.com/comfyanonymous/ComfyUI/security)

---

**Remember**: Security is a shared responsibility. Report vulnerabilities responsibly, keep your systems updated, and follow secure development practices. 🔒