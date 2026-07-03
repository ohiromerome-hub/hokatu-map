#!/bin/bash
set -e
cd "$(dirname "$0")"
UA="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
curl -s -A "$UA" "https://www.city.okazaki.lg.jp/1100/1104/1132/p028692.html" -o page.html
echo "=== links in p028692 ==="
grep -oE 'href="[^"]*\.(pdf|xlsx|xls)"' page.html | sort -u
