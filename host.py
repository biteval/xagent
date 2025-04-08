from typing import Dict
from agent_types.mcp_client import MCPClinet
from agent_types.llm import LLM , LLMKeys
import logging

class Host:
    def __init__(self):
        self.clients : Dict[str, MCPClinet] = {}
        self.llms :  Dict[str, LLM] = {}
        self.selected_llm :str|None = None
        self.history=None
    
    
    def get_available_llms(self):
        """Return the availabe llm names"""
        llm_names=[]
        for llm_name in self.llms:
            llm_names.append(llm_name)
        return llm_names
    

    def add_client(self,client:MCPClinet):
        self.clients[client.name]=client

    def select_llm(self, llm_name:str):
        """Select a llm to send requsts to it."""
        self.selected_llm = llm_name

    def add_llm(self, llm:LLM):
        #select the first added llm as default
        if self.selected_llm==None:
            self.select_llm(llm.name)
        self.llms[llm.name]=llm

    
    async def get_all_tools_schema(self):
        """Gather all clients collected tools schema"""
        available_tools=[]
        for _, client in self.clients.items():
            client_collected_tools = await client.collect_all_tools_schema()
            available_tools.extend(client_collected_tools)
        return available_tools


    async def get_ollama_payload(self,query:str, model:str="llama3.2:latest"):
        """Get the llm json payload."""
        llm_payload = {}
        llm_payload[LLMKeys.KEY_MODEL]= model 
        llm_payload[LLMKeys.KEY_STREAM]= True
        llm_payload[LLMKeys.KEY_OPTIONS]={
         LLMKeys.KEY_NUM_CTX: 8192
        }
        llm_payload[LLMKeys.KEY_TOOLS]= await self.get_all_tools_schema()
        #add user / system messages to the payload.
        messages=[]

        json_schema = """{
        "model":      "string",
        "created_at": "string",          // RFC3339 timestamp
        "message": {
            "role":       "assistant",
            "content":    "string",        // your natural reply text
            "tool_calls": [
            {
                "function": {
                "name":      "string",   // tool name
                "arguments": {}         // argument map
                }
            }
            // … more calls, if needed
            ]
        },
        "done": false
        }"""

        system_message = (
                "You are a helpful assistant with access to tools.\n\n"   
                "Choose the appropriate tool based on the user's question. "
                "If no tool is needed, reply directly.\n\n"
                'If you cannot answer reply with a natural text asking for more information."\n\n'
                "IMPORTANT: For every user query, you must ONLY respond with "
                "the exact JSON object format below, nothing else:\n"
                f"{json_schema}" 
                "After receiving a tool's response:\n"
                "1. Transform the raw data into a natural, conversational response \n"
                "2. Keep responses concise, natural and informative\n"
                "3. Focus on the most relevant information\n"
                "4. Use appropriate context from the user's question\n"
                "5. Avoid simply repeating the raw data\n\n"
                "Please use only the tools that are explicitly defined in the chat request with key 'tools'."
            )
            
        messages.append({LLMKeys.KEY_ROLE: LLMKeys.SYSTEM, LLMKeys.KEY_CONTENT: system_message})
        messages.append({LLMKeys.KEY_ROLE : LLMKeys.USER, LLMKeys.KEY_CONTENT : query})
        llm_payload[LLMKeys.KEY_MESSAGES]=messages
        return llm_payload
    

    async def excute_tool(self,server_name:str, tool_name:str, tool_args):
        for _, client in self.clients.items():
            if server_name is None:
                """The server_name is not provided as a string, this occurs when the llm do not provide
                'mcpServer' key with the tool call response."""
                #linear search to get a MCP server name with tool_name, returns None if not available.
                server_name = await client.get_mcp_server_name(tool_name)

            if await client.is_my_mcp_server(server_name):
                call_result = await client.excute_tool(server_name=server_name, tool_name=tool_name, tool_args=tool_args)
                return call_result
        return f"No mcp server {server_name} with tool {tool_name}"

   
    async def process_tool_call_response(self, response):
        messages = self.history[LLMKeys.KEY_MESSAGES]
        for tool_call in response:
            tool_call_fn = tool_call.get(LLMKeys.KEY_FUNCTION, {})
            #add the function call request to assistant message for llm
            messages.append({LLMKeys.KEY_ROLE: LLMKeys.ASSISTANT, LLMKeys.KEY_CONTENT: str(response)})
            #update the messages list
            self.history[LLMKeys.KEY_MESSAGES]=messages
            """The llm must add 'mcpServer' key to the tool call response in order to the client
            to know which mcpserver have the tool in constant time, if it not provided the client will do a linear search for the MCP server.
            """
            server_name = tool_call_fn.get(LLMKeys.KEY_MCP_SERVER, None)
            #print(f"server name from llm response {server_name}")
            #get the tool name and args from the tool call response.
            tool_name=tool_call_fn[LLMKeys.KEY_NAME]
            tool_args=tool_call_fn[LLMKeys.KEY_ARGUMENTS]
            #excute the tool, this will not work if the llm donot provide the 'mcpServer' key
            call_result = await self.excute_tool(server_name,tool_name,tool_args)
            print(f"***call_result = {call_result}")
            #add the fucntion call result to as a system message for llm
            messages.append({LLMKeys.KEY_ROLE: LLMKeys.ASSISTANT, LLMKeys.KEY_CONTENT: str(call_result)})
            #update the messages list
            self.history[LLMKeys.KEY_MESSAGES]=messages
            #print(f"call_result:{call_result}")
            await self.process_llm_response()
            


    async def process_response(self,response):
        #print(f"response:\n{response}")
        messages = self.history[LLMKeys.KEY_MESSAGES]
        content = response.get(LLMKeys.KEY_MESSAGE, {}).get(LLMKeys.KEY_CONTENT)
        if content is not None:
            #TODO : some ollama models include tool calls responses 
            # in the content value you may check if content value is tool calls response
            if isinstance(content, str):
                print(content)
                #update the messages
                messages.append({LLMKeys.KEY_ROLE: LLMKeys.ASSISTANT, LLMKeys.KEY_CONTENT: content})
                self.history[LLMKeys.KEY_MESSAGES]=messages
            else:
                logging.info(f"{content} is not a string, content type: {type(content)}")

        #Check for tool calls in the response
        tool_calls =  response.get(LLMKeys.KEY_MESSAGE, {}).get(LLMKeys.KEY_TOOL_CALLS)
        if tool_calls is not None:
            await self.process_tool_call_response(tool_calls)

    async def process_llm_response(self):
        """Send the self.history to the current selected llm
        and process the response"""
        async for response in self.llms[self.selected_llm].async_get_response(payload=self.history):
            print("RESPONSE", response)
            await self.process_response(response=response)

    async def process(self, query:str):
        #init the llm json payload and save it as self.history
        self.history = await self.get_ollama_payload(query=query)
        await self.process_llm_response()
        
        
    async def cleanup(self):
        """Cleanup resources"""
        for _, client in  self.clients.items():
            await client.cleanup()


