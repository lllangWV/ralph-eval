#!/bin/bash
# Simple context-managed headless loop
# Monitors context, kills session when threshold exceeded, runs cleanup commands, repeats

set -euo pipefail

SCRIPT_DIR="$(dirname "$0")"

# Configuration
MAX_CONTEXT_PERCENT="${MAX_CONTEXT_PERCENT:-75}"
CONTEXT_WINDOW="${CONTEXT_WINDOW:-200000}"
PROMPT_FILE="${PROMPT_FILE:-${SCRIPT_DIR}/PROMPT.md}"
CLEANUP_PROMPT="${CLEANUP_PROMPT:-${SCRIPT_DIR}/CLEANUP_PROMPT.md}"
MODEL="${MODEL:-sonnet}"

while true; do
    echo -e "\n======================== MAIN SESSION ========================\n"

    # Run Claude, split output: one stream to visualizer, one to context monitor
    cat "$PROMPT_FILE" | claude -p \
        --dangerously-skip-permissions \
        --output-format=stream-json \
        --model "$MODEL" \
        2>&1 | tee >(bunx repomirror visualize) | while IFS= read -r line; do

            # Check for usage data and extract context percentage
            if echo "$line" | grep -q '"usage"'; then
                total=$(echo "$line" | jq -r '
                    .usage // empty |
                    (.cache_read_input_tokens // 0) +
                    (.cache_creation_input_tokens // 0) +
                    (.input_tokens // 0)
                ' 2>/dev/null || echo 0)

                if [ "$total" -gt 0 ]; then
                    percent=$((total * 100 / CONTEXT_WINDOW))
                    echo "[MONITOR] Context: ${percent}% ($total tokens)" >&2

                    if [ "$percent" -gt "$MAX_CONTEXT_PERCENT" ]; then
                        echo "[MONITOR] Threshold exceeded! Breaking..." >&2
                        pkill -P $$ -f "claude -p" 2>/dev/null || true
                        break
                    fi
                fi
            fi
        done

    echo -e "\n======================== CLEANUP SESSION ========================\n"

    # Run cleanup prompt (handoff, commit, etc.)
    cat "$CLEANUP_PROMPT" | claude -p \
        --dangerously-skip-permissions \
        --output-format=stream-json \
        --model "$MODEL"

    git push origin main 2>/dev/null || true

    echo -e "\n======================== LOOP ========================\n"
done
