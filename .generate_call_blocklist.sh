curl --header 'Accept: application/json' --header 'Authorization: Basic Y2RhbmQ6djFna3dpamhzbmdyZ29pNjh6c2Z3Mzh2' 'https://ws.cleverdialer.com/api/1.3/spam?region=ES' -v -o cleverdialer.json
jq .[].normalizedPhone -r cleverdialer.json > blocklist_unsorted.txt
sort blocklist_unsorted.txt > blocklist.txt