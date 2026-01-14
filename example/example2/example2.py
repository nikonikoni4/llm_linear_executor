import sys
import os
from os import path
# Add parent directory to sys.path
current_dir = path.dirname(path.abspath(__file__))
parent_dir = path.dirname(current_dir)
project_root = path.dirname(parent_dir)
if project_root not in sys.path:
    sys.path.append(project_root)

# 1. 导入或编写tools

from langchain_core.tools import tool

@tool
def add(a: int, b: int) -> int:
    """Add two integers."""
    return a + b


# 2. 编写一个简单的plan.json 

# {
#   "simple_calc": {
#     "task": "计算任务",
#     "nodes": [
#       {
#         "node_type": "llm-first",
#         "node_name": "Calculator",
#         "thread_id": "main",
#         "task_prompt": "Please calculate 10 + 20 using the tool.",
#         "tools": ["add"],
#         "tools_limit": {"add": 5},
#         "enable_tool_loop": true
#       }
#     ]
#   }
# }


# 3. 使用plan

from langchain_openai import ChatOpenAI
from llm_linear_executor.executor import Executor
from llm_linear_executor.os_plan import load_plan_from_template
__file__ = os.path.dirname(os.path.abspath(__file__))
# 准备依赖
tools_map = {"add": add}

# 定义 LLM 工厂函数 (Executor 内部会调用此函数创建 LLM 实例)
from llm_linear_executor.llm_factory import create_llm_factory
# api_key = "your_api_key"
# model = "gpt-4o"
# llm_factory = create_llm_factory(model,api_key,chat_model=ChatOpenAI)
llm_factory = create_llm_factory(chat_model=ChatOpenAI)

# 加载指定模版
# 注意：第二个参数 "simple_calc" 对应 json 中的 key
plan = load_plan_from_template(os.path.join(__file__, "example2.json"), pattern_name="simple_calc")

# 3. 执行
executor = Executor( 
    plan=plan, 
    tools_map=tools_map,
    llm_factory=llm_factory
)

result = executor.execute()
print(f"最终结果: {result['content']}")