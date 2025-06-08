# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| Latest  | :white_check_mark: |

## Reporting a Vulnerability

If you discover a security vulnerability in the Ilograph MCP Server, please report it responsibly:

### 🔒 How to Report

1. **Do NOT open a public issue** for security vulnerabilities
2. **Email**: Open a [private security advisory](https://github.com/QuincyMillerDev/ilograph-mcp-server/security/advisories/new) on GitHub
3. **Include**: 
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if known)

### 📋 What to Expect

- **Acknowledgment**: Within 48 hours
- **Initial Assessment**: Within 1 week
- **Regular Updates**: Every 72 hours until resolved
- **Credit**: Public acknowledgment in release notes (if desired)

### 🛡️ Security Best Practices

When using this MCP server:

- Always use the latest Docker image
- Review Docker logs for unexpected behavior
- Limit network access if running locally
- Keep your MCP client updated

## Scope

This security policy covers:
- The core MCP server implementation
- Docker container security
- Documentation access patterns
- API interactions with Ilograph services

**Note**: This project accesses public Ilograph documentation only. No private data is processed or stored. 