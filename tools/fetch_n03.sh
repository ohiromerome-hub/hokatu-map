#!/bin/bash
cd "$(dirname "$0")"
curl -s -o N03-2024_23.zip "https://nlftp.mlit.go.jp/ksj/gml/data/N03/N03-2024/N03-20240101_23_GML.zip"
unzip -o -q N03-2024_23.zip -d n03
find n03 -type f
echo DONE
