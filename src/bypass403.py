#!/usr/bin/env python3
import argparse
import requests
import random
import time
import csv
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from itertools import cycle
from requests.exceptions import RequestException
from colorama import Fore, Style, init
init(autoreset=True)
def load_list(path):
    if not path:
        return []
    with open(path, "r", encoding="utf-8") as f:
        return [l.strip() for l in f if l.strip() and not l.startswith("#")]
def rand_ip():
    return f"172.{random.randint(16,31)}.{random.randint(0,255)}.{random.randint(1,254)}"
def build_headers(ua):
    return {
        "User-Agent": ua,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Referer": "https://www.google.com/",
        "X-Forwarded-For": rand_ip(),
        "X-Real-IP": rand_ip()
    }
def attempt_variations(url, session, headers, proxy, timeout):
    try:
        r = session.get(url, headers=headers, proxies=proxy, timeout=timeout, allow_redirects=True, verify=True)
        status = r.status_code
        if status != 403 and status < 400:
            return status, "GET", None
        if status == 403:
            r2 = session.head(url, headers=headers, proxies=proxy, timeout=timeout, allow_redirects=False, verify=True)
            if r2.status_code != 403 and r2.status_code < 400:
                return r2.status_code, "HEAD", None
            url_s = url.rstrip("/") + "/"
            r3 = session.get(url_s, headers=headers, proxies=proxy, timeout=timeout, allow_redirects=True, verify=True)
            if r3.status_code != 403 and r3.status_code < 400:
                return r3.status_code, "GET+slash", None
            headers_alt = dict(headers)
            headers_alt["Host"] = headers.get("Host", "")
            r4 = session.get(url, headers=headers_alt, proxies=proxy, timeout=timeout, allow_redirects=False, verify=True)
            if r4.status_code != 403 and r4.status_code < 400:
                return r4.status_code, "GET+HostAlt", None
        return status, "NO_BYPASS", None
    except RequestException as e:
        return None, "ERROR", str(e)
def worker(domain, ua_list, proxy_cycle, timeout, delay_min, delay_max, session):
    url = domain if domain.startswith("http") else f"https://{domain}"
    ua = random.choice(ua_list) if ua_list else requests.utils.default_headers()["User-Agent"]
    headers = build_headers(ua)
    proxy = None
    if proxy_cycle:
        p = next(proxy_cycle)
        proxy = {"http": p, "https": p}
    status, method, error = attempt_variations(url, session, headers, proxy, timeout)
    time.sleep(random.uniform(delay_min, delay_max))
    return {
        "domain": domain,
        "url": url,
        "status": status,
        "method": method,
        "user_agent": ua,
        "proxy": proxy["http"] if proxy else None,
        "error": error
    }
def main():
    parser = argparse.ArgumentParser(prog="403Hunter", description="Authorized testing only. Use only on targets you own or have explicit permission to test.")
    parser.add_argument("-d", "--domains", required=True, help="file with domains (one per line)")
    parser.add_argument("-u", "--ua", help="file with user-agents")
    parser.add_argument("-p", "--proxies", help="file with proxies ip:port")
    parser.add_argument("-o", "--outdir", default="out", help="output directory")
    parser.add_argument("-t", "--threads", type=int, default=10, help="concurrent threads")
    parser.add_argument("--timeout", type=int, default=10, help="request timeout seconds")
    parser.add_argument("--delay-min", type=float, default=1.0, help="min delay between requests")
    parser.add_argument("--delay-max", type=float, default=2.5, help="max delay between requests")
    parser.add_argument("--no-ssl-verify", action="store_true", help="disable SSL verification")
    parser.add_argument("--verbose", action="store_true", help="verbose output")
    args = parser.parse_args()
    doms = load_list(args.domains)
    ua_list = load_list(args.ua) if args.ua else []
    proxies = load_list(args.proxies) if args.proxies else []
    proxy_cycle = cycle(proxies) if proxies else None
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    results_csv = outdir / "results.csv"
    results_json = outdir / "results.json"
    session = requests.Session()
    if args.no_ssl_verify:
        session.verify = False
    all_results = []
    with ThreadPoolExecutor(max_workers=args.threads) as ex:
        futures = {ex.submit(worker, d, ua_list, proxy_cycle, args.timeout, args.delay_min, args.delay_max, session): d for d in doms}
        for fut in as_completed(futures):
            res = fut.result()
            all_results.append(res)
            status = res["status"]
            if status and status < 400 and status != 403:
                print(Fore.GREEN + f"[{status}] {res['domain']} -> {res['method']} UA={res['user_agent'][:40]} Proxy={res['proxy']}")
            elif status == 403:
                print(Fore.YELLOW + f"[403] {res['domain']} still forbidden UA={res['user_agent'][:40]} Proxy={res['proxy']}")
            elif status is None:
                print(Fore.RED + f"[ERR] {res['domain']} error={res['error']}")
            else:
                print(Fore.RED + f"[{status}] {res['domain']} no bypass")
            if args.verbose:
                print(Style.DIM + json.dumps(res, ensure_ascii=False))
    with open(results_csv, "w", newline="", encoding="utf-8") as csvf:
        writer = csv.DictWriter(csvf, fieldnames=["domain","url","status","method","user_agent","proxy","error"])
        writer.writeheader()
        for r in all_results:
            writer.writerow(r)
    with open(results_json, "w", encoding="utf-8") as jf:
        json.dump(all_results, jf, ensure_ascii=False, indent=2)
    print(f"Saved results to {results_csv} and {results_json}")
if __name__ == "__main__":
    main()
