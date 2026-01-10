

import os
from typing import Callable, Optional

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_openai import ChatOpenAI
api_key = os.getenv("DASHSCOPE_API_KEY") or os.getenv("OPENAI_API_KEY")


def create_qwen_llm(
    api_key: Optional[str] = None,
    model: str = "qwen-plus-2025-12-01",
    enable_search: bool = False,
    enable_thinking: bool = False,
    temperature: float = 0.7,
    **kwargs
) -> BaseChatModel:
    """
    创建通义千问模型实例

    Args:
        api_key: API密钥，如果为None则从环境变�� DASHSCOPE_API_KEY 读取
        model: 模型名称，默认 qwen-plus
               可选: qwen-turbo, qwen-plus, qwen-max, qwen-max-longcontext
        enable_search: 是否启用联网搜索（通过模型参数传递）
        enable_thinking: 是否启用思考模式（通过模型参数传递）
        temperature: 温度参数，控制输出随机性，范围 0-1
        **kwargs: 其他传递给 ChatOpenAI 的参数

    Returns:
        LangChain BaseChatModel 实例

    Example:
        >>> llm = create_qwen_llm(api_key="your-key", model="qwen-plus")
        >>> result = llm.invoke("你好")
    """
    # 获取 API key
   

    # 通义千问兼容 OpenAI API 的基础配置
    config = {
        "model": model,
        "api_key": api_key,
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "temperature": temperature,
    }

    # 添加可选参数
    if enable_search:
        config["enable_search"] = True
    if enable_thinking:
        # 通义千问的思考模式参数
        config["enable_thinking"] = True

    # 添加额外参数
    config.update(kwargs)

    return ChatOpenAI(**config)

def create_llm_factory(
    model: str = "qwen-plus-2025-12-01",
    api_key: Optional[str] = None,
    enable_search: bool = False,
    enable_thinking: bool = False,
    **base_kwargs
) -> Callable[..., BaseChatModel]:
    """
    创建 LLM 工厂函数，返回的 callback 可创建新的 BaseChatModel 实例

    预先配置 api_key 和 model，返回的 callback 只需要传入 temperature 等运行时参数。

    Args:
        model: 模型名称，默认 qwen-plus-2025-12-01
        api_key: API密钥，如果为None则从环境变量读取
        enable_search: 是否启用联网搜索
        enable_thinking: 是否启用思考模式
        **base_kwargs: 其他预配置的参数

    Returns:
        返回一个函数，调用时传入 temperature 等参数即可创建新实例

    Example:
        >>> factory = create_llm_factory(model="qwen-plus")
        >>> llm1 = factory(temperature=0.3)  # 创建低温实例
        >>> llm2 = factory(temperature=0.9)  # 创建高温实例
    """
    # 获取 API key
    if api_key is None:
        api_key = os.getenv("DASHSCOPE_API_KEY") or os.getenv("OPENAI_API_KEY")

    # 预配置参数
    base_config = {
        "model": model,
        "api_key": api_key,
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
    }

    if enable_search:
        base_config["enable_search"] = True
    if enable_thinking:
        base_config["enable_thinking"] = True

    base_config.update(base_kwargs)

    def callback(
        temperature: float = 0.7,
        **kwargs
    ) -> BaseChatModel:
        """创建新的 LLM 实例"""
        config = {**base_config, "temperature": temperature}
        config.update(kwargs)
        return ChatOpenAI(**config)

    return callback

if __name__ == "__main__":
    factory = create_llm_factory(model="qwen-plus-2025-12-01")
    llm1 = factory(temperature=0.3)  # 创建低温实例S
    print(llm1)
    print(llm1.invoke("你好"))
