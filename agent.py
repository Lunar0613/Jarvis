import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)

def calculator(expression: str):
    try:
        return str(eval(expression))
    except Exception as e:
        return f"计算失败：{str(e)}"

tools = {
    "calculator": calculator
}

system_prompt = """
你是一个Agent，拥有calculator工具。
需要计算时，严格输出JSON：{"tool":"calculator","args":{"expression":"1+2*3"}}
不需要工具、任务完成时，直接输出自然语言答案，不要输出JSON。
"""

def run_agent(user_query: str, max_round=5):
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_query}
    ]
    for i in range(max_round):
        resp = client.chat.completions.create(
            model="deepseek-flash",
            messages=messages,
            temperature=0.3
        )
        content = resp.choices[0].message.content.strip()
        print(f"\n【模型输出】{content}")

        try:
            call = json.loads(content)
            if "tool" in call and call["tool"] in tools:
                result = tools[call["tool"]](**call["args"])
                print(f"【工具返回】{result}")
                messages.append({"role": "assistant", "content": content})
                messages.append({"role": "user", "content": f"工具结果：{result}"})
                continue
        except json.JSONDecodeError:
            return content
    return "达到最大循环轮次，停止"

if __name__ == "__main__":
    task = input("请输入任务：")
    ans = run_agent(task)
    print("\n✅ Agent最终结果：", ans)
