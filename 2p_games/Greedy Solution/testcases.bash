#!/bin/bash

for file in ../testcases/input*.txt; do
    output_file="${file/input/output}"
    res1="$(cat $output_file)"
    res2="$(python3 Optimized_Solution.py < $file)"
    if [[ $res1 != $res2 ]]; then
        echo "Test failed for input file: $file"
        echo "Expected: $res1"
        echo "Got: $res2"
    fi
done