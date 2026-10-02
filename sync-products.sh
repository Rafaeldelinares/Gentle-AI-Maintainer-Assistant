#!/usr/bin/env bash
set -euo pipefail

PRODUCTS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/products"
mkdir -p "$PRODUCTS_DIR"

declare -A REPOS=(
  ["gentle-ai"]="https://github.com/Gentleman-Programming/gentle-ai.git"
  ["engram"]="https://github.com/Gentleman-Programming/engram.git"
  ["gentle-shell"]="https://github.com/Gentleman-Programming/gentle-shell.git"
  ["gentle-shell-desktop"]="https://github.com/Gentleman-Programming/gentle-shell-desktop.git"
)

echo "============================================================"
echo "Sincronizando productos del ecosistema con upstream/main..."
echo "============================================================"

for NAME in "${!REPOS[@]}"; do
  URL="${REPOS[$NAME]}"
  TARGET="$PRODUCTS_DIR/$NAME"

  if [ ! -d "$TARGET/.git" ]; then
    echo "Clonando $NAME desde $URL..."
    git clone "$URL" "$TARGET"
  else
    echo "Actualizando $NAME al último commit..."
    git -C "$TARGET" fetch origin
    # Detect default branch (main or master)
    BRANCH=$(git -C "$TARGET" rev-parse --abbrev-ref origin/HEAD 2>/dev/null | sed 's@origin/@@' || echo "main")
    git -C "$TARGET" checkout "$BRANCH" --quiet
    git -C "$TARGET" pull --ff-only origin "$BRANCH" --quiet
  fi

  COMMIT=$(git -C "$TARGET" log -1 --format="%h - %s (%ci)")
  echo "✔ $NAME sincronizado: $COMMIT"
done

echo "============================================================"
echo "Todos los productos están en su última versión oficial."
echo "============================================================"
