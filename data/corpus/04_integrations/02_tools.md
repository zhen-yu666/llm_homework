# 工具

> 来源：https://docs.langchain.com/oss/python/langchain/tools
> 抓取日期：2026-09-26
> 模块：04_integrations

## 概述

工具扩展智能体的能力——让它们获取实时数据、执行代码、查询外部数据库，并在世界上采取行动。在底层，工具是具有明确定义的输入和输出的可调用函数，传递给聊天模型。模型根据对话上下文决定何时调用工具以及提供什么输入参数。

## 使用 @tool 装饰器创建工具

创建工具的最简单方式是使用 `@tool` 装饰器。默认情况下，函数的 docstring 成为工具的描述，帮助模型理解何时使用它。类型提示是必需的，因为它们定义了工具的输入模式。

```python
from langchain.tools import tool

@tool
def search_database(query: str, limit: int = 10) -> str:
    """Search the customer database for records matching the query.
    
    Args:
        query: Search terms to look for
        limit: Maximum number of results to return
    """
    return f"Found {limit} results for '{query}'"
```

## 工具命名最佳实践

偏好使用 snake_case 命名工具（如 `web_search` 而不是 `Web Search`）。一些模型提供商对包含空格或特殊字符的名称有兼容性问题。坚持使用字母数字字符、下划线和连字符有助于提高跨提供商的兼容性。

## 自定义工具属性

### 自定义工具名称

默认情况下，工具名称来自函数名。当需要更具描述性的名称时可以覆盖：

```python
@tool("web_search")  # 自定义名称
def search(query: str) -> str:
    """Search the web for information."""
    return f"Results for: {query}"

print(search.name)  # web_search
```

### 自定义工具描述

覆盖自动生成的工具描述，为模型提供更清晰的指导：

```python
@tool("calculator", description="Performs arithmetic calculations. Use this for any math problems.")
def calc(expression: str) -> str:
    """Evaluate mathematical expressions."""
    return str(eval(expression))
```

## 高级模式定义

使用 Pydantic 模型或 JSON 模式定义复杂输入：

```python
from pydantic import BaseModel, Field
from typing import Literal

class WeatherInput(BaseModel):
    """Input for weather queries."""
    location: str = Field(description="City name or coordinates")
    units: Literal["celsius", "fahrenheit"] = Field(
        default="celsius",
        description="Temperature unit preference"
    )
    include_forecast: bool = Field(
        default=False,
        description="Include 5-day forecast"
    )

@tool(args_schema=WeatherInput)
def get_weather(location: str, units: str = "celsius", include_forecast: bool = False) -> str:
    """Get current weather and forecast."""
    ...
```