# NodeDefinition Schema Reference

Complete field specification for nodes in `plan.json`.

## Field Reference

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `node_type` | `string` | Yes | - | Node type: `"llm-first"` or `"tool-first"` |
| `node_name` | `string` | Yes | - | Node name for logging and debugging |
| `thread_id` | `string` | Yes | - | Thread ID for execution context |
| `task_prompt` | `string` | No | `""` | LLM task description. Empty = skip LLM execution |
| `tools` | `string[]` | No | `null` | Available tool names for this node |
| `enable_tool_loop` | `boolean` | No | `false` | Allow multiple tool calls until task complete |
| `tools_limit` | `object` | No | `null` | Max calls per tool: `{"tool_name": 5}` |
| `initial_tool_name` | `string` | **tool-first only** | - | Initial tool to execute (required for tool-first) |
| `initial_tool_args` | `object` | No | `null` | Arguments for initial tool call |
| `data_in_thread` | `string` | No | `"main"` | Source thread ID for data injection (new threads only) |
| `data_in_slice` | `array` | No | `null` | Message slice range `[start, end)`, null = last message only |
| `data_out` | `boolean` | No | `false` | Whether to output result to data_out dict |
| `data_out_thread` | `string` | No | `"main"` | Target thread ID for merging output |
| `data_out_description` | `string` | No | `""` | Prefix for output content |

## Node Types

### llm-first

LLM executes first, optionally calling tools.

**Required fields:** `node_type`, `node_name`, `thread_id`

**Optional fields:** `task_prompt`, `tools`, `enable_tool_loop`, `tools_limit`, `data_in_thread`, `data_in_slice`, `data_out`, `data_out_thread`, `data_out_description`

**Behavior with empty `task_prompt`:** Creates an empty node that only performs data flow operations (no LLM inference). Used for thread initialization or cross-thread data movement.

### tool-first

Tool executes first, then LLM analyzes result.

**Required fields:** `node_type`, `node_name`, `thread_id`, `initial_tool_name`

**Optional fields:** `initial_tool_args`, `task_prompt`, `tools`, `enable_tool_loop`, `tools_limit`, `data_in_thread`, `data_in_slice`, `data_out`, `data_out_thread`, `data_out_description`

**Behavior with empty `task_prompt`:** Executes the tool only, no LLM analysis. Result is stored in thread history.

## Thread Isolation Rules

1. **New thread creation**: When `thread_id` is first encountered
   - `data_in_thread` specifies source thread for initial messages
   - `data_in_slice` controls which messages are injected
   - Only executes ONCE per thread (first node only)

2. **Existing thread**: Subsequent nodes in same thread
   - Continue from previous message history
   - `data_in_thread` and `data_in_slice` are **ignored**

3. **No parent concept**: Threads are flat - data flow is explicitly configured

## Data Flow Examples

### Example 1: Simple single-thread

```json
{
  "node_type": "llm-first",
  "node_name": "Analyze",
  "thread_id": "main",
  "task_prompt": "Analyze this data"
}
```

### Example 2: Parallel collection with aggregation

```json
{
  "nodes": [
    {
      "node_type": "llm-first",
      "node_name": "Create aggregator thread",
      "thread_id": "summary",
      "task_prompt": "",
      "data_out": false
    },
    {
      "node_type": "tool-first",
      "node_name": "Fetch A",
      "thread_id": "fetch_a",
      "initial_tool_name": "get_a",
      "data_in_thread": "main",
      "data_out": true,
      "data_out_thread": "summary",
      "data_out_description": "Source A: "
    },
    {
      "node_type": "llm-first",
      "node_name": "Summarize",
      "thread_id": "summary",
      "task_prompt": "Combine all results",
      "data_out": true,
      "data_out_thread": "main"
    }
  ]
}
```

## Validation Rules

1. `tool-first` requires `initial_tool_name`
2. `llm-first` should NOT have `initial_tool_name`
3. Empty `task_prompt` = skip LLM execution (empty node)
4. `data_in_*` only applies on NEW thread creation
