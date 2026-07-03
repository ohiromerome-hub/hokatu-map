#!/bin/bash
set -e
cd /private/tmp/claude-501/-Users-hiroka-Public-claude--claude-worktrees-infallible-newton-8bd835/34789c15-930c-47c7-a879-72875b51ebf9/scratchpad/hoiku_data/aki_agents/ichinomiya/
curl -sL -A "Mozilla/5.0" "https://www.city.ichinomiya.aichi.jp/kodomokatei/hoiku/1000155/1010629/1062184.html" -o page.html
echo "size: $(wc -c < page.html)"
