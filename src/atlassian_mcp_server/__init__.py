"""Atlassian MCP Server - Main entry point."""

from .server import main

__version__ = "0.1.0"
__all__ = ["main"]

if __name__ == "__main__":
    main()
