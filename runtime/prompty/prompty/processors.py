from .tracer import Trace
from openai import Stream
from typing import Iterator
from pydantic import BaseModel
from openai.types.completion import Completion
from .core import Invoker, InvokerFactory, Prompty
from openai.types.chat.chat_completion import ChatCompletion
from openai.types.create_embedding_response import CreateEmbeddingResponse


class ToolCall(BaseModel):
    id: str
    name: str
    arguments: str


@InvokerFactory.register_processor("openai")
@InvokerFactory.register_processor("azure")
@InvokerFactory.register_processor("azure_openai")
class OpenAIProcessor(Invoker):
    """OpenAI/Azure Processor"""

    def __init__(self, prompty: Prompty) -> None:
        super().__init__(prompty)

    def invoke(self, data: any) -> any:
        """Invoke the OpenAI/Azure API

        Parameters
        ----------
        data : any
            The data to send to the OpenAI/Azure API

        Returns
        -------
        any
            The response from the OpenAI/Azure API
        """
        if isinstance(data, ChatCompletion):
            response = data.choices[0].message
            # tool calls available in response
            if response.tool_calls:
                return [
                    ToolCall(
                        id=tool_call.id,
                        name=tool_call.function.name,
                        arguments=tool_call.function.arguments,
                    )
                    for tool_call in response.tool_calls
                ]
            else:
                return response.content

        elif isinstance(data, Completion):
            return data.choices[0].text
        elif isinstance(data, CreateEmbeddingResponse):
            if len(data.data) == 0:
                raise ValueError("Invalid data")
            elif len(data.data) == 1:
                return data.data[0].embedding
            else:
                return [item.embedding for item in data.data]
        elif isinstance(data, Iterator):

            def generator():
                for chunk in data:
                    if len(chunk.choices) == 1 and chunk.choices[0].delta.content != None:
                        content = chunk.choices[0].delta.content
                        Trace.add("stream", content)
                        yield content

            return generator()
        else:
            return data
