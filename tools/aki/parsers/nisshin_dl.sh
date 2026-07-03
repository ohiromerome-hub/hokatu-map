#!/bin/bash
cd "$(dirname "$0")"
curl -s -m 30 -o nisshin_aki.pdf "https://www.city.nisshin.lg.jp/material/files/group/120/R8_20260701_hoikuen.pdf"
ls -la nisshin_aki.pdf && file nisshin_aki.pdf
