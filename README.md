# Ilograph MCP Server

A comprehensive Model Context Protocol (MCP) server for automated Ilograph diagram generation from codebases. This server analyzes source code across multiple programming languages and generates native .ilograph files that can be opened directly in the Ilograph editor, with optional rendering via the Ilograph Export API.

## 🚀 Features

- **Native .ilograph File Generation**: Creates .ilograph files that open directly in Ilograph editor
- **Multi-Language Support**: Analyze Python, JavaScript/TypeScript, and Java codebases  
- **MCP Protocol Compliance**: Full integration with AI assistants (JetBrains AI Assistant, GitHub Copilot)
- **Optional Export API Integration**: Render diagrams as SVG, PNG, HTML, or PDF (requires API key)
- **Multiple Perspectives**: Generate diagrams from different architectural viewpoints
- **Containerized Deployment**: Docker support with multi-stage builds
- **Production Ready**: Comprehensive logging, monitoring, and error handling
- **Extensible Architecture**: Modular design for easy language and feature additions

## 📋 Requirements

- Python 3.10 or higher
- Docker (optional, for containerized deployment)
- Ilograph API key (for diagram rendering)

## 🛠️ Installation

### Using pip

```bash
# Clone the repository
git clone https://github.com/your-org/ilograph-mcp-server.git
cd ilograph-mcp-server

# Install dependencies
pip install -e .

# Or with development dependencies
pip install -e ".[dev]"
```

### Using Docker

```bash
# Build the Docker image
docker build -t ilograph-mcp-server .

# Run the container
docker run -p 8000:8000 -e ILOGRAPH_API_KEY=your_key_here ilograph-mcp-server
```

## ⚙️ Configuration

Copy the example environment file and configure your settings:

```bash
cp env.example .env
```

Key configuration options:

- `ILOGRAPH_API_KEY`: Your Ilograph API key for rendering diagrams (optional, only needed for SVG/PNG/PDF export)
- `MCP_HOST`: Server host (default: localhost)
- `MCP_PORT`: Server port (default: 8000)
- `LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR)

## 🚦 Usage

### Running the Server

```bash
# Start the MCP server
python -m src.main serve

# Or with custom settings
python -m src.main serve --host 0.0.0.0 --port 8080
```

### CLI Analysis

```bash
# Analyze a codebase and generate .ilograph file (default)
python -m src.main analyze /path/to/project

# Generate with custom output path
python -m src.main analyze /path/to/project --output my-architecture.ilograph

# Generate SVG diagram (requires API key)
python -m src.main analyze /path/to/project --format svg --output diagram.svg
```

### MCP Tools

The server exposes the following MCP tools:

1. **analyze_codebase**: Extract architectural information from source code
2. **generate_diagram**: Create Ilograph diagrams from analysis results
3. **render_diagram**: Render diagrams using Ilograph Export API
4. **save_diagram**: Save diagrams to files
5. **get_supported_languages**: List supported programming languages
6. **health_check**: Check server health status

## 🏗️ Architecture

```
src/
├── analysis/           # Code analysis modules
│   ├── base.py        # Base analyzer classes
│   ├── python_analyzer.py
│   ├── javascript_analyzer.py
│   ├── java_analyzer.py
│   └── factory.py     # Analyzer factory
├── diagram/           # Diagram generation
│   ├── ilograph.py    # Ilograph schema handling
│   ├── renderer.py    # API rendering
│   └── perspectives.py
├── mcp/              # MCP server implementation
│   ├── server.py     # Main server
│   └── tools.py      # MCP tools
└── utils/            # Utilities
    ├── config.py     # Configuration management
    └── logging_config.py
```

## 🔌 JetBrains AI Assistant Integration

1. Install and configure JetBrains AI Assistant
2. Add the MCP server configuration:
   ```json
   {
     "name": "Ilograph Diagram Generator",
     "url": "http://localhost:8000",
     "enabled": true
   }
   ```
3. Use the AI assistant to analyze your codebase and generate diagrams

## 🐳 Docker Deployment

### Docker Compose

```yaml
version: '3.8'
services:
  ilograph-mcp:
    build: .
    ports:
      - "8000:8000"
    environment:
      - ILOGRAPH_API_KEY=${ILOGRAPH_API_KEY}
      - LOG_LEVEL=INFO
    volumes:
      - ./output:/app/output
      - ./logs:/app/logs
```

### Kubernetes

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ilograph-mcp-server
spec:
  replicas: 3
  selector:
    matchLabels:
      app: ilograph-mcp-server
  template:
    metadata:
      labels:
        app: ilograph-mcp-server
    spec:
      containers:
      - name: server
        image: ilograph-mcp-server:latest
        ports:
        - containerPort: 8000
        env:
        - name: ILOGRAPH_API_KEY
          valueFrom:
            secretKeyRef:
              name: ilograph-secret
              key: api-key
```

## 🧪 Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test modules
pytest tests/test_analysis.py
```

## 📝 Development

### Setup Development Environment

```bash
# Install development dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install

# Run linting
black src/ tests/
isort src/ tests/
flake8 src/ tests/
mypy src/
```

### Adding New Language Support

1. Create a new analyzer in `src/analysis/`
2. Implement the `CodeAnalyzer` interface
3. Register the analyzer in `factory.py`
4. Add tests for the new analyzer

## 📊 Monitoring

The server provides health check endpoints and Prometheus metrics:

- `/health`: Health check endpoint
- `/metrics`: Prometheus metrics

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Run the test suite
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.

## 🆘 Support

- Create an issue for bug reports or feature requests
- Contact the maintainers for enterprise support

## 🔗 Related Projects

- [Ilograph](https://www.ilograph.com/) - Interactive architecture diagrams
- [Model Context Protocol](https://modelcontextprotocol.io/) - MCP specification
- [FastMCP](https://github.com/jlowin/fastmcp) - FastMCP framework
