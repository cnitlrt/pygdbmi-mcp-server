# pygdbmi-mcp-server

[English](README_EN.md) | 中文

这是一个基于 [pygdbmi](https://github.com/cs01/pygdbmi) 开发的 MCP (Model Context Protocol) 服务器，旨在通过 MCP 协议调用 GDB 进行动态调试。

本项目部分代码参考自 [pwnomcp](https://github.com/pwno-io/pwno-mcp)。

## 功能特性

本服务器提供了一系列 MCP 工具，用于与 GDB 进行交互：

### 调试控制
- `execute`: 执行任意 GDB/pwndbg 命令。
- `run`: 运行加载的二进制文件。
- `interrupt`: 中断正在运行的程序。
- `finish`: 运行直到当前函数返回。
- `step_control`: 执行步进命令 (continue, next, step, nexti, stepi)。

### 远程调试
- `target_remote`: 连接到远程调试目标 (如 gdbserver)。
- `disconnect`: 断开远程连接。


### 文件与会话管理
- `set_file`: 加载用于调试的二进制文件。
- `set_poc_file`: 设置 PoC 文件 (通过 `set args` 传递给二进制文件)。
- `get_session_info`: 获取当前调试会话信息。

### 断点管理
- `set_breakpoint`: 在指定位置设置断点。
- `list_breakpoints`: 列出所有断点。
- `delete_breakpoint`: 按编号删除断点。
- `toggle_breakpoint`: 切换断点的启用/禁用状态。

### 状态检查
- `get_context`: 获取调试上下文 (寄存器, 堆栈, 反汇编, 代码, 回溯)。
- `get_memory`: 读取指定地址的内存。
- `disassemble`: 反汇编指定地址。

## 安装与使用

### 1. 克隆仓库

```bash
git clone https://github.com/cnitlrt/pygdbmi-mcp-server
cd pygdbmi-mcp-server
```

### 2. 配置环境

在项目根目录下创建或修改 `.env` 文件，配置服务器监听地址和传输模式：

```bash
PORT=1111
HOST="0.0.0.0"
# TRANSPORT 可选 "sse" (Server-Sent Events) 或 "stdio" (标准输入输出)
# 若未设置，服务器会在非交互式 stdin（例如 Codex MCP）下自动选择 stdio
TRANSPORT="sse"
```

### 3. 安装依赖

本项目推荐使用 `uv` 进行依赖管理和环境配置。

```bash
# 创建虚拟环境 (建议使用 Python 3.13 或更高版本)
uv venv --python 3.13

# 激活虚拟环境 (Linux/macOS)
source .venv/bin/activate
# Windows
# .venv\Scripts\activate

# 安装项目及其依赖
uv pip install -e .
```

### 4. 运行服务器

```bash
uv run pygdbmi-mcp-server
```

也可以通过参数指定传输模式：

```bash
uv run pygdbmi-mcp-server --transport streamable-http
uv run pygdbmi-mcp-server --transport stdio
```

#### 远程连接（SSE/HTTP）

让服务器监听公网/局域网地址并使用 SSE：

```bash
uv run pygdbmi-mcp-server --transport sse --host 0.0.0.0 --port 1111
```

默认 SSE 端点为 `/sse`，消息端点为 `/messages/`，因此远程地址通常是：

```
http://<服务器IP>:1111/sse
http://<server-ip>:1111/mcp
```

### 5. 远程调试示例

使用 `target_remote` 连接到 gdbserver 进行远程调试：

```bash
# 在远程机器或另一个终端启动 gdbserver
gdbserver localhost:1234 /path/to/binary

# 通过 MCP 工具进行调试：
# 1. 使用 set_file 加载符号文件（与远程二进制相同）
# 2. 使用 target_remote 连接到 gdbserver
#    示例: target_remote("localhost:1234")
# 3. 使用 set_breakpoint 设置断点
# 4. 使用 step_control("continue") 继续执行
# 5. 使用 disconnect 断开连接
```

远程调试特别适用于：
- 嵌入式系统调试
- 内核模块调试
- 跨平台调试
- Docker 容器内程序调试
