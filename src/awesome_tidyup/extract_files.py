#!/usr/bin/env python3
"""Extract file metadata from CS-6150-O01.html and save to CSV.

Usage: python -m src.awesome_tidyup.extract_files -i CS-6150-O01.html -o files.csv
Requires: beautifulsoup4 (`pip install beautifulsoup4`)
"""
from __future__ import annotations

import argparse
import csv
import re
import sys
from html import unescape as html_unescape
from pathlib import Path

try:
    from bs4 import BeautifulSoup
except Exception:
    sys.exit("BeautifulSoup4 is required. Install with: pip install beautifulsoup4")


def parse_html(path: Path):
    html = path.read_text(encoding="utf-8", errors="ignore")
    soup = BeautifulSoup(html, "html.parser")
    rows = soup.find_all("tr", attrs={"data-file-id": True})
    # If BeautifulSoup doesn't find rows (some exports may include unquoted attrs
    # or other quirks), fall back to a regex-based extractor on raw HTML.
    if not rows:
        starts = [m.start() for m in re.finditer(r"<tr\b[^>]*data-file-id=", html, re.I)]
        for idx, s in enumerate(starts):
            if idx + 1 < len(starts):
                e = starts[idx + 1]
            else:
                tb = html.find('</tbody>', s)
                e = tb if tb != -1 else len(html)
            block = html[s:e]
            # unescape entities so attributes like class=&quot;...&quot; become parseable
            block = html_unescape(block)
            # filename
            filename = ""
            mfn = re.search(r'data-filename=(?:"([^"]+)"|\'([^\']+)\'|([^\s>]+))', block)
            if mfn:
                for g in mfn.groups():
                    if g:
                        filename = g.strip()
                        break
            else:
                mnt = re.search(r'<span[^>]*class=["\']?name-text["\']?[^>]*>(.*?)</span>', block, re.I | re.S)
                if mnt:
                    filename = re.sub(r'<[^>]+>', '', mnt.group(1)).strip()

            # access restriction: locate the specific element's class attribute
            access = "none"
            # Look specifically for a span element whose class includes 'file-lock'
            access = "none"
            mspan = re.search(r"<span[^>]*class\s*=\s*(?:\"([^\"]*\bfile-lock\b[^\"]*)\"|'([^']*\bfile-lock\b[^']*)'|([^>\s]*\bfile-lock\b[^>\s]*))[^>]*>", block, re.I)
            if mspan:
                cls = next((g for g in mspan.groups() if g), "")
                parts = re.split(r"\s+", cls.strip()) if cls else []
                # unrestricted only when both d-none and sf-hidden are present
                if not ("d-none" in parts and "sf-hidden" in parts):
                    access = "restricted"
            else:
                # fallback token check
                if 'file-lock' in block and 'd-none' not in block and 'sf-hidden' not in block:
                    access = 'restricted'

            # used in
            used_in = ""
            musage = re.search(r'<td[^>]*class=["\']?file-usage["\']?[^>]*>(.*?)</td>', block, re.I | re.S)
            if musage:
                inner = musage.group(1)
                mlink = re.search(r'<a[^>]*class=["\']?usage-link["\']?[^>]*>(.*?)</a>', inner, re.I | re.S)
                if mlink:
                    used_in = re.sub(r'<[^>]+>', '', mlink.group(1)).strip()
                else:
                    msr = re.search(r'<span[^>]*class=["\']?sr-only["\']?[^>]*>(.*?)</span>', inner, re.I | re.S)
                    if msr:
                        used_in = msr.group(1).strip()

            # last updated
            mupdated = re.search(r'<td[^>]*class=["\']?file-updated["\']?[^>]*>(.*?)</td>', block, re.I | re.S)
            last_updated = re.sub(r'<[^>]+>', '', mupdated.group(1)).strip() if mupdated else ""

            # size
            msize = re.search(r'<td[^>]*class=["\']?file-size["\']?[^>]*>(.*?)</td>', block, re.I | re.S)
            size = re.sub(r'<[^>]+>', '', msize.group(1)).strip() if msize else ""

            # unescape any HTML entities
            filename = html_unescape(filename)
            used_in = html_unescape(used_in)
            last_updated = html_unescape(last_updated)
            size = html_unescape(size)

            # normalize used_in: strip whitespace and surrounding quotes
            used_in = used_in.strip()
            if used_in.startswith('"') and used_in.endswith('"') and len(used_in) >= 2:
                used_in = used_in[1:-1]
            # collapse doubled quotes that may have come from HTML entities
            used_in = used_in.replace('""', '"')
            used_in = used_in.strip()

            yield {
                "filename": filename,
                "access_restriction": access,
                "used_in": used_in,
                "last_updated": last_updated,
                "size": size,
            }
        return
    for tr in rows:
        # filename
        filename = ""
        inp = tr.find("input", attrs={"data-filename": True})
        if inp and inp.has_attr("data-filename"):
            filename = inp["data-filename"].strip()
        else:
            nt = tr.find(class_="name-text")
            if nt:
                filename = nt.get_text(strip=True)

        # access restriction: presence of .file-lock without d-none
        access = "none"
        lock = tr.find(class_="file-lock")
        if lock:
            classes = lock.get("class", [])
            # classes can be list or string; normalize to list of tokens
            if isinstance(classes, list):
                parts = classes
            else:
                parts = re.split(r"\s+", classes.strip()) if classes else []
            # treat as unrestricted only when both d-none and sf-hidden are present
            if not ("d-none" in parts and "sf-hidden" in parts):
                access = "restricted"

        # used in
        used_in = ""
        usage_td = tr.find("td", class_="file-usage")
        if usage_td:
            usage_link = usage_td.find(class_="usage-link")
            if usage_link:
                used_in = usage_link.get_text(separator=" ", strip=True)
            else:
                sr = usage_td.find("span", class_="sr-only")
                if sr:
                    used_in = sr.get_text(strip=True)

        # last updated
        updated_td = tr.find("td", class_="file-updated")
        last_updated = updated_td.get_text(strip=True) if updated_td else ""

        # size
        size_td = tr.find("td", class_="file-size")
        size = size_td.get_text(strip=True) if size_td else ""

        yield {
            "filename": filename,
            "access_restriction": access,
            "used_in": used_in,
            "last_updated": last_updated,
            "size": size,
        }


def main():
    p = argparse.ArgumentParser(description="Extract file metadata from an exported HTML file")
    p.add_argument("-i", "--input", default="CS-6150-O01.html", help="input HTML file path")
    p.add_argument("-o", "--output", default="files.csv", help="output CSV file path")
    args = p.parse_args()

    in_path = Path(args.input)
    if not in_path.exists():
        print(f"Input file not found: {in_path}", file=sys.stderr)
        raise SystemExit(1)

    records = list(parse_html(in_path))

    with open(args.output, "w", newline="", encoding="utf-8") as fh:
        fieldnames = ["filename", "access_restriction", "used_in", "last_updated", "size"]
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        for r in records:
            writer.writerow(r)

    print(f"Wrote {len(records)} rows to {args.output}")


if __name__ == "__main__":
    main()
