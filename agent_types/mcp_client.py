from agent_types.mcp_server import MCPServer , StdioServerParameters , \
SSEServerParameters
from typing import Dict
import json
from agent_types.config_keys import ServersConfKeys as JSONKeys
from mcp.client.sse import sse_client
from mcp.client.stdio import stdio_client


class MCPClinet:
    def __init__(self,name:str,servers_config_path:str):
        self.name=name
        self.servers_config_path=servers_config_path
        self.servers : Dict[str, MCPServer] = {}
        
    
    async def init(self):
        """Initilize the client by loading all servers to self.servers dict 
        and connect to each one, after this prints the wellcome msg."""
        await self._collect_servers()
        await self.connect_to_servers()
        await self.print_wellcome_msg()
    
    async def get_mcp_server_name(self,tool_name:str):
        """Linear search to find a MCP server have a tool_name 
        and returns its name or None if no servers found."""
        for server_name , server in self.servers.items():
            if any(tool_name == tool.name for tool in await server.get_tools()):
              return server_name
        return None
    

    async def is_my_mcp_server(self, server_name:str)->str|None:
        """Check if the server_name belongs to this mcp client.
        """
        #Constant check if the MCP server is belongs to this MCP client by its name as a dict key.
        return not self.servers.get(server_name,None)==None



    async def _collect_servers(self):
        """
        Open servers_config.json file  and loads all servers to self.servers dict.
        """
        with open(self.servers_config_path, "r") as f:
            servers_config = json.load(f)
            #loop through all servers names and attributes in servers_config.json file.
            for name , attrs in servers_config[JSONKeys.KEY_MCP_SERVERS].items():
                #get connection data.
                connection = attrs[JSONKeys.KEY_CONNECTION]
                #create sse server.
                if connection[JSONKeys.KEY_TYPE]==JSONKeys.KEY_SSE:
                    end_point = connection[JSONKeys.KEY_END_POINT] # get the sse endpoint.
                    #create a new MCP server with SSE parameters.
                    curr_server = MCPServer(name=name, params=SSEServerParameters(end_point=end_point))
                    self.servers[name] = curr_server
                #create stdio server
                elif connection[JSONKeys.KEY_TYPE]==JSONKeys.KEY_STDIO:
                    cmd=connection[JSONKeys.KEY_COMMAND] #get stdio command.
                    curr_args = [arg for arg in connection[JSONKeys.KEY_ARGS]] #get stdio args.
                    #create a new MCP server with stdio parameters.
                    curr_server = MCPServer(name=name, params=StdioServerParameters(command=cmd, args=curr_args))
                    self.servers[name] = curr_server
    
    async def connect_to_servers(self):
        """Connect to all collected MCP servers from servers_config.json
        """
        for _ , server in self.servers.items():
            if await server.is_stdio():
                await server.client_connect(stdio_client(server=server.params))
            elif await server.is_sse():
                await server.client_connect(sse_client(url=server.params.end_point))


    async def print_wellcome_msg(self):
        """Print earch server name with its tools names.
        """
        for server_name, server in self.servers.items():
            server_tools = await server.get_tools()
            print(f"Connected to {server_name} server with tools:",[tool.name for tool in server_tools])


    async def excute_tool(self, server_name:str, tool_name:str, tool_args:Dict[str,str]):
            """Excute a tool provided by a spesific server."""
            #get the server that provides the tool by its name.
            server = self.servers.get(str(server_name),None)
            if server is not None:
                call_resutl = await server.excute_tool(tool_name,tool_args)
                return call_resutl
            return f"There is no server with name {server_name}"
    

    async def collect_all_tools_schema(self):
        """Get all the tools schema provided by all connected mcp servers.
        """
        available_tools=[]
        for server_name, server in self.servers.items():
            curr_server_tools = await server.get_tools()
            for tool in curr_server_tools:
                curr_tool={}
                """
                The llm should be informed by a system message to include the "mcpServer" key
                in any tool_call response, this allows us to efficiently get the server from the self.servers
                dictionary by its name, and execute the tool.
                """ 
                #Specify the name of the MCP server that provides this tool.
                curr_tool["mcpServer"]=server_name
                curr_tool["type"]="function"
                curr_tool["function"]={
                    "name": tool.name,
                    "description": tool.description,
                }
                curr_tool["parameters"]=tool.inputSchema
                available_tools.append(curr_tool)
        return available_tools

    
    async def cleanup(self):
        """Clean up resources"""
        for _ , server in self.servers.items():
            await server.cleanup()