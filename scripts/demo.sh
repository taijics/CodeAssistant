#!/usr/bin/env bash
set -euo pipefail

PROJECT=${1:-.}
TASK=${2:-"为登录添加刷新 token，后端 Flask，前端 React，DB MySQL"}

evo-agent plan --project "$PROJECT" --task "$TASK" --output artifacts/spec.md
echo "Review artifacts/spec.md, then submit:"
echo "evo-agent submit --project \"$PROJECT\" --spec artifacts/spec.md --provider openai --model gpt-4o"
echo "Then apply:"
echo "evo-agent apply --project \"$PROJECT\" --resp artifacts/llm_response.txt --git-commit"