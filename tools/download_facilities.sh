#!/bin/bash
# 国土数値情報 施設データ取得（学校P29=幼稚園・こども園 / 福祉施設P14=保育所）
cd "$(dirname "$0")"
dl() { curl -s -o "$2" "$1" && echo "OK $2 $(du -h "$2" | cut -f1)" || echo "FAIL $2"; }
dl "https://nlftp.mlit.go.jp/ksj/gml/data/P29/P29-23/P29-23_23_GML.zip" P29-23_23_GML.zip
dl "https://nlftp.mlit.go.jp/ksj/gml/data/P14/P14-21/P14-21_23_GML.zip" P14-21_23_GML.zip
unzip -o -q P29-23_23_GML.zip -d p29 && unzip -o -q P14-21_23_GML.zip -d p14
find p29 p14 -type f
echo ALL_DONE
