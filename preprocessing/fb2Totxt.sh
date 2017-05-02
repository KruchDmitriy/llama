#!/bin/sh

PATH_TO_DIR="$1"
OUT_FILE="$2"
DECODER_PATH="FB2_2_txt.xsl"

> "$OUT_FILE"

find "$PATH_TO_DIR" -name "*.fb2" -print0 |
    while IFS= read -r -d $'\0' line; do
        echo processing "$line"
        xsltproc "$DECODER_PATH" "$line" >> "$OUT_FILE"
    done
