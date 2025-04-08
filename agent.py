from agent_types.mcp_client import MCPClinet
from agent_types.llm import LLM
from host import Host
import asyncio
import logging

#Configure logging
logging.basicConfig(
    level=logging.ERROR, format="%(asctime)s - %(levelname)s - %(message)s"
)


class Agent:
    def __init__(self, name:str="x"):
        self.name=name
        self.host = Host()

    async def chat_loop(self):
        try:
            while True:
                query = input("\nQuery: ").strip()
                if query in ["quit", "exit"]:
                        logging.info(f"\n{query} query exiting {self.name} agent...")
                        break
                await self.host.process(query=query)
        except Exception as ex:
            logging.error(f"\nError: {str(ex)}")
        finally:
            await self.host.cleanup()
        

async def main():
    #Create a new AI agent, default name "x"
    xagent = Agent()
    #Create a new MCP Client 
    #Edit your servers_config.json file with your MCP servers info before 
    #passing the servers_config_path to he MCPClinet.
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


if __name__ == "__main__":
    asyncio.run(main())
    
    



