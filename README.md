# BeeryLab Website

This is the repo for the website of the BeeryLab at MIT. It is modified on top of a Jekyll template developed by the Allan Lab.

## Contributor Guide

All Coley Group members are free to make changes and additions to the website (such as adding/removing themselves to/from the "People" page) through this repo, pending approval. The existing templating combined with the following guide should hopefully make this process as painless as possible. Stylistic or template change suggestions are also welcome but may require navigating some messy templates or CSS.

Before you do anything, make sure you have [Git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git) installed on your machine. Then, **(1)** fork this repo and **(2)** clone the forked repo to your local machine with the command:
```bash
$ git clone https://github.com/{your_username}/coley.mit.edu.git
```

### Local deployment

If you are making non-trivial changes (i.e. beyond just adding yourself to the "People" page), it is highly encouraged to locally deploy the website on your machine to preview the website before making a pull request. First, install Jekyll if you have not done so, following [the official guide](https://jekyllrb.com/docs/installation/#requirements) corresponding to your OS. 

In the folder corresponding to your cloned repo, simply run the following to serve the website at `http://localhost:4000`.
```bash
$ jekyll serve
```

### Making changes and pull requests

First, working in your forked repo, create and checkout a new branch (give it a descriptive name) with the command
```bash
$ git checkout -b BRANCH_NAME
```
After you make your changes, commit and push your changes to the branch:
```bash
$ git add .
$ git commit -m "COMMIT MESSAGE"
$ git push --set-upstream origin BRANCH_NAME
```
Finally, perform a pull request so that your changes can be reviewed and merged into the main repo. This can be done easily through the Github UI on the browser from your fork repo page.

### Adding you or someone else to the "People" page

Adding yourself to the People page is very simple!
1. Upload an image of yourself to `images/teampic/` with the format `{firstname}_{lastname}.[png|jpg|jpeg]`. **Please crop your image to a square**.
2. Navigate to the `_data/` folder and locate the `.yml` file that matches your position in the group (for instance, if you are a grad student, open `grad_students.yml`). 
3. Add all relevant information in the `.yml` file. 
    - Fill out `name` and `email` at minimum, with optional URLs provided in `twitter`, `linkedin`, `github`, and/or `website` fields.
    - Add a short biography for the `description` field.

That's it! Go ahead and make a pull request when you are satisfied.

### Adding publications

Some instructions for adding publications and a template are at the top of the (`_data/publications.yml`) file for your convenience. The main format for a citation is as follows:
- Author list. Linked Title. *Journal*. Volume(Issue), Pages. (Year) DOI/preprint: DOI/preprint_ID.

The minimum required fields are: `title`, `authors`, `journal`, `year`, `url`, `themes`.
- For journal papers, be sure to at least include `doi`
- For preprints, be sure to at least include `preprint`, `preprint_url`
- For conference papers, be sure to at least include `preprint_url`

If the `preprint_url` field is filled out, then the preprint button will appear under the citation.

Further, research themes should be added for each paper and they will appear as tags below the citation. The available themes and their associated colors are found in (`_data/research_themes.yml`). Currently these themes are: 
- Computer Vision
- Deep Learning
- Datasets & Benchmarks
- Biodiversity Monitoring
- Scientific Workflows
- Environmental Sensing
- Multimodal Modeling
- Interpretable & Reliable AI
- Data-Limited Learning

Note: There are slight nuances with respect to the `doi` and `preprint` fields since the former supercedes the latter.
- For preprints
    - Do NOT include the `doi` field
    - DO include the `preprint` and related fields.
- For conference papers
    - Do NOT include `doi` OR `preprint` fields.
    - DO include `url`, `preprint_url`, `preprint_site`, `preprint_year`.

### Automatic publication updates (Semantic Scholar)

Publications can be synced automatically from Semantic Scholar with:
```bash
python3 scripts/update_publications_semanticscholar.py
python3 scripts/update_publications_semanticscholar.py --dry-run
python3 scripts/update_publications_semanticscholar.py --recompute-suggested-themes
python3 scripts/update_publications_semanticscholar.py --recompute-suggested-themes --apply-suggested-themes
```

Required environment variables:
- `S2_API_KEY` (Semantic Scholar API key, sent as `x-api-key`)
- `PI_NAME` (example: `Sara Beery`)
- `LAB_START_DATE` (inclusive cutoff; format `YYYY-MM-DD`, example: `2023-09-01`)

Optional environment variable (recommended):
- `S2_AUTHOR_ID` (for precise author-id matching, with name fallback)

Behavior of the sync script:
- Queries Semantic Scholar `paper/search` year-by-year from newest year down to `LAB_START_DATE`
- Applies a global request pacer to stay at or below 1 request/second
- Filters to papers that actually include the PI as an author
- Applies a lab start-date cutoff
- Deduplicates by DOI, otherwise normalized title + year (keeps best duplicate record)
- Sorts candidate papers by `publicationDate` (desc), then year (desc), then title
- Preserves all existing entries and does not overwrite existing `themes`
- Adds missing entries with `themes: []`
- Requests `publicationTypes` and optionally `tldr` from Semantic Scholar when available
- Suggests `suggested_themes` for new entries using a weighted deterministic classifier over title, venue, abstract, optional TLDR, and publication type
- Never deletes existing publications automatically

Theme curation:
- `themes` remains the manually curated field used by the site
- `suggested_themes` is written for newly scraped papers to make manual assignment faster
- The publications page shows `suggested_themes` only when `themes` is empty
- `--recompute-suggested-themes` deletes all current `suggested_themes` and rebuilds them deterministically for the existing YAML entries
- `--apply-suggested-themes` can be paired with recompute for a one-time bulk reassignment of `themes`
- Recompute looks up live Semantic Scholar metadata for each existing publication by DOI first, then Semantic Scholar paper URL, then title/year search fallback
- Abstracts are used transiently for theme inference only and are not stored in `_data/publications.yml`
- If live Semantic Scholar enrichment is unavailable for an existing paper during recompute, its `suggested_themes` stays empty rather than using a local fallback guess

GitHub Actions automation is configured in `.github/workflows/update_publications.yml` and runs weekly.
Set repository variables/secrets for `S2_API_KEY`, `PI_NAME`, `LAB_START_DATE`, and optionally `S2_AUTHOR_ID`.

Micromamba example:
```bash
micromamba create -n pubsync python=3.11 -y
micromamba activate pubsync
pip install requests pyyaml
export S2_API_KEY="your_semantic_scholar_api_key"
export PI_NAME="Sara Beery"
export LAB_START_DATE="2023-09-01"
export S2_AUTHOR_ID="2134791809"  # optional but recommended
python3 scripts/update_publications_semanticscholar.py --dry-run
python3 scripts/update_publications_semanticscholar.py --recompute-suggested-themes
```

Simple test plan:
1. Local dry-run:
   `python3 scripts/update_publications_semanticscholar.py --dry-run`
2. Local write + inspect:
   `python3 scripts/update_publications_semanticscholar.py && git diff _data/publications.yml`
3. GitHub Actions:
   run `.github/workflows/update_publications.yml` with repo vars/secrets configured.

### Updating projects from the Google Form

Projects now sync from the public Google Form response sheet into `_data/software.yml`.
The importer:
- Reads the public CSV export for the form response tab
- Treats `Website`, `Demo`, `Code`, `Data`, and `Paper` as optional links
- Requires the other fields (`Title`, `Project Logo (square image)`, `Description`, `Publication Date`, `Research Theme`)
- Sorts projects newest-first by publication date and stores the publication year for display on the page
- Canonicalizes project research themes to the shared site-wide theme list
- Preserves any extra local-only fields on matching project titles so migration can stay gradual

Run locally with:
```bash
python3 scripts/update_projects_from_google_form.py --dry-run
python3 scripts/update_projects_from_google_form.py
```

Optional environment variable:
- `PROJECTS_SHEET_CSV_URL` to override the default public CSV export URL used by the script

GitHub Actions automation is configured in `.github/workflows/update_projects.yml`.

### Updating outreach content

The Outreach page uses two repo-local markdown files:
- `_outreach/talks.md`
- `_outreach/teaching.md`

Current behavior:
- Talks are pulled from the Google Sheet CSV configured in `_outreach/talks.md`
- Teaching/community-building items are pulled from the Google Sheet CSV configured in `_outreach/teaching.md`
- The markdown tables in `_outreach/talks.md` and `_outreach/teaching.md` are kept as local backups/templates while you migrate or edit sheet rows
- `python3 scripts/build_outreach_data.py` combines everything and sorts it newest-first automatically

For local previews, run:

```bash
python3 scripts/build_outreach_data.py
jekyll build
```

Expected format:

```md
---
section: "talks"
google_sheet_csv: "https://docs.google.com/spreadsheets/d/.../export?format=csv&gid=0"
---

| Title | Speakers | Host | Date | External |
| --- | --- | --- | --- | --- |
| Item title | Speaker Name | Host Name | 5 Mar 2025 | https://example.com |
```

Notes:
- The supported table columns are `Title`, `Date`, and `External`, plus optional people/org columns:
  `Speakers` or `Instructor(s)` map to the displayed person field, and `Host`, `Institution`, or `Instiution` map to the displayed organization field.
- Dates can be entered as full dates like `03/05/2025` or `5 Mar 2025`, month-level like `February 2026`, or year-only like `2024`.
- The loader normalizes those dates internally for sorting and display.
- Talks display dates as `DD MMM YYYY`; teaching/community-building items display as `MMM YYYY`.
- Talks display person/org metadata as `Speaker` and `Host`; teaching/community-building items display those same fields as `Instructor(s)` and `Institution`.
- If an item appears both in the markdown backup and in the Google Sheet, the loader deduplicates it by normalized title + date and keeps the richer row.
- The generated build artifact is `_data/outreach.json`.

### Other changes

The following have been set up to be similarly easy to add new content to. Hopefully it should be simple to extrapolate the editing of `.yml` files to the following, but ask Kevin or Kento if you need help.
- News (`_data/news.yml`)
- Group photos (`_data/photos.yml`, images go in `images/grouppic/`)
- Projects (`_data/software.yml`, generated from the Google Form response sheet via `scripts/update_projects_from_google_form.py`)
- Research relevant to Connor's directions on the "Research" page (`_data/research.yml`)
- WIP: The carousel highlighting recent work still needs to be refactored to be easily editable with `.yml` files. For now, they are manually declared in `_includes/carousel.html` with pictures in `image/carouselpic`)
