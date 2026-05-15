#!/usr/bin/env python3

import argparse
import json
import os
import random
import re
import sys
import time
from urllib.parse import quote, urlparse
from dataclasses import dataclass
from datetime import date, datetime
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

import requests
import yaml

DEFAULT_PI_NAME = "Sara Beery"
DEFAULT_LAB_START_DATE = "2023-09-01"
API_BASE_URL = "https://api.semanticscholar.org/graph/v1"
SEARCH_ENDPOINT = f"{API_BASE_URL}/paper/search"
PAPER_ENDPOINT = f"{API_BASE_URL}/paper"
PUBLICATIONS_PATH = Path("_data/publications.yml")
PUBLICATIONS_META_PATH = Path("_data/publications_meta.yml")
PAGE_SIZE = 100
REQUEST_TIMEOUT_SECONDS = 20
MIN_REQUEST_INTERVAL_SECONDS = 1.0
MAX_RETRIES = 8
RECOMPUTE_LOOKUP_MAX_RETRIES = 2
LOW_RELEVANCE_THRESHOLD = 0.05
USER_AGENT = "beerylab-publications-updater/1.0 (github-actions)"
SEARCH_BASE_FIELDS = [
    "paperId",
    "title",
    "year",
    "publicationDate",
    "venue",
    "abstract",
    "publicationTypes",
    "url",
    "authors.name",
    "authors.authorId",
    "externalIds",
    "openAccessPdf",
]
SEARCH_OPTIONAL_FIELDS = ["tldr"]
DETAIL_BASE_FIELDS = [
    "paperId",
    "title",
    "year",
    "publicationDate",
    "venue",
    "abstract",
    "publicationTypes",
    "externalIds",
    "url",
]
DOI_PATTERN = re.compile(r"10\.\d{4,9}/[^\s]+", re.IGNORECASE)
NAME_NORMALIZE_RE = re.compile(r"[^\w\s]+", re.UNICODE)
SPACE_RE = re.compile(r"\s+")
TITLE_NORMALIZE_RE = re.compile(r"[^\w]+", re.UNICODE)
MATCH_NORMALIZE_RE = re.compile(r"[^a-z0-9]+")
SOURCE_WEIGHTS = {
    "title": 4,
    "tldr": 3,
    "abstract": 2,
    "venue": 1,
    "publication_type": 1,
}

