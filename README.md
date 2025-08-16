# 403HunterFinal / 403HunterPro

## Repository description (English)
403HunterFinal is a Python toolkit designed to help authorized security researchers and bug bounty hunters analyze subdomains that return 403 Forbidden responses and attempt legitimate header-based variations to discover accessible endpoints. This project is intended for authorized testing only.

## وصف المستودع (العربية)
403HunterFinal هي أداة بايثون لمساعدة باحثي الأمن السيبراني وباحثي Bug Bounty المصرح لهم على فحص النطاقات الفرعية التي تعيد 403 ومحاولة تغييرات في الهيدرز لمعرفة ما إذا كانت هناك مسارات يمكن الوصول إليها. الاستخدام مقتصر على الاختبارات المصرح بها فقط.

## Project name
403HunterFinal

## Folder structure and purpose
- src/   : source code (main Python script)
- out/   : default output folder (results are written here)
- docs/  : documentation and examples
- scripts/: helper scripts for packaging or CI

## How it helps a Bug Bounty hunter
1. Reads a list of subdomains and tests them as HTTPS endpoints.
2. Rotates User-Agent and IP-related headers to emulate real users.
3. Attempts multiple request variations (GET, HEAD, adding trailing slash, host header).
4. Supports proxy rotation for distributed testing.
5. Produces CSV and JSON reports with details about every attempt.

## Quick start
Install dependencies:
```bash
python3 -m pip install requests colorama
```
Run:
```bash
python3 src/bypass403.py -d subdomains.txt -u uas.txt -p proxies.txt -o out --threads 10 --delay-min 1 --delay-max 3
```

## Legal notice / تحذير قانوني
Only use this tool on assets you own or have explicit written authorization to test. Unauthorized testing may be illegal.

## Suggested future improvements
- Add Selenium/Playwright fallback for JavaScript protected pages.
- Add modular header sets and JSON-based scenarios.
- Integrate with common bug bounty platforms for reporting.
