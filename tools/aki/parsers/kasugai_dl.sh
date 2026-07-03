#!/bin/bash
set -e
BASE="/private/tmp/claude-501/-Users-hiroka-Public-claude--claude-worktrees-infallible-newton-8bd835/34789c15-930c-47c7-a879-72875b51ebf9/scratchpad/hoiku_data"
mkdir -p "$BASE/aki_agents/kasugai" "$BASE/aki_out"
cd "$BASE/aki_agents/kasugai"
curl -sL -A "Mozilla/5.0" -o R8.8enn.pdf "https://www.city.kasugai.lg.jp/_res/projects/default_project/_page_/001/026/096/R8.8enn.pdf"
ls -la
file R8.8enn.pdf
