import json
import random
from typing import Callable

from openai import OpenAI
from openai.types.chat import ChatCompletionMessageToolCall

import config
from coinapi import coin_current_rates

class CoinAgent:
    def __init__(self, tools=[], tools_fn: list[Callable] = []):
        self.client = OpenAI(
            api_key=config.OPENAI_API_KEY, base_url=config.OPENAI_BASE_URL
        )
        self.tools: list[dict] = tools

        self.tools_map: dict[str, Callable] = {
            tool_fn.__name__: tool_fn for tool_fn in tools_fn
        }

        self.welcome = "我是一个关于加密货币的智能助理，请尽管问我！"
        self.messages = []
        self.clear()

    def send_message(self, messages):
        if self.tools:
            response = self.client.chat.completions.create(
                messages=messages,
                model=config.MODEL,
                tools=self.tools,
                tool_choice="auto",
            )

        else:
            response = self.client.chat.completions.create(
                messages=messages,
                model=config.MODEL,
            )

        return response

    def clear(self):
        self.messages = [
            {
                "role": "system",
                "content": "你是一个加密货币专家，为用户提供专业的加密货币领域建议",
            }
        ]

    def invoke(self, query: str, max_step=10):
            
        self.messages.append({"role": "user", "content": query})

        while max_step > 0:
            max_step -= 1

            response = self.send_message(self.messages)
            self.messages.append(response.choices[0].message)

            # 是否有function call调用
            tool_calls: list[ChatCompletionMessageToolCall] = getattr(
                response.choices[0].message, "tool_calls", False
            )

            if tool_calls:
                tool_calls_message = response.choices[0].message.content
                print(f"[AI] {tool_calls_message}")
                for tool_call in tool_calls:
                    print(f"[Request ToolCall] Agent 请求执行：{tool_call.function.name}")
                    user_auth = input("是否同意执行(Y/N)")
                    if user_auth.lower() == "n":
                        self.messages.append(
                            {
                                "role": "tool",
                                "content": "User blocked tool execution",
                                "tool_call_id": tool_call.id,
                            }
                        )
                        continue

                    fn_kwargs = json.loads(tool_call.function.arguments)
                    fn = self.tools_map.get(tool_call.function.name)
                    print(
                        f"[ToolCall][{tool_call.function.name}][{tool_call.id}] Execution..."
                    )
                    tool_response = fn(**fn_kwargs)

                    print(
                        f"[ToolCall][{tool_call.function.name}][{tool_call.id}] Finish response:",
                        tool_response,
                    )
                    # 添加tool调用结果
                    self.messages.append(
                        {
                            "role": "tool",
                            "content": str(tool_response),
                            "tool_call_id": tool_call.id,
                        }
                    )
            else:
                return response.choices[0].message.content


def main():

    agent = CoinAgent(
        tools=[
            {
                "type": "function",
                "function": {
                    "name": coin_current_rates.__name__,
                    "description": "获取指定加密货币对比美元的汇率",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "coin_id": {
                                "type": "string",
                                "description": "加密货币Id 例如 BTC或ETH等",
                            }
                        },
                        "required": ["coin_id"],
                    },
                },
            }
        ],
        tools_fn=[coin_current_rates],
    )

    print(agent.welcome)
    while True:
        query = input(">>>")
        if query == ".exit":
            print("Bye.")
            return
        answer = agent.invoke(query)
        print("[AI]", answer)


if __name__ == "__main__":
    main()
