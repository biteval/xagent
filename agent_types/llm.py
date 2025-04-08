import json
import httpx
import logging

#json keys or values used in the llm json request and response.
class LLMKeys:
    """
    For example this dict: 
    {"role": "assistant", "content": content}
    Would be:
    {LLMKeys.KEY_ROLE: LLMKeys.ASSISTANT, LLMKeys.KEY_CONTENT: content}

    """
    KEY_MESSAGE="message"
    KEY_MESSAGES="messages"
    KEY_CONTENT="content"
    KEY_TOOL_CALLS ="tool_calls"
    KEY_MODEL ="model"
    KEY_STREAM="stream"
    KEY_OPTIONS="options"
    KEY_NUM_CTX="num_ctx"
    KEY_TOOLS="tools"
    KEY_ROLE="role"
    USER="user" #value
    ASSISTANT ="assistant" #value
    SYSTEM="system" #value
    KEY_FUNCTION="function"
    KEY_MCP_SERVER="mcpServer"
    KEY_NAME="name"
    KEY_ARGUMENTS ="arguments"


class LLM:
    def __init__(self, name:str="ollama",url:str="http://localhost:11434/api/chat", access_token:str|None = None):
        self.name=name
        self.url=url
        self.access_token=access_token
    
    #send asynchronous streaming POST request to the llm and yield the llm json response by chunks 
    async def async_get_response(self, payload:json):
        headers = {
            "Content-Type": "application/json"
        }
        if self.access_token is not None:
            headers["Authorization"]=f"Bearer {self.access_token}"
        
        async with httpx.AsyncClient() as client:
            try:
                async with client.stream(method='POST', url=self.url, headers=headers, json=payload, timeout= httpx.Timeout(connect=10.0, read=30.0, write=10.0, pool=5.0)) as response:
                    async for chunk in response.aiter_lines():
                        if chunk:
                            try:
                                res = json.loads(chunk.encode(encoding="utf-8"))
                                yield res
                            except json.JSONDecodeError as ex:
                                logging.info(f"async_get_response error: {str(ex)}")
                                continue

            except httpx.RequestError as e:
                error_message = f"Error getting LLM response: {str(e)}"
                logging.info(error_message)

                if isinstance(e, httpx.HTTPStatusError):
                    status_code = e.response.status_code
                    logging.error(f"Status code: {status_code}")
                    logging.error(f"Response details: {e.response.text}")

                logging.info (
                    f"I encountered an error: {error_message}. "
                    "Please try again or rephrase your request."
                )
                 
