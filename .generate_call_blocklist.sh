curl --header 'Accept: application/json' --header 'Authorization: Basic Y2RhbmQ6djFna3dpamhzbmdyZ29pNjh6c2Z3Mzh2' 'https://ws.cleverdialer.com/api/1.3/spam?region=ES' -v -o cleverdialer.json
jq .[].normalizedPhone -r cleverdialer.json > blocklist_unsorted.txt
sort blocklist_unsorted.txt > blocklist.txt

curl -LOJ 'http://download.shouldianswer.net/download/shouldianswer_obsolete.apk' && unzip -n shouldianswer_obsolete.apk -d /tmp/apk && cp --no-clobber /tmp/apk/assets/data_slice_*.dat . # https://web.archive.org/web/20211003104644if_/http://download.shouldianswer.net/download/shouldianswer_obsolete.apk
curl --compressed -o data_slice_downloaded_update.bin.gz 'https://srv1.shouldianswer.net/srv2/get-database2?v=6&appver=11014&dbver=1381' && gunzip --force data_slice_downloaded_update.bin.gz

python --version

shouldianswer.py .

echo end--