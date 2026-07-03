#!/bin/bash
set -e
cd "/private/tmp/claude-501/-Users-hiroka-Public-claude--claude-worktrees-infallible-newton-8bd835/34789c15-930c-47c7-a879-72875b51ebf9/scratchpad/hoiku_data/aki_agents/anjo"
curl -sSL -A "Mozilla/5.0" -o anjo_202607.pdf "https://www.city.anjo.aichi.jp/kurasu/kosodate/hoikuen/documents/202607akijyoukyou2.pdf"
file anjo_202607.pdf
ls -la anjo_202607.pdf
