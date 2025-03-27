OpenAI 的 Function Calling 定义标准包括以下几个关键点：

1. **函数定义**：使用 JSON 格式定义函数，包括函数名、描述和参数。
2. **参数定义**：参数必须是 JSON Schema 格式，包含类型、描述等信息。
3. **调用机制**：模型在生成响应时，可以选择调用定义的函数，并传递相应的参数。

示例：

```python
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
                                "type": "string", # 是 string 而不是 str
                                "description": "加密货币Id 例如 BTC或ETH等",
                            }
                        },
                        "required": ["coin_id"],
                    },
                },
            }
        ]
```

模型在调用时会在 `response.choices[0].message.tool_calls` 产生数个 `ChatCompletionMessageToolCall` 对象

```python
# 一个简化的类
class ChatCompletionMessageToolCall:
  id: str # 函数调用id
  function.name: str
  function.arguments: str # 这是一个json str 例如 "{'name': '123'}" 需要json.loads序列化一下
```