THEME_RULES = {
    "Computer Vision": {
        "positive_strong": {
            "computer_vision": ["computer vision"],
            "image": ["image", "images", "imagery"],
            "visual": ["visual", "visual recognition", "visual understanding"],
            "detection": ["detection", "object detection"],
            "segmentation": ["segmentation", "instance segmentation", "semantic segmentation"],
            "video_understanding": ["video understanding", "video analysis", "video recognition"],
            "camera_trap_vision": ["camera trap", "camera traps", "camera-trap"],
        },
        "positive_weak": {
            "classification": ["classification"],
            "captioning": ["caption", "captioning"],
            "localization": ["localization", "localisation"],
            "tracking": ["tracking", "object tracking"],
        },
        "negative": {
            "opinion": ["position paper", "opinion"]
        },
        "required_any": {
            "computer_vision",
            "image",
            "visual",
            "detection",
            "segmentation",
            "video_understanding",
            "camera_trap_vision",
        },
        "anchor_families": {
            "computer_vision",
            "image",
            "visual",
            "detection",
            "segmentation",
            "video_understanding",
            "camera_trap_vision",
        },
        "min_score": 4,
    },
    "Datasets & Benchmarks": {
        "positive_strong": {
            "dataset": ["dataset", "datasets", "database", "databases"],
            "benchmark": ["benchmark", "benchmarks"],
            "challenge": ["challenge", "challenges"],
            "leaderboard": ["leaderboard"],
            "corpus": ["corpus", "corpora"],
        },
        "positive_weak": {
            "annotation": ["annotation", "annotated"],
            "curation": ["curation", "curated"],
            "evaluation_protocol": ["evaluation protocol", "evaluation setting"],
        },
        "negative": {
            "opinion": ["position paper", "opinion", "perspective", "viewpoint", "position"]
        },
        "required_any": {"dataset", "benchmark", "challenge", "leaderboard", "corpus"},
        "anchor_families": {"dataset", "benchmark", "challenge", "leaderboard", "corpus"},
        "min_score": 4,
    },
    "Biodiversity Monitoring": {
        "positive_strong": {
            "camera_trap": ["camera trap", "camera traps", "camera trapping", "camera trap data", "camera trap images"],
            "wildlife": ["wildlife", "wild animal", "wild animals"],
            "biodiversity": ["biodiversity", "biodiverse"],
            "conservation": ["conservation", "conservation biology"],
            "ecology": ["ecology", "ecological"],
            "species_identification": ["species identification", "species recognition", "species classification"],
            "animal_reid": ["animal re identification", "animal re-identification"],
            "occupancy": ["species occupancy", "occupancy modeling", "occupancy"],
            "population_estimation": ["population estimation"],
            "habitat": ["habitat", "habitat mapping"],
        },
        "positive_weak": {
            "species": ["species"],
            "animal": ["animal", "animals"],
            "fauna": ["fauna"],
            "citizen_science": ["citizen science"],
            "monitoring": ["monitoring"],
        },
        "negative": {
            "non_environmental": [
                "instruction selection",
                "identity preservation",
                "personalized generation",
                "building energetics",
                "activity disruption",
            ],
            "opinion": ["position paper", "opinion", "perspective", "viewpoint", "position"],
        },
        "required_any": {
            "camera_trap",
            "wildlife",
            "biodiversity",
            "conservation",
            "ecology",
            "species_identification",
            "animal_reid",
            "occupancy",
            "population_estimation",
            "habitat",
        },
        "anchor_families": {
            "camera_trap",
            "wildlife",
            "biodiversity",
            "conservation",
            "ecology",
            "species_identification",
            "animal_reid",
            "occupancy",
            "population_estimation",
            "habitat",
        },
        "min_score": 4,
    },
    "Scientific Workflows": {
        "positive_strong": {
            "annotation": ["annotation tool", "annotation platform", "annotating"],
            "labeling": ["labeling workflow", "labelling workflow"],
            "human_in_loop": ["human in the loop", "human-in-the-loop"],
            "active_learning": ["active learning"],
            "interactive": ["interactive system", "interactive tool", "interactive interface"],
            "workflow": ["workflow", "workflows"],
            "pipeline": ["pipeline", "pipelines"],
            "expert_feedback": ["expert feedback", "user feedback"],
        },
        "positive_weak": {
            "deployment": ["deployment", "deployments"],
            "tool": ["tool", "tools"],
            "citizen_science": ["citizen science"],
        },
        "negative": {
            "opinion": ["position paper", "opinion", "perspective", "viewpoint", "position"]
        },
        "required_any": {"annotation", "labeling", "human_in_loop", "active_learning", "interactive", "workflow", "pipeline"},
        "anchor_families": {"annotation", "labeling", "human_in_loop", "active_learning", "interactive", "workflow", "pipeline"},
        "min_score": 4,
    },
    "Environmental Sensing": {
        "positive_strong": {
            "remote_sensing": ["remote sensing"],
            "satellite": ["satellite", "satellites"],
            "earth_observation": ["earth observation"],
            "landsat": ["landsat"],
            "sentinel": ["sentinel"],
            "sar": ["sar", "synthetic aperture radar"],
            "hyperspectral": ["hyperspectral"],
            "lidar": ["lidar", "li dar"],
            "sonar": ["sonar"],
            "radar": ["radar"],
            "acoustic": ["acoustic", "bioacoustic", "bioacoustics", "audio"],
        },
        "positive_weak": {
            "aerial": ["aerial", "overhead imagery", "overhead image"],
            "drone": ["drone", "drones"],
            "uav": ["uav", "uas"],
            "geospatial": ["geospatial", "geo spatial", "mapping"],
        },
        "negative": {
            "non_environmental": [
                "personalized generation",
                "identity preservation",
                "instruction selection",
            ], "opinion": ['position paper', 'opinion', 'perspective', 'viewpoint', 'position']
        },
        "required_any": {
            "remote_sensing",
            "satellite",
            "earth_observation",
            "landsat",
            "sentinel",
            "sar",
            "hyperspectral",
            "lidar",
            "sonar",
            "radar",
            "acoustic",
            "aerial",
            "drone",
            "uav",
            "geospatial",
        },
        "require_strong_or_two_weak_from": {
            "remote_sensing",
            "satellite",
            "earth_observation",
            "landsat",
            "sentinel",
            "sar",
            "hyperspectral",
            "lidar",
            "sonar",
            "radar",
            "acoustic",
            "aerial",
            "drone",
            "uav",
            "geospatial",
        },
        "min_score": 4,
    },
    "Multimodal Modeling": {
        "positive_strong": {
            "multimodal": ["multimodal", "multi modal", "multi-modal"],
            "sensor_fusion": ["sensor fusion", "multisensor fusion", "multi sensor fusion"],
            "cross_modal": ["cross modal", "cross-modal"],
            "vision_language": ["vision language", "vision-language", "image text", "image-text"],
            "multimodal_model": ["multimodal model", "multimodal models"],
        },
        "positive_weak": {
            "metadata": ["metadata"],
            "text": ["text"],
            "language": ["language"],
            "retrieval": ["retrieval"],
        },
        "negative": {
            "opinion": ["position paper", "opinion", "perspective", "viewpoint", "position"]
        },
        "required_any": {"multimodal", "sensor_fusion", "cross_modal", "vision_language", "multimodal_model"},
        "anchor_families": {"multimodal", "sensor_fusion", "cross_modal", "vision_language", "multimodal_model"},
        "min_score": 4,
    },
    "Interpretable & Reliable AI": {
        "positive_strong": {
            "interpretability": ["interpretability", "interpretable", "explainable", "explanation"],
            "uncertainty": ["uncertainty", "uncertain", "uncertainty estimation"],
            "calibration": ["calibration", "calibrated"],
            "robustness": ["robustness", "robust", "distributionally robust"],
            "reliability": ["reliability", "reliable"],
            "ood": ["out of distribution", "out-of-distribution", "ood", "distribution shift"],
            "safety": ["safety", "safe ai"],
            "selective_prediction": ["selective prediction"],
            "failure_prediction": ["failure prediction"],
            "epistemic_uncertainty": ["epistemic uncertainty"],
        },
        "positive_weak": {
            "saliency": ["saliency"],
            "trustworthy": ["trustworthy", "trustworthiness"],
            "confidence": ["confidence", "confidence score"],
            "error_analysis": ["error analysis"],
        },
        "negative": {
            "opinion": ["position paper", "opinion", "perspective", "viewpoint", "position"]
        },
        "required_any": {
            "interpretability",
            "uncertainty",
            "calibration",
            "robustness",
            "reliability",
            "ood",
            "safety",
            "selective_prediction",
            "failure_prediction",
            "epistemic_uncertainty",
            "saliency",
            "trustworthy",
            "confidence",
            "error_analysis",
        },
        "anchor_families": {
            "interpretability",
            "uncertainty",
            "calibration",
            "robustness",
            "reliability",
            "ood",
            "safety",
            "selective_prediction",
            "failure_prediction",
            "epistemic_uncertainty",
        },
        "min_score": 4,
    },
    "Data-Limited Learning": {
        "positive_strong": {
            "few_shot": ["few shot", "few-shot"],
            "low_shot": ["low shot", "low-shot"],
            "zero_shot": ["zero shot", "zero-shot"],
            "long_tail": ["long tail", "long-tail"],
            "imbalanced": ["imbalanced", "class imbalance"],
            "domain_shift": ["domain shift", "distribution shift"],
            "domain_adaptation": ["domain adaptation"],
            "domain_generalization": ["domain generalization"],
            "noisy_labels": ["noisy labels", "label noise"],
            "weak_supervision": ["weak supervision"],
            "active_learning": ["active learning"],
            "label_efficient": ["label-efficient", "label efficient"],
            "limited_labels": ["limited labels", "scarce labels", "few labeled examples"],
        },
        "positive_weak": {
            "semi_supervised": ["semi supervised", "semi-supervised"],
            "self_supervised": ["self supervised", "self-supervised"],
            "unsupervised": ["unsupervised"],
        },
        "negative": {
            "opinion": ["position paper", "opinion", "perspective", "viewpoint", "position"]
        },
        "required_any": {
            "few_shot",
            "low_shot",
            "zero_shot",
            "long_tail",
            "imbalanced",
            "domain_shift",
            "domain_adaptation",
            "domain_generalization",
            "noisy_labels",
            "weak_supervision",
            "active_learning",
            "label_efficient",
            "limited_labels",
            "semi_supervised",
            "self_supervised",
            "unsupervised",
        },
        "anchor_families": {
            "few_shot",
            "low_shot",
            "zero_shot",
            "long_tail",
            "imbalanced",
            "domain_shift",
            "domain_adaptation",
            "domain_generalization",
            "noisy_labels",
            "weak_supervision",
            "active_learning",
            "label_efficient",
            "limited_labels",
        },
        "min_score": 4,
    },
}


