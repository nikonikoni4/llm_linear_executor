# 计划示例 (Plan Examples)

`llm_linear_executor` 计划的实际工作流模式。

## 模式 1：简单 LLM 任务

用于基本推理的单线程工作流。

```json
{
  "simple_task": {
    "task": "总结文本",
    "nodes": [{
      "node_type": "llm-first",
      "node_name": "Summarizer",
      "thread_id": "main",
      "task_prompt": "用 3 条要点总结以下文本。"
    }]
  }
}
```

## 模式 2：工具优先的数据获取

先获取数据，然后使用 LLM 进行分析。

```json
{
  "data_fetch": {
    "task": "查询并分析数据库",
    "nodes": [{
      "node_type": "tool-first",
      "node_name": "Query Database",
      "thread_id": "main",
      "initial_tool_name": "query_db",
      "initial_tool_args": {"table": "users", "limit": 100},
      "task_prompt": "从用户数据中分析趋势。"
    }]
  }
}
```

## 模式 3：并行数据收集

多个线程并行获取数据，然后进行汇总。

**核心概念：**
- 空节点创建聚合线程，不执行 LLM。
- 每个获取节点将结果输出到聚合线程。
- 最后一个节点综合所有结果。

```json
{
  "parallel_fetch": {
    "task": "从多个 API 收集数据",
    "nodes": [
      {
        "node_type": "llm-first",
        "node_name": "初始化聚合器",
        "thread_id": "summary",
        "task_prompt": "",
        "data_out": false
      },
      {
        "node_type": "tool-first",
        "node_name": "获取 API A",
        "thread_id": "fetch_a",
        "initial_tool_name": "call_api_a",
        "data_in_thread": "main",
        "data_out": true,
        "data_out_thread": "summary",
        "data_out_description": "API A 结果："
      },
      {
        "node_type": "tool-first",
        "node_name": "获取 API B",
        "thread_id": "fetch_b",
        "initial_tool_name": "call_api_b",
        "data_in_thread": "main",
        "data_out": true,
        "data_out_thread": "summary",
        "data_out_description": "API B 结果："
      },
      {
        "node_type": "tool-first",
        "node_name": "获取 API C",
        "thread_id": "fetch_c",
        "initial_tool_name": "call_api_c",
        "data_in_thread": "main",
        "data_out": true,
        "data_out_thread": "summary",
        "data_out_description": "API C 结果："
      },
      {
        "node_type": "llm-first",
        "node_name": "综合汇总",
        "thread_id": "summary",
        "task_prompt": "将所有 API 结果综合成一份统一的报告。",
        "data_out": true,
        "data_out_thread": "main",
        "data_out_description": "最终报告："
      }
    ]
  }
}
```

## 模式 4：序列化工具链

链式调用多个工具，每个调用都依赖于前一个输出。

```json
{
  "tool_chain": {
    "task": "多步数据管道",
    "nodes": [
      {
        "node_type": "tool-first",
        "node_name": "步骤 1：提取",
        "thread_id": "main",
        "initial_tool_name": "extract_data",
        "task_prompt": "进入转换步骤。"
      },
      {
        "node_type": "tool-first",
        "node_name": "步骤 2：转换",
        "thread_id": "main",
        "initial_tool_name": "transform_data",
        "task_prompt": "进入加载步骤。"
      },
      {
        "node_type": "tool-first",
        "node_name": "步骤 3：加载",
        "thread_id": "main",
        "initial_tool_name": "load_data",
        "task_prompt": "报告完成状态。"
      }
    ]
  }
}
```

## 模式 5：多维分析

使用不同的参数调用相同的工具，分别进行分析，然后进行合并。

**实际示例：** 分析不同维度的每日 activity 摘要。

