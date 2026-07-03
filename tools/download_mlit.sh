#!/bin/bash
# 国土数値情報（国交省）オープンデータ取得 — Hiroka承認済み 2026-07-02
cd "$(dirname "$0")"
dl() { curl -s -o "$2" "$1" && echo "OK $2 $(du -h "$2" | cut -f1)" || echo "FAIL $2"; }
dl "https://nlftp.mlit.go.jp/ksj/gml/data/N02/N02-23/N02-23_GML.zip" N02-23_GML.zip
dl "https://nlftp.mlit.go.jp/ksj/gml/data/P11/P11-22/P11-22_23_GML.zip" P11-22_23_GML.zip
dl "https://nlftp.mlit.go.jp/ksj/gml/data/N07/N07-22/N07-22_23_GML.zip" N07-22_23_GML.zip
echo ALL_DONE
