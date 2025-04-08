
class SSEServerParameters:
    """SSE server parameters contains only
    the endpoint so the client can conenct to it.
    Example:
    http://127.0.0.1:8000/sse
    """
    def __init__(self,end_point:str):
        self.end_point=end_point