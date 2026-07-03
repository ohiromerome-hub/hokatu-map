#!/bin/bash
cd "$(dirname "$0")"
curl -s -m 30 "https://kodomokosodate.city.nagoya.jp/firstuse/boshuwaku.html" -o nagoya_boshuwaku.html
echo "page: $(wc -c < nagoya_boshuwaku.html)"
grep -oE 'href="[^"]*\.pdf"[^>]*>[^<]{0,70}' nagoya_boshuwaku.html | head -10
grep -oE '(令和|20[0-9]{2})[^<>]{0,30}(時点|現在|更新)' nagoya_boshuwaku.html | head -5
curl -s -m 60 -o nagoya16.pdf "https://kodomokosodate.city.nagoya.jp/fs/1/5/2/0/_/16______7_3___8_.pdf"
ls -la nagoya16.pdf && file nagoya16.pdf
