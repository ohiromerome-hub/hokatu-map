#!/bin/bash
set -e
BASE="/private/tmp/claude-501/-Users-hiroka-Public-claude--claude-worktrees-infallible-newton-8bd835/34789c15-930c-47c7-a879-72875b51ebf9/scratchpad/hoiku_data"
mkdir -p "$BASE/aki_agents/handa" "$BASE/aki_out"
cd "$BASE/aki_agents/handa"
curl -sL -A "Mozilla/5.0" "https://www.city.handa.lg.jp/kosodate/hoikuen-youchien/1002100/1010914.html" -o page.html
wc -c page.html
