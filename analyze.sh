#!/bin/sh

rm -fr output/
python3 -m pg_analyze.main -r problems -o output/
echo ""
wc -l $(find output/ -type f) | sort -n | tail -n 8
echo ""
wc -l $(find output/ -type f -name "*.tsv") | sort -n | tail -n 8
echo ""
wc -l $(find output/ -type f -name "*.txt") | sort -n | tail -n 8
