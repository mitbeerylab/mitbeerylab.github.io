#!/usr/bin/env bash
# Make web-sized copies of gallery photos.
#
# Full-resolution originals live in _gallery_originals/ (git-ignored, and
# skipped by Jekyll). This writes resized, metadata-stripped JPEGs to
# images/gallerypic/, which is what the /gallery page serves.
#
# Usage: scripts/optimize_gallery_images.sh   (requires ImageMagick)
set -euo pipefail

cd "$(dirname "$0")/.."
SRC=_gallery_originals
DEST=images/gallerypic
MAX_EDGE=2400   # longest side in pixels
QUALITY=82

mkdir -p "$DEST"
shopt -s nullglob nocaseglob
for f in "$SRC"/*.{jpg,jpeg,png,heic,tif,tiff,webp}; do
  name=$(basename "${f%.*}")
  out="$DEST/$name.jpg"
  if [[ -f "$out" && "$out" -nt "$f" ]]; then
    continue
  fi
  magick "$f" -auto-orient -resize "${MAX_EDGE}x${MAX_EDGE}>" \
    -strip -interlace JPEG -quality "$QUALITY" "$out"
  echo "$out ($(du -h "$out" | cut -f1))"
done