@dataclass
class RequestPacer:
    min_interval_seconds: float
    next_allowed_monotonic: float = 0.0

    def wait(self) -> None:
        now = time.monotonic()
        if now < self.next_allowed_monotonic:
            time.sleep(self.next_allowed_monotonic - now)
            now = time.monotonic()
        self.next_allowed_monotonic = now + self.min_interval_seconds


@dataclass
class YearStats:
    year: int
    fetched: int = 0
    pi_matched: int = 0
    date_passed: int = 0
    new_added: int = 0


@dataclass
class CandidatePaper:
    paper: Dict[str, Any]
    source_year: int
    dedupe_key: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Update _data/publications.yml from Semantic Scholar search.")
    parser.add_argument("--dry-run", action="store_true", help="Run fetch/filter/dedupe and print stats only.")
    parser.add_argument(
        "--recompute-suggested-themes",
        action="store_true",
        help="Delete and rebuild suggested_themes for all existing YAML entries, then exit without fetching new papers.",
    )
    parser.add_argument(
        "--apply-suggested-themes",
        action="store_true",
        help="When recomputing, also replace each publication's themes with the newly generated suggested_themes.",
    )
    parser.add_argument(
        "--max-years",
        type=int,
        default=None,
        help="Only scan this many most recent years (default: all years from current year to LAB_START_DATE year).",
    )
    return parser.parse_args()


def normalize_name(name: Optional[str]) -> str:
    if not name:
        return ""
    lowered = name.lower()
    cleaned = NAME_NORMALIZE_RE.sub(" ", lowered)
    collapsed = SPACE_RE.sub(" ", cleaned).strip()
    return collapsed


def normalize_title(title: Optional[str]) -> str:
    if not title:
        return ""
    lowered = title.lower()
    cleaned = TITLE_NORMALIZE_RE.sub("", lowered)
    return cleaned.strip()


def parse_iso_date(value: Optional[str]) -> Optional[date]:
    if not value:
        return None
    raw = value.strip()
    if not raw:
        return None
    try:
        return datetime.strptime(raw[:10], "%Y-%m-%d").date()
    except ValueError:
        return None


def year_from_paper(paper: Dict[str, Any]) -> Optional[int]:
    year = paper.get("year")
    if year is not None:
        try:
            return int(year)
        except (TypeError, ValueError):
            pass
    publication_date = parse_iso_date(paper.get("publicationDate"))
    if publication_date:
        return publication_date.year
    return None


def build_search_fields(include_tldr: bool = True) -> str:
    fields = list(SEARCH_BASE_FIELDS)
    if include_tldr:
        fields.extend(SEARCH_OPTIONAL_FIELDS)
    return ",".join(fields)


def build_detail_fields(include_tldr: bool = True) -> str:
    fields = list(DETAIL_BASE_FIELDS)
    if include_tldr:
        fields.extend(SEARCH_OPTIONAL_FIELDS)
    return ",".join(fields)


def normalize_match_text(value: Optional[str]) -> str:
    if not value:
        return ""
    lowered = value.lower()
    cleaned = MATCH_NORMALIZE_RE.sub(" ", lowered)
    return SPACE_RE.sub(" ", cleaned).strip()


def phrase_family_matches(text: str, phrases: List[str]) -> bool:
    if not text:
        return False
    padded_text = f" {text} "
    for phrase in phrases:
        normalized_phrase = normalize_match_text(phrase)
        if normalized_phrase and f" {normalized_phrase} " in padded_text:
            return True
    return False


def extract_tldr_text(record: Dict[str, Any]) -> str:
    tldr = record.get("tldr")
    if isinstance(tldr, dict):
        return str(tldr.get("text") or "").strip()
    if isinstance(tldr, str):
        return tldr.strip()
    return ""


def normalize_publication_types(record: Dict[str, Any]) -> str:
    publication_types = record.get("publicationTypes") or []
    if not isinstance(publication_types, list):
        publication_types = [publication_types]
    joined = " ".join(str(item) for item in publication_types if str(item).strip())
    return normalize_match_text(joined)


def build_theme_sources(record: Dict[str, Any], venue_key: str) -> Dict[str, str]:
    return {
        "title": normalize_match_text(record.get("title")),
        "tldr": normalize_match_text(extract_tldr_text(record)),
        "abstract": normalize_match_text(record.get("abstract")),
        "venue": normalize_match_text(record.get(venue_key)),
        "publication_type": normalize_publication_types(record),
    }


def matched_family_weights(
    source_texts: Dict[str, str],
    family_rules: Dict[str, List[str]],
) -> Dict[str, int]:
    matched: Dict[str, int] = {}
    for family_name, phrases in family_rules.items():
        strongest_weight = 0
        for source_name, text in source_texts.items():
            if phrase_family_matches(text, phrases):
                strongest_weight = max(strongest_weight, SOURCE_WEIGHTS[source_name])
        if strongest_weight:
            matched[family_name] = strongest_weight
    return matched


