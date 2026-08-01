#!/usr/bin/env bash
# Scansiona il progetto (o i file passati come argomento) cercando termini
# protetti dell'opera originale.
#
# Uso:
#   check-ip.sh                 # scansiona tutto il repo
#   check-ip.sh file1 file2     # scansiona solo i file indicati
#
# Uscita:
#   0 = nessun termine vietato trovato (gli avvisi non bloccano)
#   1 = trovato almeno un termine vietato
#   2 = errore di esecuzione
#
# Nota: lo script esclude se stesso e le proprie liste dalla scansione,
# altrimenti troverebbe sempre i termini che e' incaricato di cercare.

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
VIETATI="$SKILL_DIR/references/termini-vietati.txt"
AMBIGUI="$SKILL_DIR/references/termini-ambigui.txt"

if ! command -v rg >/dev/null 2>&1; then
  echo "ERRORE: ripgrep (rg) non disponibile." >&2
  exit 2
fi

for f in "$VIETATI" "$AMBIGUI"; do
  [[ -r "$f" ]] || { echo "ERRORE: lista non leggibile: $f" >&2; exit 2; }
done

# Costruisce un pattern alternato a partire da una lista, saltando commenti
# e righe vuote ed effettuando l'escape dei metacaratteri regex.
build_pattern() {
  sed -e 's/#.*//' -e 's/[[:space:]]*$//' "$1" \
    | grep -v '^[[:space:]]*$' \
    | sed -e 's/[][\.^$*+?(){}|\\]/\\&/g' \
    | paste -sd '|' -
}

PAT_VIETATI="$(build_pattern "$VIETATI")"
PAT_AMBIGUI="$(build_pattern "$AMBIGUI")"

RG_COMMON=(--ignore-case --word-regexp --line-number --no-heading --color never)

# Esclusioni. Due categorie, entrambe necessarie:
#
# 1. La skill stessa: contiene per forza i termini che deve cercare.
# 2. La documentazione meta (CLAUDE.md, README): per enunciare il divieto
#    deve poter nominare l'opera da cui prende le distanze. Non sono
#    contenuti di gioco e non finiscono nel prodotto spedito.
#
# Il vincolo riguarda cio' che il giocatore puo' vedere o sentire: codice,
# commenti, dialoghi, asset, nomi. Se il controllo bloccasse anche i
# documenti che definiscono la regola, fallirebbe a ogni esecuzione e
# verrebbe presto ignorato -- il modo piu' rapido per far passare una
# violazione vera in mezzo al rumore.
RG_EXCLUDE=(
  --glob '!.git/**'
  --glob '!.godot/**'
  --glob '!.claude/skills/vincolo-ip/**'
  --glob '!CLAUDE.md'
  --glob '!README.md'
)

TARGETS=("$@")
if [[ ${#TARGETS[@]} -eq 0 ]]; then
  TARGETS=(".")
fi

echo "== Controllo vincolo IP =="
echo

FAIL=0

echo "-- Termini vietati --"
HITS_V="$(rg "${RG_COMMON[@]}" "${RG_EXCLUDE[@]}" --regexp "$PAT_VIETATI" "${TARGETS[@]}" 2>/dev/null)"
if [[ -n "$HITS_V" ]]; then
  echo "$HITS_V"
  echo
  COUNT_V="$(printf '%s\n' "$HITS_V" | wc -l | tr -d ' ')"
  echo "VIOLAZIONE: $COUNT_V occorrenze di termini protetti."
  echo "Vanno rimosse e sostituite con invenzioni originali."
  FAIL=1
else
  echo "Nessuno. OK."
fi
echo

echo "-- Termini ambigui (da valutare nel contesto, non bloccanti) --"
HITS_A="$(rg "${RG_COMMON[@]}" "${RG_EXCLUDE[@]}" --regexp "$PAT_AMBIGUI" "${TARGETS[@]}" 2>/dev/null)"
if [[ -n "$HITS_A" ]]; then
  echo "$HITS_A"
  echo
  COUNT_A="$(printf '%s\n' "$HITS_A" | wc -l | tr -d ' ')"
  echo "AVVISO: $COUNT_A occorrenze da valutare."
  echo "Per ognuna, chiedersi se e' uso ordinario o eco dell'originale."
  echo "Vedi SKILL.md, sezione 'Come valutare i termini ambigui'."
else
  echo "Nessuno."
fi
echo

if [[ $FAIL -eq 0 ]]; then
  echo "Esito: nessun termine vietato."
else
  echo "Esito: controllo FALLITO."
fi

exit $FAIL
