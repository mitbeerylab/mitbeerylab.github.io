#!/usr/bin/env python3

import argparse
import csv
import os
import re
import ssl
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import date, datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
SOFTWARE_PATH = REPO_ROOT / "_data" / "software.yml"
CAROUSEL_PATH = REPO_ROOT / "_data" / "carousel.yml"
DEFAULT_PROJECTS_SHEET_CSV_URL = (
    "https://docs.google.com/spreadsheets/d/1nRjzZbdweFtIlbfL59zp02gUtC7QAn2jGy4e_nIUAOo/"
    "export?format=csv&gid=889022245"
)
USER_AGENT = "beerylab-projects-updater/1.0 (github-actions)"
TITLE_ALIASES = ("Title", "title")
IMAGE_ALIASES = ("Project Logo (square image)", "Project Logo", "Logo", "logo")
DESCRIPTION_ALIASES = ("Description", "description")
CAROUSEL_IMAGE_ALIASES = (
    "Project Landscape Summary Figure",
    "Carousel Image",
    "carousel_image",
)
CAROUSEL_SUMMARY_ALIASES = (
    "<10 Word Summary / Catchphrase",
    "10 Word Summary",
    "Carousel Summary",
    "carousel_summary",
)
PUBLICATION_DATE_ALIASES = (
    "Publication Date (mainly for sorting projects on website, year will appear on page)",
    "Publication Date",
    "publication_date",
)
THEME_ALIASES = ("Research Theme", "Research Themes", "themes", "theme")
TIMESTAMP_ALIASES = ("Timestamp", "timestamp")
OPTIONAL_LINKS = [
    ("Website", ("Website", "website")),
    ("Demo", ("Demo", "demo")),
    ("Code", ("Code", "code")),
    ("Data", ("Data", "data")),
    ("Paper", ("Paper", "paper")),
]
DATE_FORMATS = (
    "%m/%d/%Y",
    "%m/%d/%y",
    "%Y-%m-%d",
    "%d %b %Y",
    "%d %B %Y",
    "%b %Y",
    "%B %Y",
    "%Y",
)
TIMESTAMP_FORMATS = (
    "%m/%d/%Y %H:%M:%S",
    "%m/%d/%Y %H:%M",
    "%Y-%m-%d %H:%M:%S",
    "%Y-%m-%d %H:%M",
)
CANONICAL_THEMES = [
    "Computer Vision",
    "Datasets & Benchmarks",
    "Biodiversity Monitoring",
    "Scientific Workflows",
    "Environmental Sensing",
    "Multimodal Modeling",
    "Interpretable & Reliable AI",
    "Data-Limited Learning",
]
RETIRED_THEMES = {"Deep Learning", "Position Papers"}
THEME_ALIAS_MAP = {
    "Data & Benchmarks": "Datasets & Benchmarks",
    "Dataset & Benchmarks": "Datasets & Benchmarks",
    "Multimodal Environmental Sensing": "Multimodal Modeling",
    "Earth Observation": "Environmental Sensing",
}
MANAGED_FIELDS = {
    "title",
    "image",
    "description",
    "links",
    "themes",
    "publication_date",
    "year",
}
CAROUSEL_MANAGED_FIELDS = {"title", "description", "image", "link", "date"}
DRIVE_FILE_ID_RE = re.compile(r"(?:/d/|id=)([-a-zA-Z0-9_]{10,})")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Update _data/software.yml from the BeeryLab project Google Form responses."
    )
    parser.add_argument("--dry-run", action="store_true", help="Print what would change without writing the YAML.")
    parser.add_argument(
        "--csv-url",
        default=None,
        help="Override the Google Sheet CSV export URL. Defaults to PROJECTS_SHEET_CSV_URL or the repo default.",
    )
    return parser.parse_args()


