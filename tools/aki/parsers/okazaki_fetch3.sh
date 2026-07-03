#!/bin/bash
cd "$(dirname "$0")"
UA="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
echo "=== page.html size ==="
wc -c page.html
echo "=== all pdf/xls anywhere ==="
grep -oiE '[a-z0-9_./-]+\.(pdf|xlsx|xls)' page.html | sort -u
echo "=== any p028692_d ==="
grep -oE 'p028692_d[^" <]*' page.html | sort -u
echo "=== links containing waku ==="
grep -oiE 'waku[a-z0-9]*\.pdf' page.html | sort -u
