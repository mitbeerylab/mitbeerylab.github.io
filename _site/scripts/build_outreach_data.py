#!/usr/bin/env python3

import csv
import json
import re
import urllib.error
import urllib.request
from collections import Counter
from datetime import datetime
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

REPO_ROOT = Path(__file__).resolve().parent.parent
OUTREACH_FILES = {
    "talk": {
        "path": REPO_ROOT / "_outreach" / "talks.md",
        "label": "Talk",
        "person_label": "Speaker",
        "org_label": "Host",
    },
    "teaching": {
        "path": REPO_ROOT / "_outreach" / "teaching.md",
        "label": "Teaching & Community Building",
        "person_label": "Instructor(s)",
        "org_label": "Institution",
    },
}
OUTPUT_PATH = REPO_ROOT / "_data" / "outreach.json"
DATE_FORMATS = (
    "%Y-%m-%d",
    "%m/%d/%Y",
    "%d %b %Y",
    "%d %B %Y",
    "%b %Y",
    "%B %Y",
    "%Y",
)
HEADER_ALIASES = {
    "title": ("Title", "title"),
    "speaker": (
        "Speakers",
        "Speaker",
        "speakers",
        "speaker",
        "Instructor(s)",
        "Instructor",
        "Instructors",
        "instructor(s)",
        "instructor",
        "instructors",
    ),
    "host": (
        "Host",
        "host",
        "Institution",
        "Institutions",
        "Instiution",
        "institution",
        "institutions",
        "instiution",
    ),
    "date_display": ("Date", "date", "publish_date_display", "Publish Date"),
    "publish_date": ("publish_date", "Publish Date ISO", "Sort Date", "sort_date"),
    "external": ("External", "external", "URL", "url"),
}
FRONT_MATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*(?:\n|\Z)(.*)\Z", re.DOTALL)


def extract_front_matter_and_body(raw_text: str, relative_path: str):
    match = FRONT_MATTER_RE.match(raw_text)
    if not match:
        raise ValueError(f"Could not parse front matter in {relative_path}.")

    front_matter = {}
    for line in match.group(1).splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if ":" not in stripped:
            raise ValueError(f"Invalid front matter line in {relative_path}: {line}")
        key, value = stripped.split(":", 1)
        front_matter[key.strip()] = value.strip().strip('"').strip("'")

    return front_matter, match.group(2)


def parse_markdown_table(body: str, relative_path: str):
    table_lines = [line.rstrip() for line in body.splitlines() if line.strip().startswith("|")]
    if not table_lines:
        return []
    if len(table_lines) < 2:
        raise ValueError(f"Markdown table in {relative_path} must include a header and separator row.")

    headers = split_table_row(table_lines[0])
    rows = []
    for line in table_lines[2:]:
        if not line.strip():
            continue
        values = split_table_row(line)
        row = {}
        for index, header in enumerate(headers):
            row[header] = values[index].strip() if index < len(values) else ""
        rows.append(row)
    return rows


def split_table_row(line: str):
    return [part.strip() for part in line.strip().lstrip("|").rstrip("|").split("|")]


def fetch_remote_rows(remote_url: str, relative_path: str):
    url = (remote_url or "").strip()
    if not url:
        return []

    request = urllib.request.Request(url, headers={"User-Agent": "beerylab-outreach/1.0"})
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            content = response.read().decode("utf-8")
    except (urllib.error.URLError, TimeoutError) as err:
        print(f"Warning: could not fetch {relative_path} remote sheet ({err}); using local table.")
        return []

    reader = csv.DictReader(content.splitlines())
    return list(reader)


def value_for(row, aliases):
    for key in aliases:
        value = row.get(key)
        if value is not None:
            return str(value).strip()
    return ""


def parse_mixed_date(raw_value: str):
    cleaned = re.sub(r"\bSept\b", "Sep", raw_value.strip(), flags=re.IGNORECASE)
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(cleaned, fmt).date()
        except ValueError:
            continue
    raise ValueError(f"Unsupported date format {cleaned!r}")


def date_precision(raw_value: str):
    cleaned = re.sub(r"\bSept\b", "Sep", raw_value.strip(), flags=re.IGNORECASE)
    if re.fullmatch(r"\d{4}", cleaned):
        return "year"
    if re.fullmatch(r"\d{1,2}/\d{1,2}/\d{4}", cleaned):
        return "day"
    if re.fullmatch(r"[A-Za-z]{3,9}\s+\d{4}", cleaned):
        return "month"
    if re.fullmatch(r"\d{1,2}\s+[A-Za-z]{3,9}\s+\d{4}", cleaned):
        return "day"
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", cleaned):
        return "day"
    raise ValueError(f"Unsupported date format {cleaned!r}")


