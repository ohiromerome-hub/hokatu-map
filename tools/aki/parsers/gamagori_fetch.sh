#!/bin/bash
UA="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
curl -sL -A "$UA" "https://www.city.gamagori.lg.jp/site/subsite-kosodate/nyuuennkizyun.html" -o page.html
echo "=== PDF/Excel links with context ==="
grep -oE 'href="[^"]*\.(pdf|xls|xlsx)"' page.html
echo "=== lines mentioning 空き ==="
grep -oE '.{0,40}空き.{0,60}' page.html | head -40