```json
{
  "daily_summary": {
    "task": "全面的每日活动摘要",
    "nodes": [
      {
        "node_type": "llm-first",
        "node_name": "创建 summary 线程",
        "thread_id": "summary",
        "task_prompt": "",
        "data_out": false
      },
      {
        "node_type": "tool-first",
        "node_name": "获取活跃分布",
        "thread_id": "node_active",
        "initial_tool_name": "get_daily_stats",
        "initial_tool_args": {"module": "active_distribution"},
        "task_prompt": "简要分析活动模式。",
        "data_in_thread": "main",
        "data_out": true,
        "data_out_thread": "summary",
        "data_out_description": "活跃分布："
      },
      {
        "node_type": "tool-first",
        "node_name": "获取行为统计",
        "thread_id": "node_behavior",
        "initial_tool_name": "get_daily_stats",
        "initial_tool_args": {"module": "behavior_stats"},
        "task_prompt": "简要分析行为模式。",
        "data_in_thread": "main",
        "data_out": true,
        "data_out_thread": "summary",
        "data_out_description": "行为统计："
      },
      {
        "node_type": "tool-first",
        "node_name": "获取任务状态",
        "thread_id": "node_tasks",
        "initial_tool_name": "get_daily_stats",
        "initial_tool_args": {"module": "task_status"},
        "task_prompt": "简要分析任务完成情况。",
        "data_in_thread": "main",
        "data_out": true,
        "data_out_thread": "summary",
        "data_out_description": "任务状态："
      },
      {
        "node_type": "llm-first",
        "node_name": "生成最终摘要",
        "thread_id": "summary",
        "task_prompt": "将所有维度的分析结合成一份全面的每日摘要。",
        "data_in_thread": "main",
        "data_out": true,
        "data_out_thread": "main",
        "data_out_description": "每日摘要："
      }
    ]
  }
}
```

## 模式 6：模拟条件分支

由于没有路由节点，可以通过多个并行线程来模拟分支。

```json
{
  "branching": {
    "task": "尝试多种方法",
    "nodes": [
      {
        "node_type": "tool-first",
        "node_name": "方案 A",
        "thread_id": "branch_a",
        "initial_tool_name": "method_a",
        "data_in_thread": "main",
        "data_out": true,
        "data_out_thread": "main",
        "data_out_description": "方案 A 结果："
      },
      {
        "node_type": "tool-first",
        "node_name": "方案 B",
        "thread_id": "branch_b",
        "initial_tool_name": "method_b",
        "data_in_thread": "main",
        "data_out": true,
        "data_out_thread": "main",
        "data_out_description": "方案 B 结果："
      },
      {
        "node_type": "llm-first",
        "node_name": "对比并选择",
        "thread_id": "main",
        "task_prompt": "对比两种方案并选择更好的结果。",
        "tools": null
      }
    ]
  }
}
```

## 模式 7：仅工具节点（无 LLM）

使用空的 `task_prompt` 来跳过 LLM 分析。

```json
{
  "tool_only": {
    "task": "直接执行操作而无需分析",
    "nodes": [{
      "node_type": "tool-first",
      "node_name": "仅执行",
      "thread_id": "main",
      "initial_tool_name": "save_to_file",
      "initial_tool_args": {"path": "/tmp/output.txt"},
      "task_prompt": ""
    }]
  }
}
```

## 模式 8：消息片段注入

控制从源线程注入哪些消息。

```json
{
  "message_slice": {
    "task": "处理特定的消息范围",
    "nodes": [{
      "node_type": "llm-first",
      "node_name": "处理前 3 条消息",
      "thread_id": "processor",
      "task_prompt": "仅处理来自 main 线程的前 3 条消息。",
      "data_in_thread": "main",
      "data_in_slice": [0, 3]
    }]
  }
}
```

## 最佳实践

1. **线程命名**：使用具有描述性的名称，如 `summary`、`fetch_x`、`branch_a`。
2. **空节点**：使用 `task_prompt: ""` 创建不需要 LLM 执行的线程。
3. **聚合**：创建专门的聚合器线程，并在最后合并结果。
4. **数据流**：为新线程始终指定 `data_in_thread`（默认为 main）。
5. **工具限制**：设置 `tools_limit` 以防止工具调用失控。
6. **描述信息**：使用 `data_out_description` 清晰地标记合并后的结果。
