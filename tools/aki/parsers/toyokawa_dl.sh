#!/bin/bash
set -e
BASE="/private/tmp/claude-501/-Users-hiroka-Public-claude--claude-worktrees-infallible-newton-8bd835/34789c15-930c-47c7-a879-72875b51ebf9/scratchpad/hoiku_data"
mkdir -p "$BASE/aki_agents/toyokawa" "$BASE/aki_out"
cd "$BASE/aki_agents/toyokawa"
curl -sL -o akizyoukyou.pdf "https://www.city.toyokawa.lg.jp/material/files/group/20/20260624akizyoukyou.pdf"
ls -la
file akizyoukyou.pdf
