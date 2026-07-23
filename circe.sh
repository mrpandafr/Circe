#!/usr/bin/env bash
# circe.sh -- pipeline complet : encode, valide, explore.
# Usage : ./circe.sh mon_texte.txt

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [ -z "${1:-}" ]; then
    echo "Usage : ./circe.sh fichier.txt"
    exit 1
fi

FICHIER_TXT="$1"
FICHIER_VJSON="${FICHIER_TXT%.txt}.vjson"

if [ ! -f "$FICHIER_TXT" ]; then
    echo "❌ Fichier introuvable : $FICHIER_TXT"
    exit 1
fi

echo "═══ 1. Tissage ═══"
python3 "$SCRIPT_DIR/circe_encoder.py" "$FICHIER_TXT"

echo ""
echo "═══ 2. Validation ═══"
python3 "$SCRIPT_DIR/validateur.py" "$FICHIER_VJSON"

echo ""
echo "═══ 3. Exploration ═══"
echo "(tape /quit pour sortir)"
python3 "$SCRIPT_DIR/circe_explorer.py" "$FICHIER_VJSON"
