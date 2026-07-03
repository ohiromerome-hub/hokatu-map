#!/bin/bash
cd "$(dirname "$0")"
curl -sL -A "Mozilla/5.0" "https://www.city.hekinan.lg.jp/soshiki/kodomo_kenkou/hoikuka/hoikuen/8254.html" -o page.html
echo "saved: $(wc -c < page.html) bytes"
