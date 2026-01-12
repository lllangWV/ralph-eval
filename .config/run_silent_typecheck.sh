#!/usr/bin/env bash
set -euo pipefail

description="$1"
shift
command="$@"

tmp_file=$(mktemp)

if eval "$command" > "$tmp_file" 2>&1; then
    printf "  ✓ %s\n" "$description"
    rm -f "$tmp_file"
    exit 0
else
    exit_code=$?

    # Extract summary line (at end of output)
    summary=$(grep -E '^[0-9]+ errors?, [0-9]+ warnings?, [0-9]+ notes?$' "$tmp_file" || true)

    if [[ -n "$summary" ]]; then
        errors=$(echo "$summary" | sed -E 's/^([0-9]+) errors?.*/\1/')
        warnings=$(echo "$summary" | sed -E 's/.*[^0-9]([0-9]+) warnings?.*/\1/')
        notes=$(echo "$summary" | sed -E 's/.*[^0-9]([0-9]+) notes?$/\1/')

        # Extract first error with its continuation line
        first_error=$(awk '
            /^\s*\/.*:[0-9]+:[0-9]+ - error:/ {
                if (found_first == 0) {
                    found_first = 1
                    first_error = $0
                    next
                }
                if (found_first) {
                    print first_error
                    printed = 1
                    exit
                }
            }
            found_first && /^\s+[^\/]/ {
                first_error = first_error "\n" $0
                print first_error
                printed = 1
                exit
            }
            END {
                if (found_first && first_error && printed == 0) {
                    print first_error
                }
            }
        ' "$tmp_file")

        printf "  ✗ %s\n" "$description"
        printf "%s errors, %s warnings, %s notes. Only showing first error:\n" "$errors" "$warnings" "$notes"
        if [[ -n "$first_error" ]]; then
            echo "$first_error"
        fi
    else
        # No summary found, show raw output
        printf "  ✗ %s\n" "$description"
        cat "$tmp_file"
    fi

    rm -f "$tmp_file"
    exit $exit_code
fi