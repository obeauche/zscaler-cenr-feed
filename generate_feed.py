#!/usr/bin/env python3
"""Regenerates the flat domain/CIDR feed for the GL.iNet router's
"Subscription URL" split-tunnel exclusion rule.

Pulls Zscaler's published Cloud Enforcement Node Ranges (CENR) for the
zscalertwo.net and zscalerthree.net clouds, aggregates the IPv4 ranges into
the smallest lossless set of CIDR blocks, and combines them with a static
list of ZCC/ZPA control-plane domains that are DNS-resolved (and so can't be
captured by the IP-range feed alone).
"""
import ipaddress
import json
import sys
import urllib.request

CLOUDS = ["zscalertwo.net", "zscalerthree.net"]

# ZPA control-plane / ZCC discovery domains -- these are DNS-resolved at
# connection time, unlike the ZIA ZEN tunnel which uses pushed IPs directly,
# so they can't be derived from the CENR IP data and must be listed here.
STATIC_DOMAINS = [
    "zscalertwo.net",
    "zscalerthree.net",
    "prod.zpath.net",
    "prod.zpath.vip",
    "private.zscaler.com",
    "mobile.zscaler.net",
    "pac.zscaler.net",
    "gateway.zscaler.net",
    "mobilesupport.zscaler.com",
    "clients4.google.com",
    "zcc.ecdn.zscaler.com",
    "healthapp.ecdn.zscaler.com",
]


def fetch_cenr(cloud):
    url = f"https://config.zscaler.com/api/{cloud}/cenr/json"
    with urllib.request.urlopen(url, timeout=30) as resp:
        return json.load(resp)


def collect_v4_ranges(data, cloud):
    v4 = set()
    for _continent, cities in data[cloud].items():
        for _city, entries in cities.items():
            for e in entries:
                r = e.get("range", "")
                if r and ":" not in r:
                    v4.add(r)
    return v4


def main():
    all_ranges = set()
    for cloud in CLOUDS:
        try:
            data = fetch_cenr(cloud)
        except Exception as exc:
            print(f"WARNING: failed to fetch {cloud}: {exc}", file=sys.stderr)
            continue
        all_ranges |= collect_v4_ranges(data, cloud)

    if not all_ranges:
        print("ERROR: no ranges fetched from any cloud, aborting", file=sys.stderr)
        sys.exit(1)

    nets = [ipaddress.ip_network(r, strict=False) for r in all_ranges]
    collapsed = sorted(
        ipaddress.collapse_addresses(nets),
        key=lambda n: (-n.num_addresses, str(n)),
    )

    lines = list(STATIC_DOMAINS) + [str(n) for n in collapsed]

    with open("feed.txt", "w") as f:
        f.write("\n".join(lines) + "\n")

    print(f"Wrote {len(STATIC_DOMAINS)} domains + {len(collapsed)} CIDR blocks "
          f"({len(lines)} total lines) to feed.txt")


if __name__ == "__main__":
    main()
