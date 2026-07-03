#!/bin/bash
set -e
B=/private/tmp/claude-501/-Users-hiroka-Public-claude--claude-worktrees-infallible-newton-8bd835/34789c15-930c-47c7-a879-72875b51ebf9/scratchpad/hoiku_data
curl -sL -A "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36" -o $B/aki_agents/gamagori/aki.pdf "https://www.city.gamagori.lg.jp/uploaded/attachment/117074.pdf"
file $B/aki_agents/gamagori/aki.pdf
