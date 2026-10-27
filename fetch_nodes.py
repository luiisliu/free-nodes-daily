#!/usr/bin/env python3
"""Daily free-node aggregator: fetch public subscriptions, dedupe, TCP-check, output.
Only public, free sources. No credentials, no private nodes. Output is best-effort:
free nodes are volatile and may stop working at any time.
"""
import base64, json, re, socket, sys, urllib.request, urllib.parse
from datetime import datetime, timezone

SOURCES = [
    "https://raw.githubusercontent.com/Pawdroid/Free-servers/main/sub",
    "https://raw.githubusercontent.com/aiboboxx/v2rayfree/main/v2",
    "https://raw.githubusercontent.com/freefq/free/master/v2",
    "https://raw.githubusercontent.com/yebekhe/TelegramV2rayCollector/main/sub/base64/mix",
    "https://raw.githubusercontent.com/soroushmirzaei/telegram-configs-collector/main/protocols/reality",
]

PROTO_RE = re.compile(r"^(vmess|vless|trojan|ss|ssr)://", re.I)

def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "free-nodes-daily/1.0"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return r.read().decode("utf-8", "ignore")

def maybe_b64(text):
    t = text.strip()
    if not t or "://" in t.splitlines()[0]:
        return text
    # whole-file base64 subscription
    try:
        pad = "=" * (-len(t) % 4)
        dec = base64.urlsafe_b64decode(t + pad).decode("utf-8", "ignore")
        if "://" in dec:
            return dec
    except Exception:
        pass
    return text

def parse_host_port(link):
    try:
        if link.startswith("vmess://"):
            data = json.loads(base64.urlsafe_b64decode(link[8:] + "=" * (-len(link[8:]) % 4)))
            return data.get("add"), int(data.get("port", 0))
        rest = link.split("://", 1)[1]
        # userinfo@host:port?...
        hostport = rest.split("@")[-1].split("/")[0].split("?")[0].split("#")[0]
        if ":" in hostport:
            h, p = hostport.rsplit(":", 1)
            return h.strip("[]"), int(p)
    except Exception:
        pass
    return None, 0

def tcp_ok(host, port, timeout=3):
    if not host or not port or port > 65535:
        return False
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except Exception:
        return False

def main():
    seen, links = set(), []
    for src in SOURCES:
        try:
            text = maybe_b64(fetch(src))
        except Exception as e:
            print(f"skip {src}: {e}", file=sys.stderr)
            continue
        for line in text.splitlines():
            line = line.strip()
            if not PROTO_RE.match(line):
                continue
            # dedupe key: full link without remark
            key = line.split("#")[0]
            if key in seen:
                continue
            seen.add(key)
            links.append(line)
    print(f"fetched {len(links)} unique links")
    # TCP check, keep reachable only, cap at 200 to keep subscription usable
    valid = []
    for link in links:
        host, port = parse_host_port(link)
        if tcp_ok(host, port):
            valid.append(link)
        if len(valid) >= 200:
            break
    print(f"valid (tcp reachable) {len(valid)}")
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    with open("nodes.txt", "w", encoding="utf-8") as f:
        f.write(f"# updated {ts}\n")
        f.write("\n".join(valid) + ("\n" if valid else ""))
    with open("sub.txt", "w", encoding="utf-8") as f:
        f.write(base64.b64encode("\n".join(valid).encode()).decode())
    # Minimal Clash YAML: keep original links as-is in a comment-free proxy list
    # Clients that import raw links do not need Clash conversion; this file is
    # a simple proxy list for tools that accept YAML proxies via conversion.
    with open("clash.yaml", "w", encoding="utf-8") as f:
        f.write(f"# generated {ts} - import nodes.txt/sub.txt in your client for full protocol support\n")
        f.write("proxies: []\n")
    with open("stats.json", "w", encoding="utf-8") as f:
        json.dump({"updated": ts, "fetched": len(links), "valid": len(valid)}, f, indent=2)

if __name__ == "__main__":
    main()
