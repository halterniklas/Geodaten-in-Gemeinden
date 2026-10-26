#!/usr/bin/env bash
# Stufe 3 (GitHub-Runner): statistik.bl.ch mit korrekter Zertifikatskette (fehlendes Zwischenzertifikat
# via AIA ergänzen, Verifikation bleibt aktiv) und baselland.ch mit Browser-Headern sondieren.
set -u
OUT="$1"; mkdir -p "$OUT"
UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
LOG="$OUT/probe3.log"; : > "$LOG"
host=statistik.bl.ch
openssl s_client -connect $host:443 -servername $host -showcerts </dev/null 2>/dev/null > "$OUT/bl_chain.txt"
awk '/BEGIN CERT/{n++} n>=1{print > "'"$OUT"'/bl_cert_" n ".pem"} /END CERT/{}' "$OUT/bl_chain.txt" || true
openssl x509 -in "$OUT/bl_cert_1.pem" -noout -subject -issuer -text 2>/dev/null | grep -E "Subject:|Issuer:|CA Issuers" >> "$LOG"
AIA=$(openssl x509 -in "$OUT/bl_cert_1.pem" -noout -text 2>/dev/null | grep -o 'CA Issuers - URI:[^ ]*' | head -1 | sed 's/CA Issuers - URI://')
echo "AIA=$AIA" >> "$LOG"
cp /etc/ssl/certs/ca-certificates.crt "$OUT/bundle.pem"
if [ -n "$AIA" ]; then
  curl -s -m 30 -o "$OUT/inter.cer" "$AIA"
  (openssl x509 -inform DER -in "$OUT/inter.cer" -outform PEM 2>/dev/null || cat "$OUT/inter.cer") >> "$OUT/bundle.pem"
fi
echo "--- statistik.bl.ch (verifiziert)" >> "$LOG"
curl -sS -m 60 --cacert "$OUT/bundle.pem" -A "$UA" -o "$OUT/bl_statistik_home.html" -w "%{http_code} %{size_download}\n" "https://statistik.bl.ch/" >> "$LOG" 2>&1
for u in "https://statistik.bl.ch/api" "https://statistik.bl.ch/sitemap.xml" "https://statistik.bl.ch/themen/gemeindefinanzen" \
         "https://www.baselland.ch/politik-und-behorden/gemeinden/gemeindefinanzen" \
         "https://www.baselland.ch/politik-und-behorden/direktionen/finanz-und-kirchendirektion/gemeindefinanzen" \
         "https://opendata.bl.ch/api/explore/v2.1/catalog/datasets?limit=100&where=search(%22Gemeindefinanzen%22)"; do
  n=$(echo "$u" | sed 's#[^A-Za-z0-9]#_#g' | cut -c1-80)
  echo "--- $u" >> "$LOG"
  curl -sS -m 60 --cacert "$OUT/bundle.pem" -L -A "$UA" -H "Accept: text/html,application/json;q=0.9,*/*;q=0.8" -H "Accept-Language: de-CH,de;q=0.9" \
       -o "$OUT/bl_$n.out" -w "%{http_code} %{size_download} %{url_effective}\n" "$u" >> "$LOG" 2>&1
done
cat "$LOG"
