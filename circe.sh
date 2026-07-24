#!/usr/bin/env bash
# circe.sh -- pipeline complet : tisse, valide, explore.
#
# Usage :
#   ./circe.sh mon_texte.txt
#   ./circe.sh a.txt b.txt c.txt          -> corpus.vjson
#   ./circe.sh a.txt b.txt -o mon.vjson

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [ $# -eq 0 ]; then
    echo "Usage : ./circe.sh fichier.txt [autre.txt ...] [-o sortie.vjson]"
    exit 1
fi

# Séparer les fichiers de l'éventuel -o
FICHIERS=()
SORTIE=""
while [ $# -gt 0 ]; do
    case "$1" in
        -o) SORTIE="$2"; shift 2 ;;
        *)  FICHIERS+=("$1"); shift ;;
    esac
done

for f in "${FICHIERS[@]}"; do
    if [ ! -f "$f" ]; then
        echo "❌ Fichier introuvable : $f"
        exit 1
    fi
done

if [ -z "$SORTIE" ]; then
    if [ ${#FICHIERS[@]} -eq 1 ]; then
        SORTIE="${FICHIERS[0]%.*}.vjson"
    else
        SORTIE="corpus.vjson"
    fi
fi

echo "═══ 1. Tissage (${#FICHIERS[@]} document(s)) ═══"
python3 "$SCRIPT_DIR/circe_encoder.py" "${FICHIERS[@]}" -o "$SORTIE"

echo ""
echo "═══ 2. Validation ═══"
python3 "$SCRIPT_DIR/validateur.py" "$SORTIE"

echo ""
echo "═══ 3. Exploration ═══"
echo "(/docs pour commencer, /quit pour sortir)"
python3 "$SCRIPT_DIR/circe_explorer.py" "$SORTIE"
