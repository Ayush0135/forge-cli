from typing import Any, Dict, Generator, List

from forge_cli.providers.base import BaseProvider
from forge_cli.tools.registry import execute_tool, get_tool_schemas


class Agent:
    def __init__(self, provider: BaseProvider):
        self.provider = provider
        self.tools = get_tool_schemas()

    def run(self, context: List[Dict[str, Any]]) -> str:
        """Run the agent loop with tool support."""
        max_steps = 10
        final_response = ""

        for step in range(max_steps):
            response = self.provider.chat(context, tools=self.tools)

            if isinstance(response, dict) and response.get("type") == "tool_call":
                tool_call = response
                context.append({"role": "assistant", "content": "", "tool_call": tool_call})

                # Execute tool
                result = execute_tool(tool_call["name"], tool_call.get("args", {}))

                # Feed observation back
                context.append(
                    {
                        "role": "tool",
                        "name": tool_call["name"],
                        "content": result,
                        "id": tool_call.get("id", "call_123"),
                    }
                )
            else:
                final_response = str(response)
                context.append({"role": "assistant", "content": final_response})
                break

        return final_response

    def stream_run(self, context: List[Dict[str, Any]]) -> Generator[str, None, None]:
        """Stream the agent run, executing tools automatically."""
        max_steps = 10

        for step in range(max_steps):
            is_tool_call = False
            tool_call = None
            final_text_chunks = []

            for chunk in self.provider.stream(context, tools=self.tools):
                if isinstance(chunk, dict) and chunk.get("type") == "tool_call":
                    is_tool_call = True
                    tool_call = chunk
                    break
                elif isinstance(chunk, str):
                    final_text_chunks.append(chunk)
                    yield chunk

            if not is_tool_call or not tool_call:
                # Append final textual response to context
                context.append({"role": "assistant", "content": "".join(final_text_chunks)})
                break

            yield f"\n[🔧 Executing tool: {tool_call['name']}(...)]\n"

            # Record the tool call intention
            context.append({"role": "assistant", "content": "".join(final_text_chunks), "tool_call": tool_call})

            # Execute the tool
            result = execute_tool(tool_call["name"], tool_call.get("args", {}))

            # Feed the observation back to the LLM
            context.append(
                {"role": "tool", "name": tool_call["name"], "content": result, "id": tool_call.get("id", "call_123")}
            )

            yield "[Observation received, generating response...]\n"
