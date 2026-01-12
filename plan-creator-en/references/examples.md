# Plan Examples

Real-world workflow patterns for `llm_linear_executor` plans.

## Pattern 1: Simple LLM Task

Single-thread workflow for basic reasoning.

```json
{
  "simple_task": {
    "task": "Summarize text",
    "nodes": [{
      "node_type": "llm-first",
      "node_name": "Summarizer",
      "thread_id": "main",
      "task_prompt": "Summarize the following text in 3 bullet points."
    }]
  }
}
```

## Pattern 2: Tool-First Data Fetch

Fetch data first, then analyze with LLM.

```json
{
  "data_fetch": {
    "task": "Query and analyze database",
    "nodes": [{
      "node_type": "tool-first",
      "node_name": "Query Database",
      "thread_id": "main",
      "initial_tool_name": "query_db",
      "initial_tool_args": {"table": "users", "limit": 100},
      "task_prompt": "Analyze the user data for trends."
    }]
  }
}
```

## Pattern 3: Parallel Data Collection

Multiple threads fetching data in parallel, then aggregating.

**Key concepts:**
- Empty node creates aggregator thread without LLM execution
- Each fetcher outputs to aggregator thread
- Final node synthesizes all results

```json
{
  "parallel_fetch": {
    "task": "Collect from multiple APIs",
    "nodes": [
      {
        "node_type": "llm-first",
        "node_name": "Initialize aggregator",
        "thread_id": "summary",
        "task_prompt": "",
        "data_out": false
      },
      {
        "node_type": "tool-first",
        "node_name": "Fetch API A",
        "thread_id": "fetch_a",
        "initial_tool_name": "call_api_a",
        "data_in_thread": "main",
        "data_out": true,
        "data_out_thread": "summary",
        "data_out_description": "API A result: "
      },
      {
        "node_type": "tool-first",
        "node_name": "Fetch API B",
        "thread_id": "fetch_b",
        "initial_tool_name": "call_api_b",
        "data_in_thread": "main",
        "data_out": true,
        "data_out_thread": "summary",
        "data_out_description": "API B result: "
      },
      {
        "node_type": "tool-first",
        "node_name": "Fetch API C",
        "thread_id": "fetch_c",
        "initial_tool_name": "call_api_c",
        "data_in_thread": "main",
        "data_out": true,
        "data_out_thread": "summary",
        "data_out_description": "API C result: "
      },
      {
        "node_type": "llm-first",
        "node_name": "Synthesize",
        "thread_id": "summary",
        "task_prompt": "Synthesize all API results into a unified report.",
        "data_out": true,
        "data_out_thread": "main",
        "data_out_description": "Final report: "
      }
    ]
  }
}
```

## Pattern 4: Sequential Tool Chaining

Chain multiple tool calls where each depends on previous output.

```json
{
  "tool_chain": {
    "task": "Multi-step data pipeline",
    "nodes": [
      {
        "node_type": "tool-first",
        "node_name": "Step 1: Extract",
        "thread_id": "main",
        "initial_tool_name": "extract_data",
        "task_prompt": "Proceed to transformation step."
      },
      {
        "node_type": "tool-first",
        "node_name": "Step 2: Transform",
        "thread_id": "main",
        "initial_tool_name": "transform_data",
        "task_prompt": "Proceed to loading step."
      },
      {
        "node_type": "tool-first",
        "node_name": "Step 3: Load",
        "thread_id": "main",
        "initial_tool_name": "load_data",
        "task_prompt": "Report completion status."
      }
    ]
  }
}
```

## Pattern 5: Multi-Dimensional Analysis

Same tool called with different parameters, analyzed separately, then combined.

**Real example:** Daily activity summary analyzing different dimensions.

