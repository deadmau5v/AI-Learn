import json
import random
import re

from openai import OpenAI

from Prompts import ReActPrompt
import config


class CoinAgent:
    def __init__(self):
        self.tools = [
            {
                "name": "list_all_cryptocurrency",
                "description": "使用该工具获取所有支持的加密货币币种",
                "parameters": {},
            },
            {
                "name": "get_cryptocurrency_price",
                "description": "使用该工具获取指定币种的价值",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "coin_name": {"type": "string", "description": "币种名称"}
                    },
                },
            },
        ]
        
        self.tool_functions = [
            CoinAgent.get_cryptocurrency_price,
            CoinAgent.list_all_cryptocurrency
        ]
        self.tools_map = {fn.__name__: fn for fn in self.tool_functions}

        self.client = OpenAI(
            api_key=config.OPENAI_API_KEY, base_url=config.OPENAI_BASE_URL
        )
        self.ReAct_PROMPT = ReActPrompt

    def invoke(self, query: str) -> str:
        """调用该AI Agent

        Args:
            prompt (str): 提示词

        Returns:
            str: AI思考最终结果
        """

        prompt = self.ReAct_PROMPT.format(
            instructions="你是一个虚拟货币助手,可以回答关于虚拟货币相关的问题",
            input=query,
            tools=self.tools,
            tool_names=self.get_tool_names(),
        )

        messages = [{"role": "user", "content": prompt}]

        while True:
            response = self.send_messages(messages)
            response_text = response.choices[0].message.content

            # print("大模型回复:\n", response_text)
            is_tool_calling, tool_name, tool_input = CoinAgent.parseToolCall(
                response_text
            )
            # print("[DEBUG]:", response_text,is_tool_calling, tool_name, tool_input, sep=f"\n{"=" * 20}\n")
            if is_tool_calling:
                call_fn = self.tools_map[tool_name]
                if not call_fn:
                    raise "执行函数错误"
                print("[Tool]", tool_name, "...")
                tool_response = call_fn(**tool_input)
                messages.append({"role": "user", "content": f"Observation:{tool_response}"})
                # print("[DEBUG]", "Function Call Response:", tool_response)
                
            finish, answer = CoinAgent.parseFinalAnswer(response_text)
            if finish:
                print(answer)
                break

    def send_messages(self, messages):
        return self.client.chat.completions.create(
            model=config.MODULE, messages=messages
        )

    @staticmethod
    def parseFinalAnswer(ai_res: str) -> tuple[bool, str]:
        """解析ai最终返回结果

        Args:
            ai_res (str): AI回复的原始回复

        Returns:
            tuple: 包含以下元素的元组:
                - bool: 是否存在最终答案.
                - str:  最终答案内容.
        """
        try:
            final_anwer = re.search(r"Final Answer:\s*(.*)", ai_res).group(1)
            if final_anwer:
                return True, final_anwer
        except Exception as e:
            pass
        return False, ""

    @staticmethod
    def parseToolCall(ai_res: str) -> tuple[bool, str, dict]:
        """Agent是否需要使用工具

        Args:
            ai_res (str): AI回复的文本

        Returns:
            tuple: 包含以下元素的元组:
                - bool: 是否调用tool
                - tool_name(str): 工具名称
                - tool_args(dcit): 工具输入的参数字典
        """
        use_tool = False
        tool_name = ""
        tool_args = {}

        try:
            tool_name = re.search(r"Action:\s*(.*)", ai_res).group(1)
            tool_args_str = re.search(r"Action Input:\s*(.*)", ai_res, re.DOTALL).group(1)
            tool_args = json.loads(tool_args_str)
            if tool_name:
                use_tool = True
        except Exception as e:
            pass

        return use_tool, tool_name, tool_args

    @staticmethod
    def get_cryptocurrency_price(coin_name: str) -> str:
        """提供给 Agent 的 function calling

        Args:
            coin_name (str): 币种名称

        Returns:
            str: 币种价值
        """
        coin_name = CoinAgent.preprocessing_coin_name(coin_name)

        match coin_name:
            case coin_name if coin_name in ["bitcoin", "btc"]:
                return random.randrange(60000, 69000)
            case coin_name if coin_name in ["ethereum", "eth"]:
                return random.randrange(2000, 3000)
            case coin_name if coin_name in ["dogecoin", "doge"]:
                return round(abs(random.random() - 0.5), 2)

    @staticmethod
    def list_all_cryptocurrency() -> list[str]:
        """列出所有支持的币种名称

        Returns:
            list[str]: 支持的币种名称列表
        """
        return ["bitcoin", "ethereum", "dogecoin"]

    def get_tool_names(self) -> list[str]:
        tool_names = []
        for tool in self.tools:
            tool_names.append(tool.get("name", None))

        return ",".join([i for i in tool_names if i is not None])

    @staticmethod
    def preprocessing_coin_name(coin_name: str) -> str:
        """预处理币种名称

        Args:
            coin_name (str): AI传入的币种名称

        Returns:
            str: 格式化后的币种名称
        """
        new_name = coin_name.strip("\n").strip()
        return new_name


if __name__ == "__main__":
    agent = CoinAgent()
    agent.invoke("对比一下比特币和其他币的价格")
