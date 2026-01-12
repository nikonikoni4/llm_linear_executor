---
name: plan-creator
description: 生成 llm_linear_executor 的 plan.json 文件。在为 llm_linear_executor 引擎创建执行计划、工作流定义或任务图时使用。该计划定义了包含 LLM/工具执行、线程隔离和数据流配置的序列化节点。关键触发词：创建计划、生成工作流、设计执行图、构建多步流程。
---

# 计划创建器 (Plan Creator)

为 `llm_linear_executor` 引擎生成 `plan.json` 文件。每个计划将工作流定义为一序列在基于线程的上下文隔离中执行的节点。

**创建计划的快速工作流：**
1. 识别任务需求和可用工具
2. 选择节点类型（`llm-first` 用于推理，`tool-first` 用于数据获取）
3. 设计线程结构（仅主线程，或用于聚合的并行线程）
4. 配置线程间的数据流
5. 设置工具限制和循环行为

## 计划结构

```json
{
  "pattern_name": {
    "task": "人类可读的任务描述",
    "nodes": [ ... ]
  }
}
```

- `pattern_name`: 该计划模式的唯一标识符
- `task`: 该计划完成内容的描述
- `nodes`: 按顺序执行的节点列表

## 节点类型

### `llm-first`

LLM 首先执行，可选择调用工具。用于“先推理后操作”的场景。

**流程：** `LLM 思考 → [可选的工具调用] → [可选的 LLM 分析]`

**适用场景：**
- 在采取行动前需要 LLM 推理
- 复杂的决策制定
- 分析和综合任务

**空节点模式：** 设置 `task_prompt: ""` 以创建一个仅执行数据流操作的空节点。用于线程初始化。

### `tool-first`

工具首先执行，然后由 LLM 进行分析。用于“先通过数据检索后分析”的场景。

**流程：** `执行工具 → [可选的 LLM 分析] → [可选的更多工具]`

**适用场景：**
- 在分析前需要原始数据
- API 调用或查询
- 数据获取任务

**必填项：** 必须指定 `initial_tool_name`

**仅执行工具模式：** 设置 `task_prompt: ""` 以仅执行工具而不进行 LLM 分析。

## 线程隔离

每个 `thread_id` 维护一个独立的动态消息历史记录。这可以防止并行工作流之间的上下文污染。

- `main` 线程：主执行线程（默认）
- 自定义线程：用于子任务的隔离上下文

**关键模式：**
1. 单一工作流：仅使用 `main` 线程
2. 并行数据收集：创建不同的线程，将结果合并到 `main`
3. 摘要聚合：创建一个 `summary` 线程，从多个节点收集数据

## 数据流配置

### 数据输入 (`data_in_thread`, `data_in_slice`)

在创建新线程时从另一个线程注入消息。仅在线程创建期间执行一次。

| 配置 | 行为 |
|--------|----------|
| `data_in_thread: "main"` | 注入来自 main 的最后一条消息 |
| `data_in_thread: "other"` | 注入来自 other 线程的最后一条消息 |
| `data_in_slice: [0, 2]` | 注入前两条消息（从 0 开始，不包含结束索引） |
| 未指定 | 默认使用 `main` 线程 |

### 数据输出 (`data_out`, `data_out_thread`, `data_out_description`)

控制节点结果是否合并到另一个线程。

| 配置 | 行为 |
|--------|----------|
| `data_out: true` | 输出到 data_out 字典并合并到目标线程 |
| `data_out_thread: "summary"` | 合并到 summary 线程（默认：main） |
| `data_out_description: "分析："` | 输出内容的前缀 |
| `data_out: false` | 仅将结果保留在当前线程中 |

**输出格式：** `{role: 'assistant', content: description + result}`

## 常见模式

### 模式 1：简单 LLM 任务

```json
{
  "simple_task": {
    "task": "基础 LLM 推理",
    "nodes": [{
      "node_type": "llm-first",
      "node_name": "Reason",
      "thread_id": "main",
      "task_prompt": "你的任务描述"
    }]
  }
}
```

### 模式 2：工具优先的数据获取

```json
{
  "data_fetch": {
    "task": "获取并分析数据",
    "nodes": [{
      "node_type": "tool-first",
      "node_name": "Get Data",
      "thread_id": "main",
      "initial_tool_name": "query_database",
      "initial_tool_args": {"table": "users"},
      "task_prompt": "分析获取到的数据"
    }]
  }
}
```

### 模式 3：并行收集 + 聚合

```json
{
  "aggregate": {
    "task": "从多个渠道收集信息",
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
        "node_name": "获取数据源 A",
        "thread_id": "node_a",
        "initial_tool_name": "get_source_a",
        "data_in_thread": "main",
        "data_out_thread": "summary",
        "data_out": true,
        "data_out_description": "数据源 A："
      },
      {
        "node_type": "tool-first",
        "node_name": "获取数据源 B",
        "thread_id": "node_b",
        "initial_tool_name": "get_source_b",
        "data_in_thread": "main",
        "data_out_thread": "summary",
        "data_out": true,
        "data_out_description": "数据源 B："
      },
      {
        "node_type": "llm-first",
        "node_name": "综合汇总",
        "thread_id": "summary",
        "task_prompt": "将所有数据综合成最终报告",
        "data_in_thread": "main",
        "data_out_thread": "main",
        "data_out": true,
        "data_out_description": "最终报告："
      }
    ]
  }
}
```

## 工具配置

| 字段 | 类型 | 默认值 | 描述 |
|-------|------|---------|-------------|
| `tools` | `string[]` | `null` | 该节点可用的工具名称 |
| `enable_tool_loop` | `boolean` | `false` | 允许执行多个工具调用直至任务完成 |
| `tools_limit` | `object` | `null` | 每个工具的最大调用次数：`{"tool_name": 5}` |

## 校验规则

1. `tool-first` **必须**指定 `initial_tool_name`
2. `llm-first` **不应**指定 `initial_tool_name`
3. `tool-first` 中空的 `task_prompt` = 仅执行工具（无 LLM）
4. `data_in_*` 仅在创建**新**线程时有效

## 参考文档

- **完整 Schema**：关于所有字段定义和校验规则，请参阅 [schema.md](references/schema.md)
- **更多示例**：关于更多模式，请参阅 [examples.md](references/examples.md)，包含：
  - 序列化工具链
  - 多维分析
  - 模拟条件分支
  - 消息片段注入
