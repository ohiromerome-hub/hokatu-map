#!/bin/bash
set -e
cd "$(dirname "$0")"
UA="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
echo "=== all hrefs with fil/ or kouhyou or waku in p028692 ==="
grep -oE 'href="[^"]*"' page.html | grep -iE 'fil/|kouhyou|waku|p028692_d' | sort -u
echo "=== body text mentions of 空き/入園月 ==="
grep -oE '令和[0-9]+年[0-9]+月[^<]{0,20}' page.html | sort -u | head -40
