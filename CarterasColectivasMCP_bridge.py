"""
MCP Bridge Server - Connects Claude Desktop to Lambda API
This server runs locally and forwards all MCP requests to the Lambda API
"""
import asyncio
import json
import sys
import os
import logging
from typing import Any
from pathlib import Path
import requests
from mcp.server import Server
from mcp.types import Resource, Tool, TextContent
import mcp.server.stdio

# Bridge version
BRIDGE_VERSION = "1.3.0"
BRIDGE_TYPE = os.getenv("BRIDGE_TYPE", "client")  # "client" or "internal"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    stream=sys.stderr,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("lambda-api-bridge")

# Lambda API configuration
API_URL = os.getenv("MCP_API_URL", "https://agents.carterascolectivas.co/mcp")

# API Key loading (supports multiple methods for flexibility)
def load_api_key():
    """
    Load API key from multiple sources (in priority order):
    1. Environment variable: API_KEY
    2. Config file from environment variable: BRIDGE_CONFIG
    3. Config file in same directory: bridge_config.json
    4. Hardcoded in this file (line below)
    """
    # Method 1: Direct environment variable
    api_key = os.getenv("API_KEY")
    if api_key:
        logger.info("API key loaded from API_KEY environment variable")
        return api_key

    # Method 2: Config file from environment variable
    config_path_env = os.getenv("BRIDGE_CONFIG")
    if config_path_env and os.path.exists(config_path_env):
        try:
            with open(config_path_env, 'r') as f:
                config = json.load(f)
                api_key = config.get("api_key")
                if api_key:
                    logger.info(f"API key loaded from config file: {config_path_env}")
                    return api_key
        except Exception as e:
            logger.warning(f"Failed to load config from {config_path_env}: {e}")

    # Method 3: Config file in same directory as script/executable
    if getattr(sys, 'frozen', False):
        # Running as executable
        script_dir = Path(sys.executable).parent
    else:
        # Running as script
        script_dir = Path(__file__).parent

    config_path = script_dir / "bridge_config.json"
    if config_path.exists():
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
                api_key = config.get("api_key")
                if api_key:
                    logger.info(f"API key loaded from config file: {config_path}")
                    return api_key
        except Exception as e:
            logger.warning(f"Failed to load config from {config_path}: {e}")

    # Method 4: Hardcoded value (for Python script users who edit the file)
    # SECURITY: Never commit real API keys! Use placeholder only.
    hardcoded_key = "your-api-key-here"
    if hardcoded_key and hardcoded_key != "your-api-key-here":
        logger.info("API key loaded from hardcoded value in script")
        return hardcoded_key

    # No API key found
    logger.error("No API key configured! Please set API_KEY environment variable or create bridge_config.json")
    return None

API_KEY = load_api_key()

class LambdaAPIBridge:
    """MCP Server that bridges to Lambda API"""
    
    def __init__(self):
        self.server = Server("lambda-api-bridge")
        self._setup_handlers()
        logger.info(f"Lambda API Bridge v{BRIDGE_VERSION} ({BRIDGE_TYPE}) initialized")
    
    def _call_lambda_api(self, method: str, params: dict = None) -> dict:
        """Call the Lambda API with MCP protocol"""
        request_data = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": method,
            "params": params or {}
        }
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {API_KEY}"
        }
        
        try:
            logger.info(f"Calling Lambda API: {method}")
            response = requests.post(API_URL, json=request_data, headers=headers, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            logger.info(f"Lambda API response received: {response.status_code}")
            return result
            
        except requests.exceptions.Timeout:
            logger.error("Lambda API request timed out")
            return {
                "jsonrpc": "2.0",
                "id": 1,
                "error": {
                    "code": -32000,
                    "message": "Request timed out"
                }
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"Lambda API request failed: {e}")
            return {
                "jsonrpc": "2.0",
                "id": 1,
                "error": {
                    "code": -32603,
                    "message": f"API request failed: {str(e)}"
                }
            }
    
    def _setup_handlers(self):
        """Setup MCP protocol handlers"""
        # Note: Only implementing tools, not resources, since Lambda API doesn't support resources/list
        
        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            """List available tools from Lambda API"""
            try:
                result = self._call_lambda_api("tools/list")
                
                if "error" in result:
                    logger.error(f"Error listing tools: {result['error']}")
                    return []
                
                tools_data = result.get("result", {}).get("tools", [])
                
                # Convert to MCP Tool objects
                tools = []
                for tool in tools_data:
                    tools.append(Tool(
                        name=tool.get("name", ""),
                        description=tool.get("description", ""),
                        inputSchema=tool.get("inputSchema", {})
                    ))
                
                logger.info(f"Listed {len(tools)} tools")
                return tools
            except Exception as e:
                logger.error(f"Exception in list_tools: {e}")
                import traceback
                traceback.print_exc(file=sys.stderr)
                return []
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: Any) -> list[TextContent]:
            """Execute a tool via Lambda API"""
            try:
                logger.info(f"Calling tool: {name}")
                
                result = self._call_lambda_api("tools/call", {
                    "name": name,
                    "arguments": arguments
                })
                
                if "error" in result:
                    error_msg = result["error"].get("message", "Unknown error")
                    logger.error(f"Tool execution error: {error_msg}")
                    return [TextContent(
                        type="text",
                        text=json.dumps({
                            "error": error_msg,
                            "code": result["error"].get("code", -32603)
                        }, indent=2)
                    )]
                
                # Extract the text content from the result
                content = result.get("result", {}).get("content", [])
                
                if content and len(content) > 0:
                    text_content = content[0].get("text", "{}")
                    logger.info(f"Tool executed successfully")
                    return [TextContent(
                        type="text",
                        text=text_content
                    )]
                else:
                    logger.warning("No content in tool response")
                    return [TextContent(
                        type="text",
                        text=json.dumps({"message": "No content returned"}, indent=2)
                    )]
            except Exception as e:
                logger.error(f"Exception in call_tool: {e}")
                import traceback
                traceback.print_exc(file=sys.stderr)
                return [TextContent(
                    type="text",
                    text=json.dumps({"error": str(e)}, indent=2)
                )]
    
    async def run(self):
        """Run the MCP server"""
        logger.info(f"Starting Lambda API Bridge v{BRIDGE_VERSION} ({BRIDGE_TYPE})...")

        try:
            async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
                logger.info(f"Bridge v{BRIDGE_VERSION} connected to stdio")
                await self.server.run(
                    read_stream,
                    write_stream,
                    self.server.create_initialization_options()
                )
        except Exception as e:
            logger.error(f"Server error: {e}")
            raise

async def main():
    """Main entry point"""
    try:
        bridge = LambdaAPIBridge()
        await bridge.run()
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        import traceback
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())