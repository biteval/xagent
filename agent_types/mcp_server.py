from mcp import ClientSession , StdioServerParameters
from agent_types.sse_server_params import SSEServerParameters
from typing import Optional
from contextlib import AsyncExitStack
from mcp.types import JSONRPCMessage
from anyio.streams.memory import MemoryObjectReceiveStream, MemoryObjectSendStream
import logging


class MCPServer:
    def __init__(self,name:str,params : Optional[StdioServerParameters| SSEServerParameters | None]):
        self.name=name
        self.params = params
        self.session : Optional[ClientSession|None] = None
        self.exit_stack = AsyncExitStack()
        self.stdio: MemoryObjectReceiveStream[JSONRPCMessage | Exception |None] = None
        self.write: MemoryObjectSendStream[JSONRPCMessage | None] = None
        
    async def is_stdio(self):
        return isinstance(self.params,StdioServerParameters)
    
    async def is_sse(self):
        return isinstance(self.params,SSEServerParameters)

    async def client_connect(self, client):
        """Init a session with the given MCP client (sse or stdio)."""
        stdio_transport = await self.exit_stack.enter_async_context(client)
        self.stdio, self.write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(ClientSession(self.stdio, self.write))
        await self.session.initialize()

 
    async def get_tools(self):
        """Return the availabe tools in this MCP server.
        """
        if not self.session:
            raise RuntimeError(f"Server {self.name} not initialized")
        # List available tools
        response = await self.session.list_tools()
        return response.tools


    async def excute_tool(self, tool_name, tool_args):
        try:
            print(f"[Calling tool {tool_name} with args {tool_args}]")
            result = await self.session.call_tool(tool_name, tool_args)
            return f"{tool_name} tool execution result: {result}"
        except Exception as ex:
            error_msg = f"Error executing {tool_name} tool: {str(ex)}"
            logging.error(error_msg)
            return error_msg
        

    async def cleanup(self):
        """Clean up resources"""
        await self.exit_stack.aclose()
