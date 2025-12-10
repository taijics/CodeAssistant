# Evolutionary Prompt Manager (EPM) — 进化式 AI 代码助手中间件

本中间件在“人 ⇄ 大模型”之间接管上下文管理与策略优化：
- 强化学习记忆（错题本）：避免重复犯错
- 自动全局检索：函数/类/页面/后端/数据库表
- 结构化文档（Spec）+ 审核工作流
- LLM 生成代码 → 自动写回 → 反馈更新记忆

核心功能（匹配你的 5 点）
1) 强化学习记忆：每次失败原因记录到错题本，下次自动注入历史提醒
2) 自动检索：索引函数/类/SQL 表/框架文件，召回与任务相关的代码与资源
3) 文档组装与审核：生成“高信噪 Spec 文档”，人工审核→确认→提交 LLM
4) 自动写回：接收 LLM 返回的“文件块/补丁”，自动写入并可选 git commit
5) 迭代改进：人工测试后若有错误，记录反馈并回到第 1 步，持续强化

# Evolutionary Prompt Manager (EPM) — 进化式 AI 代码助手中间件

新增能力
- 项目管理界面（Web UI）
  - 多项目管理：每个项目独立设置根目录与配置
  - 一键：生成 Spec → 提交 LLM → 自动写回 → 查看记忆与产物
- 多线程检索（默认 10 线程）
  - 扫描/读取/分词计数并行化，适合几千文件大仓库

安装
- Python >= 3.9
- pip install -r requirements.txt
- 可选：pip install -r requirements-llm.txt （提交 LLM） / pip install -r requirements-vector.txt（向量检索）

命令
- 启动界面：evo-agent-ui
- 生成 Spec（多线程）：
  - evo-agent plan --project . --task "你的需求" --num-workers 10
- 提交到 LLM：
  - evo-agent submit --project . --spec artifacts/spec.md --provider openai --model gpt-4o
- 自动写回：
  - evo-agent apply --project . --resp artifacts/llm_response.txt --git-commit
- 反馈与记忆：
  - evo-agent feedback --project . --task "任务摘要" --result n --reason "失败原因"
  - evo-agent memory --project . --task "关键词"

Web UI 功能
- 新建项目：名称 + 根目录（绝对路径）
- 设定 per-project 配置：包含/排除、token 预算、线程数（默认10）
- 生成 Spec：后台执行扫描→索引→选择→压缩→组装，产物保存在 <project>/.evo_agent/artifacts/
- 提交 LLM：输入 provider/model，保存响应
- 应用变更：自动写回文件；可选 git commit
- 查看错题本记忆：与任务相关的历史提醒

注意
- 多线程读文件为 I/O 密集型，10 线程默认更快；如 CPU 忙于分词，可按机器性能调 8–16。
- 产物与错题本保存在项目内：<project>/.evo_agent/
安装
- Python >= 3.9
- 基础依赖：
  - pip install -r requirements.txt
- 可选（调用 LLM）：
  - pip install -r requirements-llm.txt
  - 设置 OPENAI_API_KEY 或 ANTHROPIC_API_KEY 等
- 可选（向量检索）：
  - pip install -r requirements-vector.txt

常用命令
- 生成计划文档（Spec）并人工审核
  - evo-agent plan --project <path> --task "你的需求"
  - 产物：artifacts/spec.md（包含：用户需求、历史提醒、检索结果、上下文片段）
- 提交给 LLM（审核通过后）
  - evo-agent submit --project <path> --spec artifacts/spec.md --provider openai --model gpt-4o
  - 产物：artifacts/llm_response.txt（应为“文件块”或“统一 diff”）
- 应用代码变更（自动写回）
  - evo-agent apply --project <path> --resp artifacts/llm_response.txt --git-commit
- 记录反馈（错题本）
  - evo-agent feedback --project <path> --task "任务摘要" --result n --reason "失败原因" --correction "修正建议(可选)"
- 查看与任务相关的历史提醒
  - evo-agent memory --project <path> --task "关键词"

LLM 输出要求（建议此格式，最稳）
以“文件块”返回完整文件内容，工具将自动写回：
```evoedit
FILE: relative/path/to/file.ext
<full file content>
===END===
```
也支持统一 diff 补丁（优先尝试系统 patch 命令；失败则跳过）。

可扩展
- 替换选择器为嵌入相似度（Chroma + OpenAI Embeddings）
- 在 Compressor 中改为语义摘要（小模型）
- 引入 DSPy 做 System Prompt 自动优化

许可证：MIT