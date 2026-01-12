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
    
    # Extract error/warning/note counts and first error
    awk '
        /^[0-9]+ errors?, [0-9]+ warnings?, [0-9]+ notes?/ {
            match($0, /^([0-9]+) errors?, ([0-9]+) warnings?, ([0-9]+) notes?/, counts)
            errors = counts[1]
            warnings = counts[2]
            notes = counts[3]
        }
        /^\s*\/.*:[0-9]+:[0-9]+ - error:/ {
            if (!found_first) {
                found_first = 1
                first_error = $0
                # Peek at next line for continuation
                if (getline next_line > 0) {
                    if (next_line ~ /^\s+[^\/]/) {
                        first_error = first_error "\n" next_line
                    }
                }
            }
        }
        END {
            if (errors) {
                printf "  ✗ %s\n", ENVIRON["description"]
                printf "%s errors, %s warnings, %s notes. Only showing first error:\n", errors, warnings, notes
                if (first_error) {
                    print first_error
                }
            }
        }
    ' description="$description" "$tmp_file"
    
    rm -f "$tmp_file"
    exit $exit_code
fi