def split_header_and_entries(raw_text: str) -> Tuple[str, List[Dict[str, Any]]]:
    lines = raw_text.splitlines()
    first_entry_index = None
    for idx, line in enumerate(lines):
        if line.lstrip().startswith("- title:"):
            first_entry_index = idx
            break

    if first_entry_index is None:
        header = raw_text
        if header and not header.endswith("\n"):
            header += "\n"
        return header, []

    header = "\n".join(lines[:first_entry_index])
    if header and not header.endswith("\n"):
        header += "\n"

    body = "\n".join(lines[first_entry_index:])
    entries = yaml.safe_load(body) or []
    if not isinstance(entries, list):
        raise ValueError("Expected _data/software.yml to contain a top-level list.")
    return header, entries


def render_output(header: str, entries: List[Dict[str, Any]]) -> str:
    if not entries:
        return f"{header.rstrip()}\n" if header.strip() else ""

    body = yaml.safe_dump(
        entries,
        sort_keys=False,
        allow_unicode=True,
        default_flow_style=False,
        width=1000,
    ).rstrip()
    if header.strip():
        return f"{header.rstrip()}\n\n{body}\n"
    return f"{body}\n"


def csv_url_from_args(args: argparse.Namespace) -> str:
    value = (args.csv_url or os.getenv("PROJECTS_SHEET_CSV_URL") or DEFAULT_PROJECTS_SHEET_CSV_URL).strip()
    if not value:
        raise ValueError("Missing Google Sheet CSV URL. Set PROJECTS_SHEET_CSV_URL or pass --csv-url.")
    return value


