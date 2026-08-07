import urllib.request
import json

# רשימת ASNs של פלטפורמות הגיימינג המובילות
ASNS = [
    "AS33353",  # Sony Interactive Entertainment (PlayStation)
    "AS19425",  # Sony Network Entertainment
    "AS8075",   # Microsoft Corporation (Xbox Live / Azure)
    "AS32590",  # Valve Corporation (Steam)
    "AS29813",  # Electronic Arts (EA)
    "AS6507",   # Riot Games
    "AS5797",   # Blizzard Entertainment (Battle.net)
    "AS32044"   # Epic Games
]

def fetch_asn_prefixes(asn):
    prefixes = set()
    url = f"https://api.bgpview.io/asn/{asn}/prefixes"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
            ipv4_prefixes = data.get('data', {}).get('ipv4_prefixes', [])
            for item in ipv4_prefixes:
                prefix = item.get('prefix')
                if prefix:
                    prefixes.add(prefix)
    except Exception as e:
        print(f"Error fetching prefixes for {asn}: {e}")
    return prefixes

def main():
    all_ips = set()
    
    for asn in ASNS:
        print(f"Fetching IP ranges for {asn}...")
        prefixes = fetch_asn_prefixes(asn)
        all_ips.update(prefixes)

    # שמירת כל ה-IPs המאוחדים לקובץ טקסט אחד
    with open("gaming_ips.txt", "w") as f:
        for ip in sorted(all_ips):
            f.write(f"{ip}\n")
            
    print(f"Total prefixes fetched for Gaming EDL: {len(all_ips)}")

if __name__ == "__main__":
    main()
