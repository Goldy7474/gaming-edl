import urllib.request
import json

ASNS = [
    "AS33353",  # Sony PlayStation
    "AS19425",  # Sony Network Entertainment
    "AS8075",   # Microsoft Corporation (Xbox Live / Azure)
    "AS32590",  # Valve / Steam
    "AS29813",  # EA (Electronic Arts)
    "AS6507",   # Riot Games
    "AS5797",   # Blizzard / Battle.net
    "AS32044"   # Epic Games
]

def fetch_asn_prefixes(asn):
    prefixes = set()
    # שימוש ב-RIPE Stat API היציב
    url = f"https://stat.ripe.net/data/announced-prefixes/data.json?resource={asn}"
    try:
        req = urllib.request.Request(
            url, 
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        )
        with urllib.request.urlopen(req, timeout=15) as response:
            data = json.loads(response.read().decode())
            prefixes_list = data.get('data', {}).get('prefixes', [])
            for item in prefixes_list:
                prefix = item.get('prefix')
                # סינון IPv4 בלבד (תומך בפורמט X.X.X.X/X)
                if prefix and ':' not in prefix:
                    prefixes.add(prefix)
    except Exception as e:
        print(f"Error fetching prefixes for {asn}: {e}")
    return prefixes

def main():
    all_ips = set()
    
    for asn in ASNS:
        print(f"Fetching IP ranges for {asn}...")
        prefixes = fetch_asn_prefixes(asn)
        print(f"  -> Found {len(prefixes)} IPv4 prefixes for {asn}")
        all_ips.update(prefixes)

    print(f"\nWriting total of {len(all_ips)} unique prefixes to gaming_ips.txt")
    with open("gaming_ips.txt", "w") as f:
        for ip in sorted(all_ips):
            f.write(f"{ip}\n")

if __name__ == "__main__":
    main()
