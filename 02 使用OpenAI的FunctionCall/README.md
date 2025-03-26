OpenAI 的 Function Calling 定义标准包括以下几个关键点：

1. **函数定义**：使用 JSON 格式定义函数，包括函数名、描述和参数。
2. **参数定义**：参数必须是 JSON Schema 格式，包含类型、描述等信息。
3. **调用机制**：模型在生成响应时，可以选择调用定义的函数，并传递相应的参数。
4. **响应格式**：函数调用的响应会包含 `function_call` 字段，详细描述调用的函数和参数。

示例：

```json
{
  "name": "get_current_weather",
  "description": "Get the current weather in a given location",
  "parameters": {
    "location": {
      "type": "string",
      "description": "The city and state, e.g. San Francisco, CA"
    },
    "unit": {
      "type": "string",
      "enum": ["celsius", "fahrenheit"]
    }
  }
}
```

模型在调用时会生成类似以下格式的响应：

```json
{
  "function_call": {
    "name": "get_current_weather",
    "arguments": {
      "location": "Beijing",
      "unit": "celsius"
    }
  }
}
```