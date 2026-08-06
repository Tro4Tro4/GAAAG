"""Checks the localisation, which the engine cannot do from this machine.

Two things go wrong with keys, and neither of them is visible until the game is
running in the wrong language:

  * a key exists in one language and not in the other, so a line silently
    falls back to its key and the player reads ROOM_HALL_CLERK_LOOK;
  * a scene or a script names a key that no language file has, which is the
    same symptom arrived at from the other side.

Both are mechanical, so they are checked mechanically. CLAUDE.md has asked for
this since localisation went in; it lived as an ad-hoc snippet until the first
chapter started adding keys forty at a time.

    python tools/check_texts.py

Exits 1 if anything is wrong, so it can go in a pre-commit hook next to
gdparse and qa_check.py.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

LOCALES = {"it": Path("resources/text/it.tres"),
           "en": Path("resources/text/en.tres")}

# Where keys are used. Scenes and resources name them as plain strings; the
# scripts hold the handful of interface keys that are written from code.
SEARCH_GLOBS = ("scenes/**/*.tscn", "resources/**/*.tres", "scripts/**/*.gd")

# A key looks like this and nothing else does: capitals, digits, underscores,
# at least one underscore, at least four characters. The shape is the reason
# the project can find them without a registry.
KEY = re.compile(r'"([A-Z][A-Z0-9]*(?:_[A-Z0-9]+)+)"')

# Strings that pass the shape test and are not keys. Kept short on purpose: a
# long list here would mean the shape is wrong.
NOT_KEYS = {
    "PROCESS_MODE_DISABLED", "MOUSE_FILTER_IGNORE",
    "TEXTURE_FILTER_LINEAR", "TEXTURE_FILTER_NEAREST",
}


def entries_of(path: Path) -> dict[str, str]:
    """Pulls the entries dictionary out of a LocaleTexts .tres.

    Read with a regular expression rather than by parsing the resource format:
    the file is a flat "key": "value" list, one per line, and a parser for the
    whole of Godot's format would be a great deal of code to find out something
    a line already says.
    """
    text = path.read_text(encoding="utf-8")
    body = text.split("entries = {", 1)
    if len(body) != 2:
        raise SystemExit(f"{path}: no entries block")

    found: dict[str, str] = {}
    for line in body[1].splitlines():
        line = line.strip()
        if line.startswith("}"):
            break
        m = re.match(r'"([^"]+)"\s*:\s*"(.*)",?$', line)
        if m:
            found[m.group(1)] = m.group(2)
    return found


def used_keys() -> dict[str, set[str]]:
    """Every key named anywhere, and where it was named."""
    where: dict[str, set[str]] = {}
    for pattern in SEARCH_GLOBS:
        for path in Path(".").glob(pattern):
            for key in KEY.findall(path.read_text(encoding="utf-8")):
                if key not in NOT_KEYS:
                    where.setdefault(key, set()).add(str(path).replace("\\", "/"))
    return where


def main() -> int:
    tables = {name: entries_of(path) for name, path in LOCALES.items()}
    problems = 0

    names = list(tables)
    base, other = names[0], names[1]
    only_base = sorted(set(tables[base]) - set(tables[other]))
    only_other = sorted(set(tables[other]) - set(tables[base]))

    if only_base:
        problems += len(only_base)
        print(f"\nSolo in {base} ({len(only_base)}):")
        for k in only_base:
            print(f"  {k}")
    if only_other:
        problems += len(only_other)
        print(f"\nSolo in {other} ({len(only_other)}):")
        for k in only_other:
            print(f"  {k}")

    known = set(tables[base]) | set(tables[other])
    used = used_keys()
    missing = sorted(k for k in used if k not in known)
    if missing:
        problems += len(missing)
        print(f"\nUsate ma non tradotte ({len(missing)}):")
        for k in missing:
            print(f"  {k}   <- {', '.join(sorted(used[k]))}")

    # Not a failure: a key can legitimately be written from code in a way the
    # search cannot see, and an unused key costs nothing but a line.
    unused = sorted(k for k in known if k not in used)
    if unused:
        print(f"\nTradotte ma mai nominate ({len(unused)}), da controllare a mano:")
        print("  " + ", ".join(unused))

    empty = sorted(k for k, v in tables[base].items() if not v.strip())
    if empty:
        problems += len(empty)
        print(f"\nVuote in {base} ({len(empty)}): " + ", ".join(empty))

    print(f"\n{len(tables[base])} chiavi in {base}, {len(tables[other])} in {other}")
    print("tutto a posto" if not problems else f"{problems} problemi")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
