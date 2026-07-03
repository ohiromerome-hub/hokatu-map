#!/bin/bash
cd /private/tmp/claude-501/-Users-hiroka-Public-claude--claude-worktrees-infallible-newton-8bd835/34789c15-930c-47c7-a879-72875b51ebf9/scratchpad/hoiku_data/aki_agents/toyohashi/
UA="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
echo "=== 58151 ==="
curl -sL -A "$UA" "https://www.city.toyohashi.lg.jp/58151.htm" -o p58151.html -w "%{http_code}\n"
echo "=== 124099 ==="
curl -sL -A "$UA" "https://www.city.toyohashi.lg.jp/item/124099.htm" -o p124099.html -w "%{http_code}\n"
ls -la
