# Docker Deployment Guide

## Quick Start with Docker

### Prerequisites
- Docker Desktop installed and running
- Atlassian API token (see QUICKSTART.md)

### 1. Build the Docker Image

```bash
cd /Users/ajain/pcp-repos/atlassian-mcp-server

# Build image
docker build -t atlassian-mcp-server:latest .

# Verify build
docker images | grep atlassian-mcp-server
```

### 2. Run with Docker Run

```bash
docker run -it --rm \
  -e ATLASSIAN_CLOUD_ID="picarro.atlassian.net" \
  -e ATLASSIAN_EMAIL="your-email@picarro.com" \
  -e ATLASSIAN_API_TOKEN="your-token-here" \
  -e JIRA_DEFAULT_PROJECT="PH" \
  atlassian-mcp-server:latest
```

### 3. Run with Docker Compose (Recommended)

```bash
# Create .env file
cat > .env << 'EOF'
ATLASSIAN_CLOUD_ID=picarro.atlassian.net
ATLASSIAN_EMAIL=your-email@picarro.com
ATLASSIAN_API_TOKEN=your-token-here
JIRA_DEFAULT_PROJECT=PH
MCP_LOG_LEVEL=INFO
EOF

# Start the service
docker compose up -d

# View logs
docker compose logs -f

# Stop the service
docker compose down
```

## Configure Cursor with Dockerized Server

### Option 1: Named Pipe (Recommended for Docker)

Update `~/.cursor/mcp_config.json`:

```json
{
  "mcpServers": {
    "atlassian": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "-e", "ATLASSIAN_CLOUD_ID=picarro.atlassian.net",
        "-e", "ATLASSIAN_EMAIL=your-email@picarro.com",
        "-e", "ATLASSIAN_API_TOKEN=your-token-here",
        "-e", "JIRA_DEFAULT_PROJECT=PH",
        "atlassian-mcp-server:latest"
      ]
    }
  }
}
```

### Option 2: Docker Compose Exec

If you want to use docker compose:

```json
{
  "mcpServers": {
    "atlassian": {
      "command": "docker",
      "args": [
        "compose",
        "-f", "/Users/ajain/pcp-repos/atlassian-mcp-server/docker-compose.yml",
        "run",
        "--rm",
        "atlassian-mcp-server"
      ]
    }
  }
}
```

## Docker Commands Cheat Sheet

```bash
# Build
docker build -t atlassian-mcp-server:latest .

# Build with no cache
docker build --no-cache -t atlassian-mcp-server:latest .

# Run interactively
docker run -it --rm atlassian-mcp-server:latest

# Run with env file
docker run -it --rm --env-file .env atlassian-mcp-server:latest

# Check running containers
docker ps

# View logs
docker logs atlassian-mcp-server

# Stop container
docker stop atlassian-mcp-server

# Remove container
docker rm atlassian-mcp-server

# Remove image
docker rmi atlassian-mcp-server:latest

# Inspect image
docker inspect atlassian-mcp-server:latest

# Check image size
docker images atlassian-mcp-server
```

## Docker Compose Commands

```bash
# Start services
docker compose up -d

# Stop services
docker compose down

# View logs
docker compose logs -f

# Restart service
docker compose restart

# Rebuild and restart
docker compose up -d --build

# Remove volumes
docker compose down -v
```

## Multi-Architecture Build

To build for multiple platforms (e.g., for deployment):

```bash
# Create builder
docker buildx create --name multiarch-builder --use

# Build for multiple platforms
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  -t yourusername/atlassian-mcp-server:latest \
  --push \
  .
```

## Pushing to Docker Hub

```bash
# Login to Docker Hub
docker login

# Tag image
docker tag atlassian-mcp-server:latest yourusername/atlassian-mcp-server:latest
docker tag atlassian-mcp-server:latest yourusername/atlassian-mcp-server:0.1.0

# Push
docker push yourusername/atlassian-mcp-server:latest
docker push yourusername/atlassian-mcp-server:0.1.0
```

## Troubleshooting

### Container Exits Immediately

Check logs:
```bash
docker logs atlassian-mcp-server
```

Common issues:
- Missing environment variables
- Invalid API token
- Network connectivity

### Can't Connect from Cursor

1. Verify container is running:
   ```bash
   docker ps | grep atlassian-mcp-server
   ```

2. Test manually:
   ```bash
   docker run -it --rm \
     --env-file .env \
     atlassian-mcp-server:latest
   ```

3. Check Cursor MCP config path:
   ```bash
   cat ~/.cursor/mcp_config.json
   ```

### Authentication Errors

Verify credentials:
```bash
docker run -it --rm \
  -e ATLASSIAN_CLOUD_ID="picarro.atlassian.net" \
  -e ATLASSIAN_EMAIL="your-email@picarro.com" \
  -e ATLASSIAN_API_TOKEN="your-token" \
  atlassian-mcp-server:latest
```

## Image Optimization

Current image size: ~150MB (Python 3.11 slim base)

Further optimizations:
- Use Alpine Linux (smaller base) - saves ~50MB
- Multi-stage build already implemented
- No dev dependencies in production image

## Security Best Practices

✅ No secrets in Dockerfile
✅ Environment variables for credentials
✅ Non-root user (Python slim defaults)
✅ Minimal base image
✅ .dockerignore to exclude sensitive files
✅ Multi-stage build reduces attack surface

## Resume/Portfolio Points

**Containerization Skills:**
- Multi-stage Docker builds for optimal image size
- Docker Compose orchestration
- Environment-based configuration
- Security best practices (no hardcoded secrets)
- Cross-platform builds (buildx)

**DevOps/Deployment:**
- Container-based microservice architecture
- Environment variable injection
- Resource limits and health checks
- Logging configuration
- Restart policies

---

**Next Steps:**
1. Build and test locally ✅
2. Push to Docker Hub
3. Deploy to production (optional)
4. Add to CI/CD pipeline (GitHub Actions)
