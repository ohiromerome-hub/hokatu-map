#!/bin/bash
cd "$(dirname "$0")"
curl -sL -A "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)" \
  "https://www.city.konan.lg.jp/kurashi/1009685/1011199/1003360/1003398.html" \
  -o page.html
echo "size: $(wc -c < page.html)"
