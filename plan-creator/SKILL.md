---
name: plan-creator
description: Generate plan.json files for llm_linear_executor. Use when creating an execution plan, workflow definition, or task graph for the llm_linear_executor engine. The plan defines sequential nodes with LLM/tool execution, thread isolation, and data flow configuration. Key triggers - create a plan, generate workflow, design execution graph, build multi-step process.
---

# Plan Creator

Generate `plan.json` files for the `llm_linear_executor` engine. Each plan defines a workflow as a sequence of nodes that execute with thread-based context isolation.

**Quick workflow for creating a plan:**
1. Identify the task requirements and available tools
2. Choose node types (llm-first for reasoning, tool-first for data fetching)
3. Design thread structure (main only, or parallel threads for aggregation)
4. Configure data flow between threads
5. Set tool limits and looping behavior

## Plan Structure

```json
{
  "pattern_name": {
    "task": "Human-readable task description",
    "nodes": [ ... ]
  }
}
```

- `pattern_name`: Unique identifier for this plan pattern
- `task`: Description of what this plan accomplishes
- `nodes`: Ordered list of nodes to execute sequentially

## Node Types

### `llm-first`

LLM executes first, optionally calling tools. Use for reasoning-before-action scenarios.

**Flow:** `LLM Thinking → [Optional Tool Call(s)] → [Optional LLM Analysis]`

**When to use:**
- Need LLM reasoning before taking action
- Complex decision making
- Analysis and synthesis tasks

**Empty node pattern:** Set `task_prompt: ""` to create an empty node that only performs data flow operations. Used for thread initialization.

### `tool-first`

Tool executes first, then LLM analyzes. Use for data-retrieval-before-analysis scenarios.

**Flow:** `Execute Tool → [Optional LLM Analysis] → [Optional More Tools]`

**When to use:**
- Need raw data before analysis
- API calls or queries
- Data fetching tasks

**Required:** `initial_tool_name` must be specified

**Tool-only pattern:** Set `task_prompt: ""` to execute tool without LLM analysis.

## Thread Isolation

Each `thread_id` maintains an independent message history. This prevents context contamination between parallel workflows.

- `main` thread: Primary execution thread (default)
- Custom threads: Isolated contexts for subtasks

**Key patterns:**
1. Single workflow: Use only `main` thread
2. Parallel data gathering: Create separate threads, merge results to `main`
3. Summary aggregation: Create a `summary` thread, collect data from multiple nodes

## Data Flow Configuration

### Data Input (`data_in_thread`, `data_in_slice`)

Inject messages from another thread when creating a NEW thread. Only executes once during thread creation.

| Config | Behavior |
|--------|----------|
| `data_in_thread: "main"` | Inject last message from main |
| `data_in_thread: "other"` | Inject last message from other thread |
| `data_in_slice: [0, 2]` | Inject first 2 messages (0-indexed, exclusive end) |
| Not specified | Uses `main` thread by default |

### Data Output (`data_out`, `data_out_thread`, `data_out_description`)

Control whether node results merge to another thread.

| Config | Behavior |
|--------|----------|
| `data_out: true` | Output to data_out dict and merge to target |
| `data_out_thread: "summary"` | Merge to summary thread (default: main) |
| `data_out_description: "Analysis: "` | Prefix for output content |
| `data_out: false` | Keep result in current thread only |

**Output format:** `{role: 'assistant', content: description + result}`

## Common Patterns

### Pattern 1: Simple LLM Task

```json
{
  "simple_task": {
    "task": "Basic LLM reasoning",
    "nodes": [{
      "node_type": "llm-first",
      "node_name": "Reason",
      "thread_id": "main",
      "task_prompt": "Your task here"
    }]
  }
}
```

### Pattern 2: Tool-First Data Fetch

```json
{
  "data_fetch": {
    "task": "Fetch and analyze data",
    "nodes": [{
      "node_type": "tool-first",
      "node_name": "Get Data",
      "thread_id": "main",
      "initial_tool_name": "query_database",
      "initial_tool_args": {"table": "users"},
      "task_prompt": "Analyze the retrieved data"
    }]
  }
}
```

### Pattern 3: Parallel Collection + Aggregation

```json
{
  "aggregate": {
    "task": "Collect from multiple sources",
    "nodes": [
      {
        "node_type": "llm-first",
        "node_name": "Create summary thread",
        "thread_id": "summary",
        "task_prompt": "",
        "data_out": false
      },
      {
        "node_type": "tool-first",
        "node_name": "Fetch source A",
        "thread_id": "node_a",
        "initial_tool_name": "get_source_a",
        "data_in_thread": "main",
        "data_out_thread": "summary",
        "data_out": true,
        "data_out_description": "Source A: "
      },
      {
        "node_type": "tool-first",
        "node_name": "Fetch source B",
        "thread_id": "node_b",
        "initial_tool_name": "get_source_b",
        "data_in_thread": "main",
        "data_out_thread": "summary",
        "data_out": true,
        "data_out_description": "Source B: "
      },
      {
        "node_type": "llm-first",
        "node_name": "Synthesize",
        "thread_id": "summary",
        "task_prompt": "Synthesize all data into a final report",
        "data_in_thread": "main",
        "data_out_thread": "main",
        "data_out": true,
        "data_out_description": "Final report: "
      }
    ]
  }
}
```

## Tool Configuration

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `tools` | `string[]` | `null` | Available tool names for this node |
| `enable_tool_loop` | `boolean` | `false` | Allow multiple tool calls until task complete |
| `tools_limit` | `object` | `null` | Max calls per tool: `{"tool_name": 5}` |

## Validation Rules

1. `tool-first` **must** specify `initial_tool_name`
2. `llm-first` **should not** specify `initial_tool_name`
3. Empty `task_prompt` in `tool-first` = execute tool only (no LLM)
4. `data_in_*` only applies when creating a NEW thread

## Reference Documentation

- **Complete schema**: See [schema.md](references/schema.md) for all field definitions and validation rules
- **More examples**: See [examples.md](references/examples.md) for additional patterns including:
  - Sequential tool chaining
  - Multi-dimensional analysis
  - Conditional branching simulation
  - Message slice injection
