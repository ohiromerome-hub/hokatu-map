#!/bin/bash
# 豊田市 こども園等 空き状況・申込状況一覧表 PDF取得（Hiroka指示の空き状況パイロット）
cd "$(dirname "$0")"
curl -s -o toyota_aki_r0808.pdf "https://www.city.toyota.aichi.jp/_res/projects/default_project/_page_/001/016/130/r0808.pdf"
ls -la toyota_aki_r0808.pdf
file toyota_aki_r0808.pdf
