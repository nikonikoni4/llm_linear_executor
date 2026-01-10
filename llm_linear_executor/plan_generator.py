"""
执行计划生成器

使用 LLM 根据技能定义生成执���计划 (ExecutionPlan)
"""
from typing import Sequence
from pathlib import Path
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.tools import BaseTool
from .schemas import ExecutionPlan


def read_skill_definition(skills_path: str | Path) -> str:
    """
    读取技能定义文件

    Args:
        skills_path: 技能定义文件路径 (.md 文件)

    Returns:
        技能定义内容字符串
    """
    if isinstance(skills_path, str):
        skills_path = Path(skills_path)

    if not skills_path.exists():
        raise FileNotFoundError(f"技能定义文件不存在: {skills_path}")

    with open(skills_path, "r", encoding="utf-8") as f:
        return f.read()


def plan_generator(
    task: str,
    skills_path: str | Path,
    llm,
    tools: Sequence[BaseTool]
) -> ExecutionPlan:
    """
    根据技能定义生成执行计划

    Args:
        skills_path: 技能定义文件路径
        llm: langchain的chatmodel
        enable_thinking: 是否启用思考模式

    Returns:
        生成的执行计划对象

    Example:
        >>> plan = plan_generator(
        ...     skills_path="skills/user_behavior_summary.md"
        ... )
        >>> print(plan.task)
    """
    # 读取技能定义
    skill_definition = read_skill_definition(skills_path)

    tool_definitions = "\n".join(
        [f"{tool.name}: {tool.description}, args: {tool.args}" for tool in tools]
    )

    # 设置输出解析器
    parser = PydanticOutputParser(pydantic_object=ExecutionPlan)

    # 构建提示词
    prompt = f"""你需要依据给定的技能定义，为用户生成一个执行计划。
# 技能定义
{skill_definition}
# 可用的工具
{tool_definitions}
# 输出格式
{parser.get_format_instructions()}
# 用户的任务
{task}
"""

    print(prompt)

    # 创建 LLM 并生成计划
    result = llm.invoke(prompt)
    print(result)

    # 解析结果为 ExecutionPlan
    execution_plan: ExecutionPlan = parser.parse(result.content)
    return execution_plan


if __name__ == "__main__":
    from .save_plan import save_plan_as_template

    # 示例：生成并保存计划
    plan = plan_generator(
        date="2026-01-03",
        skills_path=r"D:\desktop\simple-llm-playground\skills\user_behavior_summary.md"
    )
    print(plan)

    # 提取工具调用次数作为默认限制
    tools_limit = {}
    for node in plan.nodes:
        if node.node_type == "tool" and node.tool_name:
            tools_limit[node.tool_name] = tools_limit.get(node.tool_name, 0) + 1

    save_plan_as_template(
        plan=plan,
        date="2026-01-03",
        output_path=r"llm_linear_executor\patterns\test.json",
        pattern_name="comprehensive",
        tools_limit=tools_limit
    )
