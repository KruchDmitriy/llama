#! /bin/bash

PATH_TO_DIR="$1"
OUT_FILE="$2"

touch "$OUT_FILE"
> "$OUT_FILE"

tmpfile=$(mktemp /tmp/XXXXX.txt)

find "$PATH_TO_DIR" -name "*.pdf" -print0 |
    while IFS= read -r -d $'\0' line; do
        echo processing "$line"
        pdftotext "$line" "$tmpfile"

        cat "$tmpfile" >> "$OUT_FILE"
    done

rm "$tmpfile"