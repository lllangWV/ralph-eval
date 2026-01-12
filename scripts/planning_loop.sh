while true; do
    cat scripts/PLANNING_PROMPT.md | claude -p \
        --dangerously-skip-permissions \
        --output-format=stream-json \
        --model opus \
        --verbose \
        | bunx repomirror visualize
    git push origin launch-1
    echo -n "\n\n========================LOOP=========================\n\n"
done