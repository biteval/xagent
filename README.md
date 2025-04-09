# XAgent

XAgent is an AI Agent library simplifies the creation of single or multi AI agents with multi LLMs based on Anthropic's MCP protocol, aims to provide free and open source AI agent that can handle complex online tasks to all people around the world, adding value to their lives.
<a href="https://youtu.be/83VpJnFdBkI" target="_blank">Watch this video to learn how to create AI agents from scratch using XAgent lib</a>

# Architecture

<p align="center">
  <img src="https://github.com/biteval/xagent/blob/main/static/xagent-architect.jpeg" alt="XAgent Architecture">
</p>


# Componenets 

The agent_types module contains this basic components:

## llm

1. The llm component provides this classes:

1. LLM class provides async_get_response method to asynchronously send streaming requests to the LLM endpoint using httpx.AsyncClient(), yielding each response chunk as it is received.

2. LLMKeys class stores the keys used in the LLM request and response json object to avoid hard writing this keys each time we need to read or write a value to the json object.

## mcp_client

The mcp_client component providess a class MCPClinet with this main responsibilities:

1. Reading the MCP servers informations from the given servers_config.json file and connect to each MCP server.

2. Maintain a dict of MCP server name to MCP server instance for quick access to any MCP server by its name.

3. Collect all the tools schemas provided by each MCP server and mark each tool with owner MCP server name with key "mcpServer" for easy access to the desired MCP server later when tool calling is needed.

4. Execute a tool and return the call result by forwarding the tool call query to the desired MCP server by its name.


the ServersConfKeys class defines keys used in the servers_config.json file.

## mcp_server

first, let's discover two small classes:

1. StdioServerParameters:  given by Anthropic MCP protocol defines the main parameters for stdio communication like command and args etc

2. SSEServerParameters: provided by XAgent defines the SSE end_point parameter needed by a MCP client to connect to MCP server.


The mcp_server component provides a class MCPServer as a unified type for stdio and SSE MCP servers, the given StdioServerParameters or  SSEServerParameters in the constructor determins the type of the MCP server.

The MCPServer class is responsible for:

1. Maintains a session between the MCP server and the given MCP client 

2. Return the available tools in this MCP server

3. Execute a tool given tool name and args


# host 

The host component provides a class named Host that manages multiple MCP clients (connected to mltiple MCP servers) , and multiple LLMs.

responsibilities:

1. maintains a dict for MCP clients for quick access to any MCP client by its name

2. maintains a dict for LLMs for quick access to any LLM by its name, and a selected_llm variable for the current selected LLM

3. maintains a conversation history with the selected LLM which is the json object used to send and recieve responses from the LLM

4. Provided a method get_all_tools_schema to collect all available tools from the MCP clients (the tools collected by each MCP client from all its MCP servers) in order to send this schema to the LLM within the json object

5. Provides a method get_ollama_payload to create a basic json object with the default model "llama3.2:latest" and collected tools shemas from all the MCP clients, this json object is ready to send it to the LLM after adding a user input to it, the LLM instance will perform the query using async_get_response and the Host object recieves respose chunks.


6. Provides excute_tool method to forward any tool call response from the LLM to the MCP client that have the MCP server owns the specified tool


7. Process LLM response if it a text response display it in the chat, or in case of tool call response it forward it to a process_tool_call_response method to process the tool call response by sending it back to the LLM and recieves its response.


# agent

The agent component provides a class Agent that keeps one Host instance as a member and maintains a chat loop by reading user input in a loop and sent the input back to the Host instance for processing.

This is an example of setting up a new AI agent using XAgent library:

# Example usage

```
async def main():
    #Create a new AI agent, default name "x"
    xagent = Agent()
    #Create a new MCP Client 
    def_mcp_client = MCPClinet(name="default", servers_config_path="./servers_config.json")
    #Initialize the MCP CLient
    await def_mcp_client.init()
    #Add the MCP client to the host
    xagent.host.add_client(def_mcp_client)
    #Create a new LLM default to ollama llama3.2:latest model and endpoint http://localhost:11434/api/chat
    def_llm = LLM()
    #Add the llm to the host
    xagent.host.add_llm(def_llm)
    #Start the chat loop
    await xagent.chat_loop()
```

# Install

## Set up your environment

First, install uv and set up our Python project and environment:

## Linux

```
curl -LsSf https://astral.sh/uv/install.sh | sh
```
## Windows

```
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Now, let’s clone the XAgent repo:

```
git clone https://github.com/biteval/xagent.git
```

Move to the project folder:

```
cd xagent
```

Init, create virtual environment and activate it :

```
uv init
```

```
uv venv
```


## Linux

```
source .venv/bin/activate
```

## Windows

```
.venv\Scripts\activate
```

# Install dependencies

## Linux

```
uv add "mcp[cli]" httpx python-dotenv
```

## Windows 

```
uv add mcp[cli] httpx python-dotenv
```

## Start the AI Agent

Now, you can run your first AI agent using this command after modify servers_config.json file with your MCP servers details:

```
python agent.py
```

# Overview 

- The servers_config.json file defines the available MCP stdio or SSE servers, allowing the MCP client to identify and connect to them accordingly. for example:

```

{
    "mcpServers": {

      "Browser CTL": {
        "connection":{
         "type":"sse",
         "end_point":"http://127.0.0.1:8001/sse"
        }
      },

      "Email Reader": {
        "connection":{
        "type":"stdio",
        "command": "python",
        "args": ["./stdio_servers/examples/email_reader.py"]
      }
    }

    }
}

```

- In the example above the first element is a SSE MCP server with name: "Browser CTL" and endpoint http://127.0.0.1:8001/sse

- The second element is a stdio MCP server with name "Email Reader" and can be launched using command python and path ./stdio_servers/examples/email_reader.py with no args.

- Using this information described in servers_config.json file the MCP client can connect to SSE or stdio MCP servers.

-  Each MCP client connects to all the specified MCP servers in servers_config.json and keep a dict of these connected MCP servers with the name of each server as a key, this allows access to a specific MCP server by its name directly, also tagging each tool with the MCP server name makes tools calling more efficient when the client have multiple MCP servers.


-  When the MCP client collects tools from each MCP server it adds "mcpServer" key to each tool schema, and the LLM must be informed using a system message to replay back with the same "mcpServer" value for each tool call response, so the MCP client can know which MCP server owns the tool and get it from the dict in constant time, if the LLM do not responde back with the MCP server name in a tool call response the MCP client will search for the MCP server in linear time to excute the tool.


- The Host instance can have many MCP clients and LLMs so it keeps a dict to access each MCP client by its name and another dict for LLMs, also a selected_llm variable so only the current selected LLM used, while the user can switch between them, the host also stores and update the conversation history with user and assistant messages, the updated history is sent to the LLM in each request.

- The Agent object keeps one Host instance and maintains a chat loop passing the user input to the host for processing.


# Contributing

Your contribution is crucial to our mission. If you're unable to contribute directly, you can still make a significant impact by sharing this project within your community. 

For more insights and updates, explore our YouTube channel:

<a href="https://www.youtube.com/@BitEval" target="_blank">
  <img src="https://github.com/biteval/browser_ctl/blob/main/static/biteval_logo.jpeg" alt="BitEval">
</a>












