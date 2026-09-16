# Multi-stage build for smaller image size
FROM python:3.11-slim as builder

# Set working directory
WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency files
COPY pyproject.toml ./
COPY README.md ./

# Copy source code
COPY src/ ./src/

# Install dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -e .

# Runtime stage
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY --from=builder /app/src ./src

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Labels for metadata
LABEL maintainer="Ajay Jain"
LABEL description="Atlassian MCP Server for Jira integration"
LABEL version="0.1.0"

# Health check (optional, for future HTTP endpoint)
# HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
#   CMD python -c "import sys; sys.exit(0)"

# Run the MCP server
ENTRYPOINT ["python", "-m", "atlassian_mcp_server"]
