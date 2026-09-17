#!/usr/bin/env python3
"""Test MCP server integration by simulating client initialization."""

import asyncio
import json
import subprocess
import sys
from pathlib import Path

async def test_mcp_server():
    """Test MCP server responds to initialize request."""
    print("🧪 Testing MCP Server Integration\n")
    
    # Start the MCP server
    server_path = Path(__file__).parent / "src"
    env = {"PYTHONPATH": str(server_path)}
    
    process = await asyncio.create_subprocess_exec(
        sys.executable, "-m", "atlassian_mcp_server",
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env
    )
    
    # Send initialize request
    init_request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {
                "name": "test-client",
                "version": "1.0.0"
            }
        }
    }
    
    print(f"📤 Sending initialize request...")
    request_json = json.dumps(init_request) + "\n"
    process.stdin.write(request_json.encode())
    await process.stdin.drain()
    
    # Read response with timeout
    try:
        response_line = await asyncio.wait_for(
            process.stdout.readline(),
            timeout=5.0
        )
        
        if response_line:
            response = json.loads(response_line.decode())
            print(f"📥 Received response\n")
            
            if "result" in response:
                print("✅ Server initialized successfully!")
                print(f"   Server: {response['result'].get('serverInfo', {}).get('name', 'unknown')}")
                print(f"   Protocol: {response['result'].get('protocolVersion', 'unknown')}")
                
                # List tools
                list_tools_request = {
                    "jsonrpc": "2.0",
                    "id": 2,
                    "method": "tools/list",
                    "params": {}
                }
                
                print(f"\n📤 Requesting tools list...")
                request_json = json.dumps(list_tools_request) + "\n"
                process.stdin.write(request_json.encode())
                await process.stdin.drain()
                
                response_line = await asyncio.wait_for(
                    process.stdout.readline(),
                    timeout=5.0
                )
                
                if response_line:
                    response = json.loads(response_line.decode())
                    if "result" in response and "tools" in response["result"]:
                        tools = response["result"]["tools"]
                        print(f"✅ Found {len(tools)} tools:\n")
                        for tool in tools:
                            print(f"   • {tool['name']}: {tool.get('description', 'No description')[:60]}...")
                        
                        print(f"\n🎉 MCP Server is fully operational!")
                        return True
            else:
                print(f"❌ Error in response: {response.get('error', 'Unknown error')}")
                return False
        else:
            print("❌ No response received from server")
            return False
            
    except asyncio.TimeoutError:
        print("❌ Timeout waiting for server response")
        stderr = await process.stderr.read()
        if stderr:
            print(f"\nServer stderr:\n{stderr.decode()}")
        return False
    finally:
        process.terminate()
        await process.wait()

if __name__ == "__main__":
    result = asyncio.run(test_mcp_server())
    sys.exit(0 if result else 1)
