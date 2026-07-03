#!/bin/bash
cd /private/tmp/claude-501/-Users-hiroka-Public-claude--claude-worktrees-infallible-newton-8bd835/34789c15-930c-47c7-a879-72875b51ebf9/scratchpad/hoiku_data/aki_agents/okazaki/
UA="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
curl -sL -A "$UA" "https://www.city.okazaki.lg.jp/_res/projects/default_project/_page_/001/003/640/20260801akijoukyou.pdf" -o aki_202608.pdf -w "http=%{http_code} size=%{size_download}\n"
file aki_202608.pdf