```json
{
  "daily_summary": {
    "task": "Comprehensive daily activity summary",
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
        "node_name": "Get active distribution",
        "thread_id": "node_active",
        "initial_tool_name": "get_daily_stats",
        "initial_tool_args": {"module": "active_distribution"},
        "task_prompt": "Briefly analyze activity patterns.",
        "data_in_thread": "main",
        "data_out": true,
        "data_out_thread": "summary",
        "data_out_description": "Active distribution: "
      },
      {
        "node_type": "tool-first",
        "node_name": "Get behavior stats",
        "thread_id": "node_behavior",
        "initial_tool_name": "get_daily_stats",
        "initial_tool_args": {"module": "behavior_stats"},
        "task_prompt": "Briefly analyze behavior patterns.",
        "data_in_thread": "main",
        "data_out": true,
        "data_out_thread": "summary",
        "data_out_description": "Behavior stats: "
      },
      {
        "node_type": "tool-first",
        "node_name": "Get task status",
        "thread_id": "node_tasks",
        "initial_tool_name": "get_daily_stats",
        "initial_tool_args": {"module": "task_status"},
        "task_prompt": "Briefly analyze task completion.",
        "data_in_thread": "main",
        "data_out": true,
        "data_out_thread": "summary",
        "data_out_description": "Task status: "
      },
      {
        "node_type": "llm-first",
        "node_name": "Generate final summary",
        "thread_id": "summary",
        "task_prompt": "Combine all dimension analyses into a comprehensive daily summary.",
        "data_in_thread": "main",
        "data_out": true,
        "data_out_thread": "main",
        "data_out_description": "Daily Summary: "
      }
    ]
  }
}
```

## Pattern 6: Conditional Branching Simulation

Since there's no router node, simulate branching with multiple parallel threads.

```json
{
  "branching": {
    "task": "Try multiple approaches",
    "nodes": [
      {
        "node_type": "tool-first",
        "node_name": "Approach A",
        "thread_id": "branch_a",
        "initial_tool_name": "method_a",
        "data_in_thread": "main",
        "data_out": true,
        "data_out_thread": "main",
        "data_out_description": "Result A: "
      },
      {
        "node_type": "tool-first",
        "node_name": "Approach B",
        "thread_id": "branch_b",
        "initial_tool_name": "method_b",
        "data_in_thread": "main",
        "data_out": true,
        "data_out_thread": "main",
        "data_out_description": "Result B: "
      },
      {
        "node_type": "llm-first",
        "node_name": "Compare and select",
        "thread_id": "main",
        "task_prompt": "Compare both approaches and select the better result.",
        "tools": null
      }
    ]
  }
}
```

## Pattern 7: Tool-Only Node (No LLM)

Use empty `task_prompt` to skip LLM analysis.

```json
{
  "tool_only": {
    "task": "Execute action without analysis",
    "nodes": [{
      "node_type": "tool-first",
      "node_name": "Execute only",
      "thread_id": "main",
      "initial_tool_name": "save_to_file",
      "initial_tool_args": {"path": "/tmp/output.txt"},
      "task_prompt": ""
    }]
  }
}
```

## Pattern 8: Message Slice Injection

Control what messages from source thread are injected.

```json
{
  "message_slice": {
    "task": "Process specific message range",
    "nodes": [{
      "node_type": "llm-first",
      "node_name": "Process first 3 messages",
      "thread_id": "processor",
      "task_prompt": "Process only the first 3 messages from main thread.",
      "data_in_thread": "main",
      "data_in_slice": [0, 3]
    }]
  }
}
```

## Best Practices

1. **Thread naming**: Use descriptive names like `summary`, `fetch_x`, `branch_a`
2. **Empty nodes**: Use `task_prompt: ""` to create threads without LLM execution
3. **Aggregation**: Create dedicated aggregator thread, merge results at end
4. **Data flow**: Always specify `data_in_thread` for new threads (default is main)
5. **Tool limits**: Set `tools_limit` to prevent runaway tool calls
6. **Descriptions**: Use `data_out_description` to label merged results clearly