def passes_theme_gates(theme_name, rules, strong_matches, weak_matches, score):
    present = set(strong_matches) | set(weak_matches)

    required_any = set(rules.get("required_any") or set())
    if required_any and not (present & required_any):
        return False

    anchor_families = set(rules.get("anchor_families") or set())
    if anchor_families and not (present & anchor_families):
        return False

    strong_or_two_weak = set(rules.get("require_strong_or_two_weak_from") or set())
    if strong_or_two_weak:
        strong_present = set(strong_matches) & strong_or_two_weak
        weak_present = set(weak_matches) & strong_or_two_weak
        if not strong_present and len(weak_present) < 2:
            return False

    if theme_name == "Biodiversity Monitoring":
        if present and present <= {"species", "animal", "fauna", "monitoring"}:
            return False

    return score >= int(rules.get("min_score", 4))


def classify_themes(record: Dict[str, Any], venue_key: str) -> Tuple[List[str], Dict[str, Dict[str, Any]]]:
    source_texts = build_theme_sources(record, venue_key=venue_key)
    theme_debug: Dict[str, Dict[str, Any]] = {}
    suggestions: List[str] = []

    for theme_name, rules in THEME_RULES.items():
        strong_matches = matched_family_weights(source_texts, rules.get("positive_strong", {}))
        weak_matches = matched_family_weights(source_texts, rules.get("positive_weak", {}))
        negative_matches = matched_family_weights(source_texts, rules.get("negative", {}))

        positive_score = (2 * sum(strong_matches.values())) + sum(weak_matches.values())
        negative_score = 2 * sum(negative_matches.values())
        total_score = positive_score - negative_score

        if passes_theme_gates(theme_name, rules, strong_matches, weak_matches, total_score):
            suggestions.append(theme_name)

        theme_debug[theme_name] = {
            "score": total_score,
            "strong_families": sorted(strong_matches.keys()),
            "weak_families": sorted(weak_matches.keys()),
            "negative_families": sorted(negative_matches.keys()),
        }

    return suggestions, theme_debug


def suggest_themes_for_paper(paper: Dict[str, Any]) -> List[str]:
    suggestions, _ = classify_themes(paper, venue_key="venue")
    return suggestions


def suggest_themes_for_entry(entry: Dict[str, Any]) -> List[str]:
    suggestions, _ = classify_themes(entry, venue_key="journal")
    return suggestions


def normalize_doi(value: Optional[str]) -> Optional[str]:
    if not value:
        return None
    doi = value.strip()
    doi = re.sub(r"^https?://(dx\.)?doi\.org/", "", doi, flags=re.IGNORECASE)
    doi = doi.strip().lower()
    return doi or None


def extract_doi_from_url(url: Optional[str]) -> Optional[str]:
    if not url:
        return None
    match = DOI_PATTERN.search(url)
    return normalize_doi(match.group(0)) if match else None


def extract_s2_paper_id_from_url(url: Optional[str]) -> Optional[str]:
    if not url:
        return None
    try:
        parsed = urlparse(url)
    except ValueError:
        return None
    path_parts = [part for part in parsed.path.split("/") if part]
    if "paper" not in path_parts:
        return None
    if not path_parts:
        return None
    candidate = path_parts[-1].strip()
    return candidate or None


def get_doi_from_paper(paper: Dict[str, Any]) -> Optional[str]:
    external_ids = paper.get("externalIds") or {}
    doi = normalize_doi(external_ids.get("DOI") or external_ids.get("doi"))
    if doi:
        return doi
    return extract_doi_from_url(paper.get("url"))


def paper_title_year_key(paper: Dict[str, Any]) -> Optional[str]:
    title_key = normalize_title(paper.get("title"))
    year = year_from_paper(paper)
    if not title_key or year is None:
        return None
    return f"{title_key}::{year}"


def existing_entry_title_year_key(entry: Dict[str, Any]) -> Optional[str]:
    title_key = normalize_title(entry.get("title"))
    year = entry.get("year")
    try:
        year_int = int(year)
    except (TypeError, ValueError):
        year_int = None
    if not title_key or year_int is None:
        return None
    return f"{title_key}::{year_int}"


def split_header_and_publications(raw_text: str) -> Tuple[str, List[Dict[str, Any]]]:
    lines = raw_text.splitlines()
    first_publication_index = None
    for idx, line in enumerate(lines):
        if line.lstrip().startswith("- title:"):
            first_publication_index = idx
            break

    if first_publication_index is None:
        header = raw_text
        if header and not header.endswith("\n"):
            header += "\n"
        return header, []

    header = "\n".join(lines[:first_publication_index])
    if header and not header.endswith("\n"):
        header += "\n"

    body = "\n".join(lines[first_publication_index:])
    publications = yaml.safe_load(body) or []
    if not isinstance(publications, list):
        raise ValueError("Expected _data/publications.yml to contain a top-level list.")
    return header, publications


def make_session() -> requests.Session:
    session = requests.Session()
    headers = {"Accept": "application/json", "User-Agent": USER_AGENT}
    api_key = (os.getenv("S2_API_KEY") or "").strip()
    if api_key:
        headers["x-api-key"] = api_key
    session.headers.update(headers)
    return session


def _retry_after_seconds(response: requests.Response, default_seconds: int = 2) -> int:
    raw = (response.headers.get("Retry-After") or "").strip()
    if not raw:
        return default_seconds
    try:
        return max(1, int(float(raw)))
    except ValueError:
        pass
    try:
        retry_dt = parsedate_to_datetime(raw)
        delta_seconds = int((retry_dt - datetime.now(retry_dt.tzinfo)).total_seconds())
        return max(1, delta_seconds)
    except Exception:
        return default_seconds


def _backoff_seconds(attempt: int, floor_seconds: float = 0.0) -> float:
    base = min(60.0, float(2 ** max(0, attempt - 1)))
    wait = max(floor_seconds, base)
    jitter = random.uniform(0.0, 0.75)
    return min(120.0, wait + jitter)


