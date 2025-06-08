# Use multi-stage build for better caching and smaller final image
FROM python:3.13-slim as builder

# Add metadata labels
LABEL org.opencontainers.image.title="Ilograph MCP Server"
LABEL org.opencontainers.image.description="FastMCP server providing AI agents with comprehensive Ilograph documentation and validation tools"
LABEL org.opencontainers.image.url="https://github.com/QuincyMillerDev/ilograph-mcp-server"
LABEL org.opencontainers.image.source="https://github.com/QuincyMillerDev/ilograph-mcp-server"
LABEL org.opencontainers.image.version="0.1.0"
LABEL org.opencontainers.image.created="2025-01-27"
LABEL org.opencontainers.image.licenses="MIT"
LABEL org.opencontainers.image.vendor="QuincyMillerDev"

# Install uv from the official distroless image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set working directory
WORKDIR /app

# Copy dependency files first for better Docker layer caching
COPY pyproject.toml uv.lock ./

# Install dependencies only (not the project itself yet)
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-install-project --no-editable

# Copy the entire project
COPY . .

# Install the project itself
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-editable

# Production stage
FROM python:3.13-slim

# Add metadata labels to final image
LABEL org.opencontainers.image.title="Ilograph MCP Server"
LABEL org.opencontainers.image.description="FastMCP server providing AI agents with comprehensive Ilograph documentation and validation tools"
LABEL org.opencontainers.image.url="https://github.com/QuincyMillerDev/ilograph-mcp-server"
LABEL org.opencontainers.image.source="https://github.com/QuincyMillerDev/ilograph-mcp-server"
LABEL org.opencontainers.image.version="0.1.0"
LABEL org.opencontainers.image.created="2025-01-27"
LABEL org.opencontainers.image.licenses="MIT"
LABEL org.opencontainers.image.vendor="QuincyMillerDev"

# Create non-root user for security
RUN groupadd --gid 1000 app && \
    useradd --uid 1000 --gid app --shell /bin/bash --create-home app

# Set working directory
WORKDIR /app

# Copy the virtual environment from builder stage
COPY --from=builder --chown=app:app /app/.venv /app/.venv

# Copy the project source code
COPY --from=builder --chown=app:app /app/src /app/src

# Make sure the virtual environment is used
ENV PATH="/app/.venv/bin:$PATH"

# Switch to non-root user
USER app

# Health check for container monitoring
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import ilograph_mcp.server; print('Health check passed')" || exit 1

# Run the MCP server
CMD ["python", "-m", "ilograph_mcp.server"] 