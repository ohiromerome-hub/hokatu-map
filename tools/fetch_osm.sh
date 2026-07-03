#!/bin/bash
# OSM Overpass APIから愛知県の保育施設(kindergarten/childcare)を取得
cd "$(dirname "$0")"
cat > osm_query.txt <<'EOF'
[out:json][timeout:90];
area["name"="愛知県"]["admin_level"="4"]->.a;
nwr(area.a)["amenity"~"^(kindergarten|childcare)$"];
out center tags;
EOF
curl -s -X POST -d @osm_query.txt "https://overpass-api.de/api/interpreter" -o osm_hoiku.json
python3 -c "
import json
d=json.load(open('osm_hoiku.json'))
print('elements:', len(d.get('elements',[])))
"
echo DONE
