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
    
    # Extract summary stats
    awk '
        /workers \[[0-9]+ items\]/ {
            match($0, /\[([0-9]+) items\]/, items)
            total = items[1]
        }
        /^=+ .+ failed.*passed/ {
            match($0, /([0-9]+) failed, ([0-9]+) passed/, stats)
            failed = stats[1]
            passed = stats[2]
        }
        /stopping after [0-9]+ failures/ {
            match($0, /stopping after ([0-9]+) failures/, stop)
            stopped = stop[1]
        }
        END {
            if (total && failed && passed) {
                printf "%s total tests. Stopped after %s failures. %s failed, %s passed.\n\n", total, stopped ? stopped : failed, failed, passed
                printf "1st failure:\n\n"
            }
        }
    ' description="$description" "$tmp_file"
    
    # Extract and format first failure
    awk '
        /^_+ .+ _+$/ { 
            if (found) exit
            found = 1
            match($0, /_+ (.+) _+/, arr)
            test_name = arr[1]
            next
        }
        /^=+ short test summary/ { exit }
        /^\[gw[0-9]+\]/ { next }
        found && /^[^ ]/ && /:/ {
            match($0, /^([^:]+):([0-9]+):/, loc)
            file_path = loc[1]
            line_num = loc[2]
            getline
            getline
            match($0, /E   ([^:]+): (.+)$/, err)
            error_type = err[1]
            error_msg = err[2]
            
            # Remove path before src/ in parentheses
            gsub(/\([^)]*\/src\//, "(src/", error_msg)
            
            printf "%s (%s:%s) - %s: %s\n", test_name, file_path, line_num, error_type, error_msg
            exit
        }
    ' "$tmp_file"
    
    rm -f "$tmp_file"
    exit $exit_code
fi