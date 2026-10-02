#!/usr/bin/env bash
# ════════════════════════════════════════════════════════════════════════════
#  load.sh — pull the three systems' issues from GitHub into the local store.
#
#  Acquisition uses the HOST's authenticated `gh`. The container only holds data.
#  Idempotent: every insert upserts on its natural key.
#
#  Usage:
#     ./load.sh                      # all three systems, all states, with comments
#     ./load.sh --state open         # open issues only (much faster)
#     ./load.sh --no-comments        # skip comment fetching
#     ./load.sh --limit 500          # cap issues per system
#     ./load.sh --reset              # drop the volume and rebuild from scratch
# ════════════════════════════════════════════════════════════════════════════
set -euo pipefail

cd "$(dirname "$0")"

STATE=all
LIMIT=3000
WITH_COMMENTS=1
RESET=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --state)       STATE="$2"; shift 2 ;;
    --limit)       LIMIT="$2"; shift 2 ;;
    --no-comments) WITH_COMMENTS=0; shift ;;
    --reset)       RESET=1; shift ;;
    -h|--help)     sed -n '2,16p' "$0"; exit 0 ;;
    *) echo "unknown flag: $1" >&2; exit 2 ;;
  esac
done

SYSTEMS=(
  "gentle-ai|Gentleman-Programming/gentle-ai|Go"
  "engram|Gentleman-Programming/engram|Go"
  "gentle-shell|Gentleman-Programming/gentle-shell|TypeScript"
)

say()     { printf '\n\033[1;36m▸ %s\033[0m\n' "$*"; }
ok()      { printf '\033[1;32m  ✔ %s\033[0m\n' "$*"; }
psql_run(){ docker compose exec -T db psql -q -v ON_ERROR_STOP=1 -U gama -d gama; }

if [[ $RESET -eq 1 ]]; then
  say "resetting: removing volume"
  docker compose down -v --remove-orphans
fi

mkdir -p data

say "starting postgres"
docker compose up -d --wait
ok "postgres up on 127.0.0.1:55432"

# ── 1. Systems ──────────────────────────────────────────────────────────────
say "systems"
: > data/systems.tsv
for entry in "${SYSTEMS[@]}"; do
  IFS='|' read -r slug full lang <<<"$entry"
  read -r rid branch <<<"$(gh api "repos/$full" --jq '"\(.id) \(.default_branch)"')"
  printf '%s\t%s\t%s\t%s\t%s\n' "$slug" "$full" "$lang" "$branch" "$rid" >> data/systems.tsv
done
psql_run <<'SQL'
CREATE TEMP TABLE t(slug text, full_name text, language text, default_branch text, repo_id bigint);
\copy t FROM '/data/systems.tsv'
INSERT INTO systems (slug, full_name, language, default_branch, repo_id)
SELECT slug, full_name, language, default_branch, repo_id FROM t
ON CONFLICT (slug) DO UPDATE
  SET full_name = EXCLUDED.full_name, repo_id = EXCLUDED.repo_id,
      default_branch = EXCLUDED.default_branch;
SQL
cut -f1,2 data/systems.tsv | sed 's/^/    /'

# ── 2. Labels ───────────────────────────────────────────────────────────────
say "labels"
: > data/labels.tsv
for entry in "${SYSTEMS[@]}"; do
  IFS='|' read -r slug full _lang <<<"$entry"
  gh label list -R "$full" --limit 200 --json name,color,description \
    | jq -r --arg slug "$slug" \
      '.[] | [$slug, .name, (.color // ""), ((.description // "") | gsub("[\t\n\r]"; " "))] | @tsv' \
    >> data/labels.tsv
done
psql_run <<'SQL'
CREATE TEMP TABLE t(slug text, name text, color text, description text);
\copy t FROM '/data/labels.tsv'
INSERT INTO labels (system_id, name, color, description)
SELECT s.id, t.name, t.color, t.description FROM t JOIN systems s ON s.slug = t.slug
ON CONFLICT (system_id, name) DO UPDATE
  SET color = EXCLUDED.color, description = EXCLUDED.description;
SQL
ok "$(wc -l < data/labels.tsv) labels"