def normalized_publish_date(row):
    explicit_date = value_for(row, HEADER_ALIASES["publish_date"])
    if explicit_date:
        return datetime.strptime(explicit_date, "%Y-%m-%d").date().isoformat()

    display_date = value_for(row, HEADER_ALIASES["date_display"])
    return parse_mixed_date(display_date).isoformat()


def display_date_for(row, item_type: str):
    raw_date = value_for(row, HEADER_ALIASES["date_display"])
    parsed_date = parse_mixed_date(raw_date)
    precision = date_precision(raw_date)

    if precision == "year":
        return parsed_date.strftime("%Y")
    if item_type == "teaching":
        return parsed_date.strftime("%b %Y")
    if precision == "month":
        return parsed_date.strftime("%b %Y")
    return parsed_date.strftime("%d %b %Y")


def normalize_row(row, item_type: str, label: str, relative_path: str):
    title = value_for(row, HEADER_ALIASES["title"])
    raw_date_display = value_for(row, HEADER_ALIASES["date_display"])
    external = value_for(row, HEADER_ALIASES["external"])
    publish_date = normalized_publish_date(row)

    if not title or not raw_date_display or not external:
        raise ValueError(f"{relative_path} entries must include Title, Date, and External.")

    normalized = {
        "type": item_type,
        "type_label": label,
        "title": title,
        "publish_date": publish_date,
        "publish_date_display": display_date_for(row, item_type),
        "external": external,
    }
    speaker = value_for(row, HEADER_ALIASES["speaker"])
    host = value_for(row, HEADER_ALIASES["host"])
    if speaker:
        normalized["speaker"] = speaker
    if host:
        normalized["host"] = host
    return normalized


def apply_item_labels(item, config):
    labeled = dict(item)
    if "speaker" in labeled:
        labeled["speaker_label"] = config["person_label"]
    if "host" in labeled:
        labeled["host_label"] = config["org_label"]
    return labeled


def normalized_text(value: str):
    collapsed = re.sub(r"\s+", " ", value.strip()).casefold()
    return re.sub(r"[^0-9a-z]+", "", collapsed)


def canonical_external_url(value: str):
    cleaned = value.strip()
    if not cleaned:
        return ""

    split = urlsplit(cleaned)
    path = split.path.rstrip("/")
    if split.path == "/":
        path = "/"
    return urlunsplit((split.scheme.lower(), split.netloc.lower(), path, "", ""))


def row_key(row, item_type: str):
    title = normalized_text(value_for(row, HEADER_ALIASES["title"]))
    publish_date = normalized_publish_date(row)
    external = canonical_external_url(value_for(row, HEADER_ALIASES["external"]))

    if title and publish_date:
        return f"{item_type}||{title}||{publish_date}"
    return f"{item_type}||{external}"


def row_quality(row):
    fields = (
        value_for(row, HEADER_ALIASES["title"]),
        value_for(row, HEADER_ALIASES["speaker"]),
        value_for(row, HEADER_ALIASES["host"]),
        value_for(row, HEADER_ALIASES["date_display"]),
        value_for(row, HEADER_ALIASES["publish_date"]),
        value_for(row, HEADER_ALIASES["external"]),
    )
    return sum(1 for value in fields if value)


def choose_preferred_row(existing_row, candidate_row):
    candidate_quality = row_quality(candidate_row)
    existing_quality = row_quality(existing_row)
    if candidate_quality > existing_quality:
        return candidate_row
    if candidate_quality == existing_quality:
        return candidate_row
    return existing_row


def load_items(item_type: str, config):
    relative_path = str(config["path"].relative_to(REPO_ROOT))
    front_matter, body = extract_front_matter_and_body(config["path"].read_text(encoding="utf-8"), relative_path)
    local_rows = parse_markdown_table(body, relative_path)
    remote_rows = fetch_remote_rows(front_matter.get("google_sheet_csv", ""), relative_path)

    merged = {}
    for row in local_rows:
        merged[row_key(row, item_type)] = row
    for row in remote_rows:
        key = row_key(row, item_type)
        existing = merged.get(key)
        merged[key] = choose_preferred_row(existing, row) if existing else row

    return [
        apply_item_labels(normalize_row(row, item_type, config["label"], relative_path), config)
        for row in merged.values()
    ]


def main():
    items = []
    for item_type, config in OUTREACH_FILES.items():
        items.extend(load_items(item_type, config))

    items.sort(key=lambda item: (item["publish_date"], item["title"].lower()), reverse=True)
    counts = Counter(item["type"] for item in items)
    payload = {
        "counts": {
            "total": len(items),
            "talks": counts["talk"],
            "teaching": counts["teaching"],
        },
        "items": items,
    }

    OUTPUT_PATH.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
