# zscaler-cenr-feed

Auto-updated flat domain/CIDR feed for a GL.iNet travel router's split-tunnel
exclusion rule, so Zscaler Client Connector (ZCC) traffic bypasses a
WireGuard backhaul tunnel instead of riding it unnecessarily.

- `generate_feed.py` pulls Zscaler's published Cloud Enforcement Node Ranges
  (CENR) for the `zscalertwo.net` and `zscalerthree.net` clouds, aggregates
  the IPv4 ranges into the smallest lossless set of CIDR blocks, and combines
  them with a static list of DNS-resolved ZCC/ZPA control-plane domains.
- A daily GitHub Action (`.github/workflows/update-feed.yml`) regenerates
  `feed.txt` and commits it if Zscaler's published ranges changed.
- The router fetches the raw file directly via its "Subscription URL" mode
  and refreshes on its own schedule.

Content is entirely derived from Zscaler's own public, unauthenticated API
(`config.zscaler.com/api/<cloud>/cenr/json`) — nothing here is specific to
any tenant or private configuration.