def request_json_with_retries(
    session: requests.Session,
    pacer: RequestPacer,
    url: str,
    params: Dict[str, Any],
    max_retries: int = MAX_RETRIES,
) -> Dict[str, Any]:
    last_err: Exception = RuntimeError("Request failed before receiving any response.")

    for attempt in range(1, max_retries + 1):
        try:
            pacer.wait()
            response = session.get(url, params=params, timeout=REQUEST_TIMEOUT_SECONDS)
        except requests.RequestException as exc:
            last_err = exc
            if attempt == max_retries:
                break
            time.sleep(_backoff_seconds(attempt))
            continue

        if response.status_code == 429:
            retry_after = float(_retry_after_seconds(response))
            backoff = _backoff_seconds(attempt)
            sleep_seconds = max(retry_after, backoff)
            last_err = RuntimeError(
                f"HTTP 429 rate-limited. Retry-After={retry_after}. Body: {response.text[:200]!r}"
            )
            if attempt == max_retries:
                break
            time.sleep(sleep_seconds)
            continue

        if response.status_code in (500, 502, 503, 504):
            last_err = RuntimeError(f"HTTP {response.status_code}: {response.text[:200]!r}")
            if attempt == max_retries:
                break
            time.sleep(_backoff_seconds(attempt))
            continue

        if 400 <= response.status_code < 500:
            last_err = RuntimeError(f"HTTP {response.status_code}: {response.text[:200]!r}")
            break

        try:
            response.raise_for_status()
        except requests.RequestException as exc:
            last_err = exc
            if attempt == max_retries:
                break
            time.sleep(_backoff_seconds(attempt))
            continue

        try:
            parsed = response.json()
            if isinstance(parsed, dict):
                return parsed
            last_err = RuntimeError(f"Unexpected JSON type {type(parsed)} for params={params!r}")
        except (ValueError, json.JSONDecodeError) as exc:
            last_err = RuntimeError(
                f"JSON decode failed (HTTP {response.status_code}). Body starts: {response.text[:200]!r}"
            )
            if attempt == max_retries:
                raise last_err from exc

        if attempt == max_retries:
            break
        time.sleep(_backoff_seconds(attempt))

    raise RuntimeError(f"Failed after {max_retries} attempts: {last_err}") from last_err


def is_unsupported_tldr_error(exc: Exception) -> bool:
    message = str(exc).lower()
    return "400" in message and "tldr" in message


def is_http_not_found_error(exc: Exception) -> bool:
    return "404" in str(exc)


def is_non_systemic_lookup_error(exc: Exception) -> bool:
    message = str(exc)
    return "400" in message or "404" in message


def request_paper_details_by_id(
    session: requests.Session,
    pacer: RequestPacer,
    paper_id: str,
    include_tldr: bool = True,
) -> Dict[str, Any]:
    encoded_id = quote(paper_id, safe="")
    return request_json_with_retries(
        session=session,
        pacer=pacer,
        url=f"{PAPER_ENDPOINT}/{encoded_id}",
        params={"fields": build_detail_fields(include_tldr=include_tldr)},
        max_retries=RECOMPUTE_LOOKUP_MAX_RETRIES,
    )


def search_paper_by_title_year(
    session: requests.Session,
    pacer: RequestPacer,
    title: str,
    year: Optional[int],
    include_tldr: bool = True,
) -> Optional[Dict[str, Any]]:
    params: Dict[str, Any] = {
        "query": title,
        "fields": build_detail_fields(include_tldr=include_tldr),
        "limit": 10,
        "offset": 0,
    }
    if year is not None:
        params["year"] = year

    payload = request_json_with_retries(
        session=session,
        pacer=pacer,
        url=SEARCH_ENDPOINT,
        params=params,
        max_retries=RECOMPUTE_LOOKUP_MAX_RETRIES,
    )
    results = payload.get("data") or []
    if not isinstance(results, list):
        return None

    normalized_target_title = normalize_title(title)
    exact_year_matches: List[Dict[str, Any]] = []
    exact_title_matches: List[Dict[str, Any]] = []

    for candidate in results:
        candidate_title = normalize_title(candidate.get("title"))
        if candidate_title != normalized_target_title:
            continue
        exact_title_matches.append(candidate)
        candidate_year = year_from_paper(candidate)
        if year is not None and candidate_year == year:
            exact_year_matches.append(candidate)

    if exact_year_matches:
        return sorted(exact_year_matches, key=paper_sort_key)[0]
    if exact_title_matches:
        return sorted(exact_title_matches, key=paper_sort_key)[0]
    return None


def fetch_live_theme_record(
    session: requests.Session,
    pacer: RequestPacer,
    entry: Dict[str, Any],
) -> Tuple[Optional[Dict[str, Any]], Optional[str], bool, bool]:
    include_tldr = True
    had_request_error = False
    title = (entry.get("title") or "").strip()
    year_value = entry.get("year")
    try:
        year = int(year_value) if year_value is not None else None
    except (TypeError, ValueError):
        year = None

    lookup_attempts: List[Tuple[str, str]] = []

    doi = normalize_doi(entry.get("doi")) or extract_doi_from_url(entry.get("url"))
    if doi:
        lookup_attempts.append(("doi", f"DOI:{doi}"))

    s2_paper_id = extract_s2_paper_id_from_url(entry.get("url"))
    if s2_paper_id:
        lookup_attempts.append(("paper_id", s2_paper_id))

    for source, paper_id in lookup_attempts:
        try:
            record = request_paper_details_by_id(
                session=session,
                pacer=pacer,
                paper_id=paper_id,
                include_tldr=include_tldr,
            )
            return record, source, include_tldr, had_request_error
        except RuntimeError as exc:
            if include_tldr and is_unsupported_tldr_error(exc):
                include_tldr = False
                try:
                    record = request_paper_details_by_id(
                        session=session,
                        pacer=pacer,
                        paper_id=paper_id,
                        include_tldr=include_tldr,
                    )
                    return record, source, include_tldr, had_request_error
                except RuntimeError as retry_exc:
                    if is_non_systemic_lookup_error(retry_exc):
                        continue
                    had_request_error = True
                    return None, None, include_tldr, had_request_error
            if is_non_systemic_lookup_error(exc):
                continue
            had_request_error = True
            return None, None, include_tldr, had_request_error

    if not title:
        return None, None, include_tldr, had_request_error

    try:
        record = search_paper_by_title_year(
            session=session,
            pacer=pacer,
            title=title,
            year=year,
            include_tldr=include_tldr,
        )
        if record is not None:
            return record, "title_year_search", include_tldr, had_request_error
    except RuntimeError as exc:
        if include_tldr and is_unsupported_tldr_error(exc):
            include_tldr = False
            try:
                record = search_paper_by_title_year(
                    session=session,
                    pacer=pacer,
                    title=title,
                    year=year,
                    include_tldr=include_tldr,
                )
                if record is not None:
                    return record, "title_year_search", include_tldr, had_request_error
            except RuntimeError as retry_exc:
                if not is_non_systemic_lookup_error(retry_exc):
                    had_request_error = True
        elif not is_non_systemic_lookup_error(exc):
            had_request_error = True

    return None, None, include_tldr, had_request_error


