#!/bin/bash
B=/private/tmp/claude-501/-Users-hiroka-Public-claude--claude-worktrees-infallible-newton-8bd835/34789c15-930c-47c7-a879-72875b51ebf9/scratchpad/hoiku_data/aki_agents/seto
UA="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
# Google site search won't work via curl reliably; try the city's own search and likely pages
curl -sL -A "$UA" "https://www.city.seto.aichi.jp/docs/2imu0000001a2ie/" -o $B/seto_try1.html
curl -sL -A "$UA" "https://www.city.seto.aichi.jp/kosodate/" -o $B/seto_kosodate.html
curl -sL -A "$UA" "https://www.city.seto.aichi.jp/cgi-bin/search/search.cgi?query=%E4%BF%9D%E8%82%B2%E5%9C%92%20%E7%A9%BA%E3%81%8D%E7%8A%B6%E6%B3%81" -o $B/seto_search.html
for f in seto_try1 seto_kosodate seto_search; do echo "== $f =="; wc -c $B/$f.html; done