# ── 3. Issues + label links + comments ──────────────────────────────────────
for entry in "${SYSTEMS[@]}"; do
  IFS='|' read -r slug full _lang <<<"$entry"
  say "fetching $slug  (state=$STATE limit=$LIMIT comments=$WITH_COMMENTS)"

  gh issue list -R "$full" --state "$STATE" --limit "$LIMIT" \
    --json number,title,body,state,author,createdAt,updatedAt,closedAt,labels,comments \
    > "data/$slug.issues.json"

  jq -r '.[] | [
      (.number|tostring), (.title // ""), (.body // ""), .state,
      (.author.login // ""), (.createdAt // ""), (.updatedAt // ""), (.closedAt // ""),
      ((.comments // []) | length | tostring)
    ] | @tsv' "data/$slug.issues.json" > "data/$slug.issues.tsv"

  jq -r --arg slug "$slug" \
    '.[] | .number as $n | (.labels // [])[] | [$slug, ($n|tostring), .name] | @tsv' \
    "data/$slug.issues.json" > "data/$slug.issue_labels.tsv"

  if [[ $WITH_COMMENTS -eq 1 ]]; then
    jq -r --arg slug "$slug" \
      '.[] | .number as $n | ((.comments // [])[]) as $c
       | select($c.id != null)
       | [$slug, ($n|tostring), ($c.id|tostring), ($c.author.login // ""), ($c.body // ""), ($c.createdAt // "")]
       | @tsv' "data/$slug.issues.json" > "data/$slug.comments.tsv"
  else
    : > "data/$slug.comments.tsv"
  fi

  psql_run <<SQL
CREATE TEMP TABLE ti(number int, title text, body text, state text, author text,
                     created_at text, updated_at text, closed_at text, comments_count int);
\\copy ti FROM '/data/$slug.issues.tsv'
INSERT INTO issues (system_id, number, title, body, state, author,
                    created_at, updated_at, closed_at, comments_count)
SELECT s.id, ti.number, ti.title, ti.body, lower(ti.state), nullif(ti.author,''),
       ti.created_at::timestamptz,
       nullif(ti.updated_at,'')::timestamptz,
       nullif(ti.closed_at,'')::timestamptz,
       ti.comments_count
FROM ti JOIN systems s ON s.slug = '$slug'
ON CONFLICT (system_id, number) DO UPDATE
  SET title = EXCLUDED.title, body = EXCLUDED.body, state = EXCLUDED.state,
      closed_at = EXCLUDED.closed_at, comments_count = EXCLUDED.comments_count,
      fetched_at = now();

CREATE TEMP TABLE tl(slug text, number int, label_name text);
\\copy tl FROM '/data/$slug.issue_labels.tsv'
INSERT INTO issue_labels (issue_id, label_id)
SELECT i.id, l.id
FROM tl
JOIN systems s ON s.slug = tl.slug
JOIN issues  i ON i.system_id = s.id AND i.number = tl.number
JOIN labels  l ON l.system_id = s.id AND l.name = tl.label_name
ON CONFLICT DO NOTHING;

CREATE TEMP TABLE tc(slug text, number int, gh_id bigint, author text, body text, created_at text);
\\copy tc FROM '/data/$slug.comments.tsv'
INSERT INTO comments (issue_id, gh_id, author, body, created_at)
SELECT i.id, tc.gh_id, nullif(tc.author,''), tc.body,
       nullif(tc.created_at,'')::timestamptz
FROM tc
JOIN systems s ON s.slug = tc.slug
JOIN issues  i ON i.system_id = s.id AND i.number = tc.number
ON CONFLICT (gh_id) DO NOTHING;
SQL
  ok "$(jq length "data/$slug.issues.json") issues · $(wc -l < "data/$slug.issue_labels.tsv") label links · $(wc -l < "data/$slug.comments.tsv") comments"
done

# ── 4. Derived columns + cross-reference extraction ─────────────────────────
say "derived columns and cross_refs"
psql_run -c "SELECT refresh_derived();"
ok "done"

# ── 5. Summary ──────────────────────────────────────────────────────────────
say "summary"
psql_run -P pager=off <<'SQL'
SELECT s.slug,
       count(*)                                      AS issues,
       count(*) FILTER (WHERE i.state = 'open')      AS open,
       pg_size_pretty(sum(i.body_bytes)::bigint)     AS body_text
FROM issues i JOIN systems s ON s.id = i.system_id
GROUP BY s.slug ORDER BY s.slug;

SELECT count(*) AS qualified_cross_refs FROM cross_refs;

SELECT * FROM v_triage_debt;
SQL

echo
printf '\033[1;32m✔ connect:  docker compose exec db psql -U gama -d gama\033[0m\n'