def author_matches_paper(paper: Dict[str, Any], normalized_pi_name: str, s2_author_id: Optional[str]) -> bool:
    normalized_author_id = str(s2_author_id).strip() if s2_author_id else None
    for author in paper.get("authors") or []:
        author_name = normalize_name(author.get("name"))
        author_id = str(author.get("authorId")).strip() if author.get("authorId") is not None else None
        if normalized_author_id:
            if author_id == normalized_author_id or author_name == normalized_pi_name:
                return True
        elif author_name == normalized_pi_name:
            return True
    return False


def passes_cutoff(paper: Dict[str, Any], cutoff_date: date, cutoff_year: int) -> bool:
    publication_date = parse_iso_date(paper.get("publicationDate"))
    if publication_date:
        return publication_date >= cutoff_date
    year = year_from_paper(paper)
    if year is None:
        return False
    return year >= cutoff_year


def best_record_score(paper: Dict[str, Any]) -> Tuple[int, int, int, int]:
    has_doi = 1 if get_doi_from_paper(paper) else 0
    publication_date = parse_iso_date(paper.get("publicationDate"))
    has_pub_date = 1 if publication_date else 0
    has_venue_or_url = 1 if (
        paper.get("venue")
        or paper.get("url")
        or ((paper.get("openAccessPdf") or {}).get("url"))
    ) else 0
    date_rank = int(publication_date.strftime("%Y%m%d")) if publication_date else 0
    return has_doi, has_pub_date, has_venue_or_url, date_rank


def dedupe_key_for_paper(paper: Dict[str, Any]) -> Optional[str]:
    doi = get_doi_from_paper(paper)
    if doi:
        return f"doi::{doi}"
    title_year = paper_title_year_key(paper)
    if title_year:
        return f"title_year::{title_year}"
    return None


def fetch_search_papers_year_by_year(
    session: requests.Session,
    pacer: RequestPacer,
    pi_name: str,
    normalized_pi_name: str,
    cutoff_date: date,
    s2_author_id: Optional[str],
    max_years: Optional[int],
) -> Tuple[List[CandidatePaper], Dict[int, YearStats]]:
    current_year = date.today().year
    cutoff_year = cutoff_date.year
    years = list(range(current_year, cutoff_year - 1, -1))
    if max_years is not None:
        years = years[:max_years]

    stats_by_year = {year: YearStats(year=year) for year in years}
    deduped: Dict[str, CandidatePaper] = {}
    include_tldr = True

    for year in years:
        stats = stats_by_year[year]
        offset = 0
        consecutive_zero_pi_pages = 0

        while True:
            try:
                payload = request_json_with_retries(
                    session=session,
                    pacer=pacer,
                    url=SEARCH_ENDPOINT,
                    params={
                        "query": pi_name,
                        "year": year,
                        "fields": build_search_fields(include_tldr=include_tldr),
                        "offset": offset,
                        "limit": PAGE_SIZE,
                    },
                )
            except RuntimeError as exc:
                if include_tldr and is_unsupported_tldr_error(exc):
                    print("Semantic Scholar search rejected the optional 'tldr' field; continuing without it.")
                    include_tldr = False
                    continue
                raise

            page = payload.get("data") or []
            if not isinstance(page, list):
                page = []

            if not page:
                break

            stats.fetched += len(page)
            pi_matches = [p for p in page if author_matches_paper(p, normalized_pi_name, s2_author_id)]
            stats.pi_matched += len(pi_matches)

            if pi_matches:
                consecutive_zero_pi_pages = 0
            else:
                consecutive_zero_pi_pages += 1

            date_passed = [p for p in pi_matches if passes_cutoff(p, cutoff_date=cutoff_date, cutoff_year=cutoff_year)]
            stats.date_passed += len(date_passed)

            for paper in date_passed:
                dedupe_key = dedupe_key_for_paper(paper)
                if not dedupe_key:
                    continue

                candidate = CandidatePaper(paper=paper, source_year=year, dedupe_key=dedupe_key)
                existing = deduped.get(dedupe_key)
                if existing is None or best_record_score(candidate.paper) > best_record_score(existing.paper):
                    deduped[dedupe_key] = candidate

            if consecutive_zero_pi_pages >= 2:
                break

            if len(page) < PAGE_SIZE:
                break

            relevance = (stats.pi_matched / stats.fetched) if stats.fetched else 0.0
            if stats.fetched >= PAGE_SIZE and relevance < LOW_RELEVANCE_THRESHOLD:
                break

            offset += len(page)

    return list(deduped.values()), stats_by_year


