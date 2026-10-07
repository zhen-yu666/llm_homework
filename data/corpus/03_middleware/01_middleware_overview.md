# 中间件总览

> 来源：https://docs.langchain.com/oss/javascript/langchain/middleware/custom
> 抓取日期：2026-09-26
> 模块：03_middleware

## 钩子类型

中间件提供两种风格的钩子来拦截智能体执行。你可以选择节点式钩子和包装式钩子。

### 节点式钩子（Node-style hooks）

按顺序在特定执行点运行。用于日志记录、验证和状态更新。可用的钩子：

| 钩子 | 运行时机 |
|---|---|
| `beforeAgent` | 智能体启动之前（每次调用一次） |
| `beforeModel` | 每次模型调用之前 |
| `afterModel` | 每次模型响应之后 |
| `afterAgent` | 智能体完成之后（每次调用一次） |

```python
from langchain.agents.middleware import createMiddleware

createMessageLimitMiddleware = (maxMessages=50) => {
    return createMiddleware({
        name: "MessageLimitMiddleware",
        beforeModel: (state) => {
            if (state.messages.length === maxMessages) {
                return {
                    messages: [new AIMessage("Conversation limit reached.")],
                    jumpTo: "end"
                };
            }
        },
        afterModel: (state) => {
            const lastMessage = state.messages[state.messages.length - 1];
            console.log(`Model returned: ${lastMessage.content}`);
        }
    });
};
```

### 包装式钩子（Wrap-style hooks）

拦截执行并控制处理程序何时被调用。用于重试、缓存和转换。你决定处理程序被调用零次（短路）、一次（正常流程）或多次（重试逻辑）。可用的钩子：

| 钩子 | 运行时机 |
|---|---|
| `wrapModelCall` | 围绕每次模型调用 |
| `wrapToolCall` | 围绕每次工具调用 |

```python
from langchain.agents.middleware import createMiddleware

createRetryMiddleware = (maxRetries=3) => {
    return createMiddleware({
        name: "RetryMiddleware",
        wrapModelCall: (request, handler) => {
            for (let attempt = 0; attempt < maxRetries; attempt++) {
                try {
                    return handler(request);
                } catch (e) {
                    if (attempt === maxRetries - 1) throw e;
                    console.log(`Retry ${attempt + 1}/${maxRetries}`);
                }
            }
        }
    });
};
```

## 状态更新

节点式钩子和包装式钩子都可以更新智能体状态。机制不同：

- **节点式钩子**（`beforeAgent`、`beforeModel`、`afterModel`、`afterAgent`）：直接返回一个字典。该字典使用图的 reducers 应用于智能体状态。
- **包装式钩子**（`wrapModelCall`、`wrapToolCall`）：对于模型调用，直接返回一个 `Command` 以在模型响应之外注入状态更新。对于工具调用，直接返回一个 `Command`。

## 执行顺序

中间件的执行顺序为：`before_agent` → `before_model` → `[wrap_model_call]` → `after_model` → `[wrap_tool_call]` → `after_agent`。包装式钩子拦截并控制实际的模型或工具调用。