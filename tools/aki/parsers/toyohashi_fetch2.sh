#!/bin/bash
cd /private/tmp/claude-501/-Users-hiroka-Public-claude--claude-worktrees-infallible-newton-8bd835/34789c15-930c-47c7-a879-72875b51ebf9/scratchpad/hoiku_data/aki_agents/toyohashi/
UA="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
for id in 124574 124099; do
  echo "=== $id ==="
  curl -s -A "$UA" -H "Accept: text/html,application/xhtml+xml" -H "Accept-Language: ja,en" \
    "https://www.city.toyohashi.lg.jp/item/${id}.htm" -o "item_${id}.html" -w "http=%{http_code} size=%{size_download}\n"
done
echo "=== links in item_124574 (secure/pdf) ==="
grep -oE 'href="[^"]*"' item_124574.html 2>/dev/null | grep -iE 'secure|\.pdf|\.xls' | sort -u
echo "=== title ==="; grep -o '<title>[^<]*</title>' item_124574.html