import sys
import json
import ipaddress
import urllib.request

# ASNs רשמיים של פלטפורמות המשחקים המובילות
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

OUTPUT_FILE = "gaming_ips.txt"
MINIMUM_EXPECTED_PREFIXES = 20  # סף מינימלי להגנה מפני קובץ ריק / כשל תקשורת

def fetch_asn_prefixes(asn):
    valid_prefixes = set()
    url = f"https://stat.ripe.net/data/announced-prefixes/data.json?resource={asn}"
    
    try:
        req = urllib.request.Request(
            url, 
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        )
        # Timeout מוגדר למניעת תקיעת ה-Runner
        with urllib.request.urlopen(req, timeout=15) as response:
            data = json.loads(response.read().decode('utf-8'))
            prefixes_list = data.get('data', {}).get('prefixes', [])
            
            for item in prefixes_list:
                prefix = item.get('prefix')
                if not prefix or ':' in prefix:  # סינון IPv6
                    continue
                
                try:
                    # 1. נרמול ואימות CIDR תקין עבור Palo Alto (מונע כשל שורות ב-PAN-OS)
                    net_obj = ipaddress.ip_network(prefix, strict=False)
                    
                    # 2. סינון כתובות פרטיות, Loopback או Unspecified (RFC 1918)
                    if not (net_obj.is_private or net_obj.is_loopback or net_obj.is_unspecified):
                        valid_prefixes.add(str(net_obj))
                    else:
                        print(f"[WARN] Ignored private network for {asn}: {prefix}", file=sys.stderr)
                except ValueError:
                    print(f"[WARN] Ignored malformed prefix for {asn}: {prefix}", file=sys.stderr)
                    continue

    except Exception as e:
        print(f"[ERROR] Error fetching prefixes for {asn}: {e}", file=sys.stderr)
        
    return valid_prefixes

def main():
    print("[INFO] Starting Gaming IP prefixes retrieval via RIPE Stat...")
    all_ips = set()
    
    for asn in ASNS:
        print(f"[INFO] Fetching IP ranges for {asn}...")
        prefixes = fetch_asn_prefixes(asn)
        print(f"  -> Found {len(prefixes)} valid IPv4 prefixes for {asn}")
        all_ips.update(prefixes)

    # 3. מנגנון Fail-Safe: הכשלת הריצה אם נאספו פחות מהסף הצפוי
    if len(all_ips) < MINIMUM_EXPECTED_PREFIXES:
        print(f"[CRITICAL] Only {len(all_ips)} prefixes retrieved. Expected at least {MINIMUM_EXPECTED_PREFIXES}.", file=sys.stderr)
        print("[CRITICAL] Aborting file write to protect existing Palo Alto EDL.", file=sys.stderr)
        sys.exit(1)  # הכשלת ה-Action למניעת Commit של קובץ ריק או פגום

    # 4. כתיבה ממוינת ונקייה לקובץ הטקסט
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for ip in sorted(all_ips):
            f.write(f"{ip}\n")
            
    print(f"[SUCCESS] Successfully updated {OUTPUT_FILE} with {len(all_ips)} unique prefixes.")

if __name__ == "__main__":
    main()
