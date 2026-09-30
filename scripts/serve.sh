#!/usr/bin/env bash
# Start this source tree, not whichever older copy Terminal happens to be in.
set -euo pipefail
ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd -- "$ROOT"
printf 'Serving source: %s\n' "$ROOT"
if ! command -v bundle >/dev/null 2>&1; then
  printf 'Bundler is not available. Follow the Ruby 3.3 setup in README.md.\n' >&2
  exit 1
fi
bundle check || bundle install
ruby scripts/check.rb --source-only
bundle exec jekyll clean
exec bundle exec jekyll serve --livereload --baseurl "" "$@"
