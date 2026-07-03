#!/bin/bash
set -e
BASE="/private/tmp/claude-501/-Users-hiroka-Public-claude--claude-worktrees-infallible-newton-8bd835/34789c15-930c-47c7-a879-72875b51ebf9/scratchpad/hoiku_data"
mkdir -p "$BASE/aki_agents/seto" "$BASE/aki_out"
cd "$BASE/aki_agents/seto"
curl -sL -A "Mozilla/5.0" -o m-2.xls "https://www.city.seto.aichi.jp/docs/2025/04/13/00505309289/files/m-2.xls"
ls -la
file m-2.xls