def map_paper_to_yaml_entry(paper: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    title = (paper.get("title") or "").strip()
    if not title:
        return None

    year = year_from_paper(paper)
    if year is None:
        return None

    authors = [
        (author.get("name") or "").strip()
        for author in (paper.get("authors") or [])
        if (author.get("name") or "").strip()
    ]
    authors_str = ", ".join(authors) if authors else "Unknown authors"
    venue = (paper.get("venue") or "").strip() or "Unknown venue"

    doi = get_doi_from_paper(paper)
    if doi:
        url = f"https://doi.org/{doi}"
    else:
        url = (paper.get("url") or "").strip()
        if not url:
            url = ((paper.get("openAccessPdf") or {}).get("url") or "").strip()
    if not url:
        return None

    entry: Dict[str, Any] = {
        "title": title,
        "authors": authors_str,
        "journal": venue,
        "year": int(year),
        "url": url,
        "themes": [],
        "suggested_themes": suggest_themes_for_paper(paper),
    }
    if doi:
        entry["doi"] = doi
    return entry


def existing_keys(publications: List[Dict[str, Any]]) -> Tuple[set, set]:
    doi_keys = set()
    title_year_keys = set()
    for entry in publications:
        doi = normalize_doi(entry.get("doi")) or extract_doi_from_url(entry.get("url"))
        if doi:
            doi_keys.add(doi)
            continue
        title_year = existing_entry_title_year_key(entry)
        if title_year:
            title_year_keys.add(title_year)
    return doi_keys, title_year_keys


def paper_sort_key(paper: Dict[str, Any]) -> Tuple[int, int, str]:
    year = year_from_paper(paper) or 0
    publication_date = parse_iso_date(paper.get("publicationDate"))
    if publication_date:
        date_rank = int(publication_date.strftime("%Y%m%d"))
    else:
        date_rank = (year * 10000) + 101
    title_rank = (paper.get("title") or "").strip().lower()
    return (-date_rank, -year, title_rank)


def sort_recent_first(candidates: List[CandidatePaper]) -> List[CandidatePaper]:
    return sorted(candidates, key=lambda c: paper_sort_key(c.paper))


def render_output(header: str, entries: List[Dict[str, Any]]) -> str:
    if not entries:
        if header.strip():
            return f"{header.rstrip()}\n"
        return ""

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


def format_publications_updated_date(updated_on: date) -> str:
    return f"{updated_on.strftime('%B')} {updated_on.day}, {updated_on.year}"


def render_publications_meta(updated_on: date) -> str:
    body = yaml.safe_dump(
        {"updated": format_publications_updated_date(updated_on)},
        sort_keys=False,
        allow_unicode=True,
        default_flow_style=False,
        width=1000,
    ).rstrip()
    return f"{body}\n"


def write_text_if_changed(path: Path, text: str) -> bool:
    if path.exists() and path.read_text(encoding="utf-8") == text:
        return False
    path.write_text(text, encoding="utf-8")
    return True


def recompute_suggested_themes(
    publications: List[Dict[str, Any]],
    session: requests.Session,
    pacer: RequestPacer,
    apply_suggested_themes: bool = False,
) -> Dict[str, int]:
    scanned_count = len(publications)
    cleared_count = 0
    non_empty_count = 0
    enriched_count = 0
    fallback_only_count = 0
    abstract_enriched_count = 0
    applied_count = 0
    tldr_disabled_noted = 0
    systemic_lookup_failures = 0
    live_lookup_disabled = False

    for entry in publications:
        if "themes" not in entry or entry.get("themes") is None:
            entry["themes"] = []

        if "suggested_themes" in entry:
            cleared_count += 1
            del entry["suggested_themes"]
        entry["suggested_themes"] = []

        live_record: Optional[Dict[str, Any]] = None
        had_request_error = False
        if not live_lookup_disabled:
            try:
                live_record, _, include_tldr, had_request_error = fetch_live_theme_record(
                    session=session,
                    pacer=pacer,
                    entry=entry,
                )
                if not include_tldr and not tldr_disabled_noted:
                    print("Semantic Scholar detail lookup rejected the optional 'tldr' field; continuing without it.")
                    tldr_disabled_noted = 1
            except (requests.RequestException, RuntimeError):
                live_record = None
                had_request_error = True

        if had_request_error:
            systemic_lookup_failures += 1
            if systemic_lookup_failures >= 2 and not live_lookup_disabled:
                print("Repeated Semantic Scholar lookup failures detected; using local metadata fallback for remaining publications.")
                live_lookup_disabled = True
        elif live_record is not None:
            systemic_lookup_failures = 0

        if live_record:
            enriched_count += 1
            if (live_record.get("abstract") or "").strip():
                abstract_enriched_count += 1
            entry["suggested_themes"] = suggest_themes_for_paper(live_record)
        else:
            fallback_only_count += 1

        if entry["suggested_themes"]:
            non_empty_count += 1
        if apply_suggested_themes:
            entry["themes"] = list(entry["suggested_themes"])
            applied_count += 1

    return {
        "scanned_count": scanned_count,
        "cleared_count": cleared_count,
        "non_empty_count": non_empty_count,
        "enriched_count": enriched_count,
        "fallback_only_count": fallback_only_count,
        "abstract_enriched_count": abstract_enriched_count,
        "applied_count": applied_count,
    }


def validate_env() -> Tuple[str, date, Optional[str]]:
    pi_name = (os.getenv("PI_NAME") or DEFAULT_PI_NAME).strip()
    if not pi_name:
        raise ValueError("Missing required environment variable: PI_NAME")

    lab_start_raw = (os.getenv("LAB_START_DATE") or DEFAULT_LAB_START_DATE).strip()
    if not lab_start_raw:
        raise ValueError("Missing required environment variable: LAB_START_DATE")

    lab_start_date = parse_iso_date(lab_start_raw)
    if not lab_start_date:
        raise ValueError("Invalid LAB_START_DATE format. Expected YYYY-MM-DD.")

    s2_author_id = (os.getenv("S2_AUTHOR_ID") or "").strip() or None
    return pi_name, lab_start_date, s2_author_id


def main() -> int:
    args = parse_args()

    if args.max_years is not None and args.max_years <= 0:
        print("--max-years must be a positive integer.")
        return 1
    if args.apply_suggested_themes and not args.recompute_suggested_themes:
        print("--apply-suggested-themes can only be used together with --recompute-suggested-themes.")
        return 1

    try:
        pi_name, lab_start_date, s2_author_id = validate_env()
    except ValueError as exc:
        print(str(exc))
        return 1

    repo_root = Path(__file__).resolve().parents[1]
    publications_path = repo_root / PUBLICATIONS_PATH
    publications_meta_path = repo_root / PUBLICATIONS_META_PATH
    if not publications_path.exists():
        print(f"File not found: {publications_path}")
        return 1

    raw_text = publications_path.read_text(encoding="utf-8")
    header, existing_publications = split_header_and_publications(raw_text)
    publications_meta_text = render_publications_meta(date.today())

    if args.recompute_suggested_themes:
        pacer = RequestPacer(min_interval_seconds=MIN_REQUEST_INTERVAL_SECONDS)
        session = make_session()
        try:
            recompute_stats = recompute_suggested_themes(
                existing_publications,
                session=session,
                pacer=pacer,
                apply_suggested_themes=args.apply_suggested_themes,
            )
        finally:
            session.close()

        print(f"Publications scanned for recompute: {recompute_stats['scanned_count']}")
        print(f"Existing suggested_themes cleared: {recompute_stats['cleared_count']}")
        print(f"Publications enriched from Semantic Scholar: {recompute_stats['enriched_count']}")
        print(f"Publications with abstract available from Semantic Scholar: {recompute_stats['abstract_enriched_count']}")
        print(f"Publications classified via fallback-only metadata: {recompute_stats['fallback_only_count']}")
        print(f"Publications with non-empty regenerated suggestions: {recompute_stats['non_empty_count']}")
        if args.apply_suggested_themes:
            print(f"Publications with themes replaced from suggestions: {recompute_stats['applied_count']}")
        print("Sample regenerated suggestions:")
        for entry in existing_publications[:10]:
            themes = entry.get("suggested_themes") or []
            print(f"- {entry.get('title', '').strip()} | suggested_themes={themes}")
        if args.dry_run:
            print("Dry run enabled: no file changes written.")
            return 0

        updated_text = render_output(header=header, entries=existing_publications)
        publications_changed = updated_text != raw_text
        meta_changed = write_text_if_changed(publications_meta_path, publications_meta_text)
        if publications_changed:
            publications_path.write_text(updated_text, encoding="utf-8")

        if not publications_changed and not meta_changed:
            print("No changes made.")
            return 0

        if publications_changed and meta_changed:
            print(f"Updated {publications_path} with recomputed suggested_themes and refreshed {publications_meta_path}.")
        elif publications_changed:
            print(f"Updated {publications_path} with recomputed suggested_themes.")
        else:
            print(f"Refreshed {publications_meta_path}.")
        return 0

    existing_doi_keys, existing_title_year_keys = existing_keys(existing_publications)

    normalized_pi_name = normalize_name(pi_name)
    pacer = RequestPacer(min_interval_seconds=MIN_REQUEST_INTERVAL_SECONDS)
    session = make_session()
    try:
        candidates, stats_by_year = fetch_search_papers_year_by_year(
            session=session,
            pacer=pacer,
            pi_name=pi_name,
            normalized_pi_name=normalized_pi_name,
            cutoff_date=lab_start_date,
            s2_author_id=s2_author_id,
            max_years=args.max_years,
        )
    except (requests.RequestException, RuntimeError) as exc:
        print(f"Failed to fetch from Semantic Scholar: {exc}")
        if not (os.getenv("S2_API_KEY") or "").strip():
            print("Tip: set S2_API_KEY to increase Semantic Scholar API rate limits.")
        return 1
    finally:
        session.close()

    candidates_sorted = sort_recent_first(candidates)
    new_entries: List[Dict[str, Any]] = []
    duplicates_skipped = 0

    for candidate in candidates_sorted:
        mapped = map_paper_to_yaml_entry(candidate.paper)
        if not mapped:
            continue

        doi = normalize_doi(mapped.get("doi")) or extract_doi_from_url(mapped.get("url"))
        title_year = existing_entry_title_year_key(mapped)

        duplicate_existing = False
        if doi and doi in existing_doi_keys:
            duplicate_existing = True
        elif title_year and title_year in existing_title_year_keys:
            duplicate_existing = True

        if duplicate_existing:
            duplicates_skipped += 1
            continue

        new_entries.append(mapped)
        stats_by_year[candidate.source_year].new_added += 1
        if doi:
            existing_doi_keys.add(doi)
        if title_year:
            existing_title_year_keys.add(title_year)

    merged_entries = new_entries + list(existing_publications)

    print("Per-year stats (fetched, PI-matched, date-passed, new-added):")
    for year in sorted(stats_by_year.keys(), reverse=True):
        stats = stats_by_year[year]
        print(
            f"- {year}: fetched={stats.fetched}, PI-matched={stats.pi_matched}, "
            f"date-passed={stats.date_passed}, new-added={stats.new_added}"
        )

    total_fetched = sum(s.fetched for s in stats_by_year.values())
    total_pi_matched = sum(s.pi_matched for s in stats_by_year.values())
    total_date_passed = sum(s.date_passed for s in stats_by_year.values())
    print(f"Total fetched papers: {total_fetched}")
    print(f"Total PI-matched papers: {total_pi_matched}")
    print(f"Total papers passing date cutoff: {total_date_passed}")
    print(f"New papers to add: {len(new_entries)}")
    print(f"Duplicates skipped against existing YAML: {duplicates_skipped}")

    print("Top 10 most recent papers after filtering:")
    for candidate in candidates_sorted[:10]:
        title = (candidate.paper.get("title") or "").strip()
        publication_date = candidate.paper.get("publicationDate") or "n/a"
        year = year_from_paper(candidate.paper)
        year_text = str(year) if year is not None else "n/a"
        print(f"- {title} | publicationDate={publication_date} | year={year_text}")

    if args.dry_run:
        print("Dry run enabled: no file changes written.")
        return 0

    updated_text = render_output(header=header, entries=merged_entries)
    publications_changed = updated_text != raw_text
    meta_changed = write_text_if_changed(publications_meta_path, publications_meta_text)

    if not publications_changed and not meta_changed:
        print("No changes made.")
        return 0

    if publications_changed:
        publications_path.write_text(updated_text, encoding="utf-8")

    if publications_changed and meta_changed:
        print(f"Updated {publications_path} with {len(new_entries)} new entries and refreshed {publications_meta_path}.")
    elif publications_changed:
        print(f"Updated {publications_path} with {len(new_entries)} new entries.")
    else:
        print(f"Refreshed {publications_meta_path}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
