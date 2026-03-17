import os
import json
from openai import OpenAI


class AgentOutputItem:
    def __init__(self, type: str, content: str):
        self.type = type
        self.content = content

    @classmethod
    def model_validate_json(cls, data: str):
        parsed = json.loads(data)
        return cls(
            type=parsed.get("type"),
            content=parsed.get("content")
        )


class Agent:
    broker = None

    @classmethod
    def configure_broker(cls, broker):
        cls.broker = broker

    def __init__(
        self,
        name,
        model,
        tools,
        instructions,
        max_function_calls=10,
        **kwargs
    ):
        self.name = name
        self.model = model
        self.tools = tools
        self.instructions = instructions
        self.max_function_calls = max_function_calls

        self.message_history = []
        self.full_history = []

    def _get_tool_schema(self):
        return [tool._tool_metadata for tool in self.tools]

    def _execute_tool(self, tool_name, arguments):
        for tool in self.tools:
            if tool._tool_metadata["function"]["name"] == tool_name:
                return tool(**arguments)
        raise Exception(f"Tool {tool_name} not found")

    def promptAI(self, user_input: str):
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        messages = [
            {"role": "system", "content": self.instructions},
            {"role": "user", "content": user_input}
        ]

        response = client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=self._get_tool_schema(),
            tool_choice="auto"
        )

        msg = response.choices[0].message

        # Handle tool calls
        if msg.tool_calls:
            for call in msg.tool_calls:
                tool_name = call.function.name
                args = json.loads(call.function.arguments)

                print(f"[CALL] {tool_name} -> {args}")

                result = self._execute_tool(tool_name, args)

                print(f"[RESULT] {result}")

                output = {
                    "type": "function_call_result",
                    "content": str(result)
                }

                self.message_history.append(output)
                self.full_history.append(output)

                if Agent.broker:
                    Agent.broker.put_nowait(json.dumps(output))

            return "Function executed"

        # Normal response
        content = msg.content

        output = {
            "type": "text",
            "content": content
        }

        self.message_history.append(output)
        self.full_history.append(output)

        if Agent.broker:
            Agent.broker.put_nowait(json.dumps(output))

        return content