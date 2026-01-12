# NodeDefinition Schema 参考 (Schema Reference)

`plan.json` 中节点的完整字段规范。

## 字段参考 (Field Reference)

| 字段 | 类型 | 是否必填 | 默认值 | 描述 |
|-------|------|----------|---------|-------------|
| `node_type` | `string` | 是 | - | 节点类型：`"llm-first"` 或 `"tool-first"` |
| `node_name` | `string` | 是 | - | 用于日志记录和调试的节点名称 |
| `thread_id` | `string` | 是 | - | 执行上下文的线程 ID |
| `task_prompt` | `string` | 否 | `""` | LLM 任务描述。为空则跳过 LLM 执行 |
| `tools` | `string[]` | 否 | `null` | 该节点可用的工具名称列表 |
| `enable_tool_loop` | `boolean` | 否 | `false` | 允许执行多个工具调用直至任务完成 |
| `tools_limit` | `object` | 否 | `null` | 每个工具的最大调用次数：`{"tool_name": 5}` |
| `initial_tool_name` | `string` | **仅 tool-first** | - | 初始执行的工具（tool-first 必填） |
| `initial_tool_args` | `object` | 否 | `null` | 初始工具调用的参数 |
| `data_in_thread` | `string` | 否 | `"main"` | 数据注入的源线程 ID（仅限新线程） |
| `data_in_slice` | `array` | 否 | `[0, 1]` | 消息片段范围 `[start, end)`，默认仅第一条消息 |
| `data_out` | `boolean` | 否 | `false` | 是否将结果输出到 data_out 字典 |
| `data_out_thread` | `string` | 否 | `"main"` | 合并输出的目标线程 ID |
| `data_out_description` | `string` | 否 | `""` | 输出内容的前缀 |

## 节点类型 (Node Types)

### llm-first

LLM 首先执行，可选择调用工具。

**必填字段**：`node_type`, `node_name`, `thread_id`

**可选字段**：`task_prompt`, `tools`, `enable_tool_loop`, `tools_limit`, `data_in_thread`, `data_in_slice`, `data_out`, `data_out_thread`, `data_out_description`

**当 `task_prompt` 为空时的行为**：创建一个仅执行数据流操作（无 LLM 推理）的空节点。用于线程初始化或跨线程数据移动。

### tool-first

工具首先执行，然后 LLM 分析结果。

**必填字段**：`node_type`, `node_name`, `thread_id`, `initial_tool_name`

**可选字段**：`initial_tool_args`, `task_prompt`, `tools`, `enable_tool_loop`, `tools_limit`, `data_in_thread`, `data_in_slice`, `data_out`, `data_out_thread`, `data_out_description`

**当 `task_prompt` 为空时的行为**：仅执行工具，不进行 LLM 分析。结果存储在线程历史记录中。

## 线程隔离规则 (Thread Isolation Rules)

1. **新线程创建**：当首次遇到某个 `thread_id` 时
   - `data_in_thread` 指定初始消息的源线程
   - `data_in_slice` 控制注入哪些消息
   - 每个线程仅在初始化时执行**一次**（仅限第一个节点）

2. **现有线程**：同一线程中的后续节点
   - 从之前的消息历史记录继续
   - `data_in_thread` 和 `data_in_slice` 将被**忽略**

3. **无父级概念**：线程是平级的 - 数据流通过显式配置实现。

## 数据流示例 (Data Flow Examples)

### 示例 1：简单单线程

```json
{
  "node_type": "llm-first",
  "node_name": "Analyze",
  "thread_id": "main",
  "task_prompt": "分析此数据"
}
```

### 示例 2：带聚合的并行收集

```json
{
  "nodes": [
    {
      "node_type": "llm-first",
      "node_name": "创建聚合线程",
      "thread_id": "summary",
      "task_prompt": "",
      "data_out": false
    },
    {
      "node_type": "tool-first",
      "node_name": "获取 A",
      "thread_id": "fetch_a",
      "initial_tool_name": "get_a",
      "data_in_thread": "main",
      "data_out": true,
      "data_out_thread": "summary",
      "data_out_description": "数据源 A："
    },
    {
      "node_type": "llm-first",
      "node_name": "综合汇总",
      "thread_id": "summary",
      "task_prompt": "合并所有结果",
      "data_out": true,
      "data_out_thread": "main"
    }
  ]
}
```

## 校验规则 (Validation Rules)

1. `tool-first` 要求必须有 `initial_tool_name`
2. `llm-first` **不应**包含 `initial_tool_name`
3. 空的 `task_prompt` = 跳过 LLM 执行（空节点）
4. `data_in_*` 仅在**新**线程创建时生效