def fetch_rows(csv_url: str) -> List[Dict[str, str]]:
    request = urllib.request.Request(csv_url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            payload = response.read().decode("utf-8-sig")
    except urllib.error.URLError as exc:
        reason = getattr(exc, "reason", None)
        if not isinstance(reason, ssl.SSLCertVerificationError):
            raise
        insecure_context = ssl._create_unverified_context()
        with urllib.request.urlopen(request, timeout=30, context=insecure_context) as response:
            payload = response.read().decode("utf-8-sig")
        print("Warning: SSL certificate verification failed locally; retried project sheet fetch without verification.")
    return list(csv.DictReader(payload.splitlines()))


def value_for(row: Dict[str, Any], aliases: Iterable[str]) -> str:
    for key in aliases:
        value = row.get(key)
        if value is not None:
            return str(value).strip()
    return ""


def is_blank_row(row: Dict[str, Any]) -> bool:
    return not any(str(value).strip() for value in row.values())


def normalize_title_key(title: str) -> str:
    return re.sub(r"\s+", " ", title.strip().lower())


def parse_date_value(raw_value: str) -> date:
    cleaned = raw_value.strip()
    if not cleaned:
        raise ValueError("Missing publication date.")
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(cleaned, fmt).date()
        except ValueError:
            continue
    raise ValueError(f"Unsupported publication date format: {raw_value!r}")


def parse_timestamp(raw_value: str) -> Optional[datetime]:
    cleaned = raw_value.strip()
    if not cleaned:
        return None
    for fmt in TIMESTAMP_FORMATS:
        try:
            return datetime.strptime(cleaned, fmt)
        except ValueError:
            continue
    return None


def normalize_url(raw_url: str) -> str:
    value = raw_url.strip()
    if not value:
        return ""
    parsed = urllib.parse.urlparse(value)
    if parsed.scheme:
        return value
    if value.startswith("www."):
        return f"https://{value}"
    return value


def extract_drive_file_id(raw_url: str) -> Optional[str]:
    match = DRIVE_FILE_ID_RE.search(raw_url)
    if match:
        return match.group(1)
    return None


def normalize_image_url(raw_url: str) -> str:
    url = normalize_url(raw_url)
    if not url:
        return ""
    drive_file_id = extract_drive_file_id(url)
    if drive_file_id:
        return f"https://drive.google.com/thumbnail?id={drive_file_id}&sz=w400"
    return url


def normalize_carousel_image_url(raw_url: str) -> str:
    url = normalize_url(raw_url)
    if not url:
        return ""
    drive_file_id = extract_drive_file_id(url)
    if drive_file_id:
        return f"https://drive.google.com/thumbnail?id={drive_file_id}&sz=w1600"
    return url


def normalize_theme_name(raw_theme: str) -> str:
    cleaned = re.sub(r"\s+", " ", raw_theme.strip())
    return THEME_ALIAS_MAP.get(cleaned, cleaned)


def normalize_themes(raw_value: str) -> List[str]:
    if not raw_value.strip():
        raise ValueError("Missing research theme.")

    seen = set()
    normalized: List[str] = []
    unknown: List[str] = []
    for chunk in re.split(r"[,\n;]+", raw_value):
        candidate = normalize_theme_name(chunk)
        if not candidate:
            continue
        if candidate in RETIRED_THEMES:
            continue
        if candidate in CANONICAL_THEMES:
            if candidate not in seen:
                normalized.append(candidate)
                seen.add(candidate)
        else:
            unknown.append(chunk.strip())

    if unknown:
        raise ValueError(
            "Unknown research theme(s): "
            + ", ".join(sorted(set(value for value in unknown if value)))
        )
    if not normalized:
        raise ValueError("No valid research themes found.")
    return normalized


def build_links(row: Dict[str, Any]) -> List[Dict[str, str]]:
    links = []
    for label, aliases in OPTIONAL_LINKS:
        url = normalize_url(value_for(row, aliases))
        if url:
            links.append({"label": label, "url": url})
    return links


def richness_score(row: Dict[str, Any]) -> Tuple[int, int, int]:
    optional_link_count = sum(1 for _, aliases in OPTIONAL_LINKS if value_for(row, aliases))
    description_length = len(value_for(row, DESCRIPTION_ALIASES))
    theme_count = len([chunk for chunk in re.split(r"[,\n;]+", value_for(row, THEME_ALIASES)) if chunk.strip()])
    return optional_link_count, description_length, theme_count


def select_preferred_row(current_row: Dict[str, Any], candidate_row: Dict[str, Any]) -> Dict[str, Any]:
    current_timestamp = parse_timestamp(value_for(current_row, TIMESTAMP_ALIASES)) or datetime.min
    candidate_timestamp = parse_timestamp(value_for(candidate_row, TIMESTAMP_ALIASES)) or datetime.min
    if candidate_timestamp != current_timestamp:
        return candidate_row if candidate_timestamp > current_timestamp else current_row

    current_pub_date = parse_date_value(value_for(current_row, PUBLICATION_DATE_ALIASES))
    candidate_pub_date = parse_date_value(value_for(candidate_row, PUBLICATION_DATE_ALIASES))
    if candidate_pub_date != current_pub_date:
        return candidate_row if candidate_pub_date > current_pub_date else current_row

    candidate_richness = richness_score(candidate_row)
    current_richness = richness_score(current_row)
    if candidate_richness != current_richness:
        return candidate_row if candidate_richness > current_richness else current_row

    current_title = value_for(current_row, TITLE_ALIASES).lower()
    candidate_title = value_for(candidate_row, TITLE_ALIASES).lower()
    return candidate_row if candidate_title < current_title else current_row


def entry_publication_date(entry: Dict[str, Any]) -> date:
    raw_publication_date = str(entry.get("publication_date") or "").strip()
    if raw_publication_date:
        return parse_date_value(raw_publication_date)

    year_value = entry.get("year")
    try:
        year = int(year_value)
        return date(year, 1, 1)
    except (TypeError, ValueError):
        pass
    return date.min


def sort_key_for_entry(entry: Dict[str, Any]) -> Tuple[int, str]:
    publication_date = entry_publication_date(entry)
    date_rank = int(publication_date.strftime("%Y%m%d")) if publication_date != date.min else 0
    return (-date_rank, str(entry.get("title") or "").strip().lower())


def carousel_sort_key(entry: Dict[str, Any]) -> Tuple[int, str]:
    raw_date = str(entry.get("date") or "").strip()
    slide_date = parse_date_value(raw_date) if raw_date else date.min
    date_rank = int(slide_date.strftime("%Y%m%d")) if slide_date != date.min else 0
    return (-date_rank, str(entry.get("title") or "").strip().lower())


def build_entry(row: Dict[str, Any], existing_entry: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    title = value_for(row, TITLE_ALIASES)
    description = value_for(row, DESCRIPTION_ALIASES)
    publication_date_raw = value_for(row, PUBLICATION_DATE_ALIASES)
    image_raw = value_for(row, IMAGE_ALIASES)
    themes_raw = value_for(row, THEME_ALIASES)

    missing_fields = []
    if not title:
        missing_fields.append("Title")
    if not image_raw:
        missing_fields.append("Project Logo (square image)")
    if not description:
        missing_fields.append("Description")
    if not publication_date_raw:
        missing_fields.append("Publication Date")
    if not themes_raw:
        missing_fields.append("Research Theme")
    if missing_fields:
        raise ValueError(f"Missing required field(s): {', '.join(missing_fields)}")

    publication_date = parse_date_value(publication_date_raw)
    image_url = normalize_image_url(image_raw)
    if not image_url:
        raise ValueError("Project Logo (square image) must be a valid URL.")

    entry: Dict[str, Any] = {
        "title": title,
        "image": image_url,
        "description": description,
        "themes": normalize_themes(themes_raw),
        "publication_date": publication_date.isoformat(),
        "year": publication_date.year,
    }

    links = build_links(row)
    if links:
        entry["links"] = links

    if existing_entry:
        for key, value in existing_entry.items():
            if key not in MANAGED_FIELDS and key not in entry:
                entry[key] = value

    return entry


def build_carousel_entry(row: Dict[str, Any], existing_entry: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    title = value_for(row, TITLE_ALIASES)
    summary = value_for(row, CAROUSEL_SUMMARY_ALIASES)
    image_raw = value_for(row, CAROUSEL_IMAGE_ALIASES)
    paper_url = normalize_url(value_for(row, ("Paper", "paper")))
    publication_date_raw = value_for(row, PUBLICATION_DATE_ALIASES)

    if not (title and summary and image_raw and paper_url and publication_date_raw):
        return None

    publication_date = parse_date_value(publication_date_raw)
    image_url = normalize_carousel_image_url(image_raw)
    if not image_url:
        return None

    entry: Dict[str, Any] = {
        "title": title,
        "description": summary,
        "image": image_url,
        "link": paper_url,
        "date": publication_date.isoformat(),
    }

    if existing_entry:
        for key, value in existing_entry.items():
            if key not in CAROUSEL_MANAGED_FIELDS and key not in entry:
                entry[key] = value

    return entry


def main() -> int:
    args = parse_args()

    if not SOFTWARE_PATH.exists():
        print(f"File not found: {SOFTWARE_PATH}")
        return 1
    if not CAROUSEL_PATH.exists():
        print(f"File not found: {CAROUSEL_PATH}")
        return 1

    try:
        csv_url = csv_url_from_args(args)
        rows = fetch_rows(csv_url)
    except (ValueError, urllib.error.URLError, TimeoutError) as exc:
        print(f"Failed to fetch project rows: {exc}")
        return 1

    raw_text = SOFTWARE_PATH.read_text(encoding="utf-8")
    header, existing_entries = split_header_and_entries(raw_text)
    existing_by_title = {
        normalize_title_key(str(entry.get("title") or "")): entry
        for entry in existing_entries
        if str(entry.get("title") or "").strip()
    }
    carousel_raw_text = CAROUSEL_PATH.read_text(encoding="utf-8")
    carousel_header, existing_carousel_entries = split_header_and_entries(carousel_raw_text)
    existing_carousel_by_title = {
        normalize_title_key(str(entry.get("title") or "")): entry
        for entry in existing_carousel_entries
        if str(entry.get("title") or "").strip()
    }

    selected_rows: Dict[str, Dict[str, Any]] = {}
    blank_rows_skipped = 0
    duplicate_rows_collapsed = 0

    for row in rows:
        if is_blank_row(row):
            blank_rows_skipped += 1
            continue
        title = value_for(row, TITLE_ALIASES)
        title_key = normalize_title_key(title)
        if not title_key:
            print("Encountered a non-empty row without a Title.")
            return 1

        existing_row = selected_rows.get(title_key)
        if existing_row is None:
            selected_rows[title_key] = row
            continue

        preferred = select_preferred_row(existing_row, row)
        if preferred is not existing_row:
            selected_rows[title_key] = preferred
        duplicate_rows_collapsed += 1

    generated_entries: List[Dict[str, Any]] = []
    generated_carousel_entries: List[Dict[str, Any]] = []
    for title_key, row in selected_rows.items():
        try:
            generated_entries.append(build_entry(row, existing_by_title.get(title_key)))
        except ValueError as exc:
            title = value_for(row, TITLE_ALIASES) or "<untitled>"
            print(f"Invalid project row for {title!r}: {exc}")
            return 1
        carousel_entry = build_carousel_entry(row, existing_carousel_by_title.get(title_key))
        if carousel_entry is not None:
            generated_carousel_entries.append(carousel_entry)

    generated_title_keys = {normalize_title_key(str(entry.get("title") or "")) for entry in generated_entries}
    preserved_local_entries = [
        entry
        for entry in existing_entries
        if normalize_title_key(str(entry.get("title") or "")) not in generated_title_keys
    ]
    generated_carousel_title_keys = {
        normalize_title_key(str(entry.get("title") or "")) for entry in generated_carousel_entries
    }
    preserved_local_carousel_entries = [
        entry
        for entry in existing_carousel_entries
        if normalize_title_key(str(entry.get("title") or "")) not in generated_carousel_title_keys
    ]

    combined_entries = generated_entries + preserved_local_entries
    combined_entries.sort(key=sort_key_for_entry)
    combined_carousel_entries = generated_carousel_entries + preserved_local_carousel_entries
    combined_carousel_entries.sort(key=carousel_sort_key)

    print(f"Fetched project rows: {len(rows)}")
    print(f"Blank rows skipped: {blank_rows_skipped}")
    print(f"Duplicate title rows collapsed: {duplicate_rows_collapsed}")
    print(f"Projects generated from form rows: {len(generated_entries)}")
    print(f"Existing local-only projects preserved: {len(preserved_local_entries)}")
    print("Projects sorted by publication date:")
    for entry in combined_entries[:10]:
        print(f"- {entry.get('title', '').strip()} | publication_date={entry.get('publication_date', 'n/a')} | year={entry.get('year', 'n/a')}")
    print(f"Carousel slides generated from form rows: {len(generated_carousel_entries)}")
    print(f"Existing local-only carousel slides preserved: {len(preserved_local_carousel_entries)}")
    print("Carousel sorted by publication date:")
    for entry in combined_carousel_entries[:10]:
        print(f"- {entry.get('title', '').strip()} | date={entry.get('date', 'n/a')}")

    updated_text = render_output(header=header, entries=combined_entries)
    updated_carousel_text = render_output(header=carousel_header, entries=combined_carousel_entries)
    if args.dry_run:
        print("Dry run enabled: no file changes written.")
        return 0

    software_changed = updated_text != raw_text
    carousel_changed = updated_carousel_text != carousel_raw_text
    if not software_changed and not carousel_changed:
        print("No changes made.")
        return 0

    if software_changed:
        SOFTWARE_PATH.write_text(updated_text, encoding="utf-8")
    if carousel_changed:
        CAROUSEL_PATH.write_text(updated_carousel_text, encoding="utf-8")

    if software_changed and carousel_changed:
        print(f"Updated {SOFTWARE_PATH} and {CAROUSEL_PATH}")
    elif software_changed:
        print(f"Updated {SOFTWARE_PATH}")
    else:
        print(f"Updated {CAROUSEL_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
