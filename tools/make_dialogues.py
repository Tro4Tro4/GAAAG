"""Turns conversation and scene scripts into the .tres resources the game eats.

The runtime consumes [Dialogue] and [Sequence] resources, and it goes on doing
so: nothing here touches DialogueRunner or SequenceRunner. What changes is where
the writing happens. A conversation of two lines and four options costs 48 lines
of .tres — measured, that is resources/dialogues/console.tres — and the game is
budgeted at forty-four rooms and several hundred conversations. Writing those by
hand was named the production bottleneck in CLAUDE.md before a single real one
existed; this is the moment it stopped being hypothetical, because the mover in
the flat is the first character in the game with something to say.

So the source of truth moves to a script, and the .tres becomes a generated
file. Same shape as everything else in tools/: the thing that produces an asset
lives in the repository, because an asset nobody can remake is an asset nobody
can correct. The developer never runs this — they press Play on the .tres.

Run from the project root:

    python tools/make_dialogues.py                 # everything
    python tools/make_dialogues.py resources/dialogues/mover.dlg

Exits 1 if any source is wrong, and writes nothing in that case: a half-written
set of resources is worse than none.


The format
----------

One directive per line, keyword first. Blank lines and lines starting with #
are ignored, and indentation is decoration — the keyword says everything about
where a line belongs. Keywords are English, like every other identifier in the
project; the content they carry is always a text key, so the words the player
reads are still only in resources/text/.

A conversation, in a .dlg next to the .tres it makes:

    uid    baggadlgmovr01
    colour 0.86 0.74 0.52

    line start
        says DLG_MOVER_START

        option DLG_MOVER_OPT_LIST
            if    !asked_list
            raise asked_list
            reply DLG_MOVER_REPLY_LIST

        option DLG_MOVER_OPT_LABEL
            if   saw_delivery_label
            goto label

        option DLG_MOVER_OPT_BYE
            reply DLG_MOVER_REPLY_BYE
            end

    line label
        says DLG_MOVER_LABEL

The first `line` is where the conversation starts, exactly as the resource has
always had it. `if` takes the condition strings the whole game shares — see
Conditions — and may be repeated. `reply` and `goto` are mutually exclusive,
because only one of the two can be on the caption; saying so here is better
than the runner saying so at play time.

A scene, in a .seq:

    uid baggaseqintr01

    walk  AtDoor
    say   SEQ_INTRO_ARRIVE
    sound thud
    flag  intro_seen

The nine kinds of step are say, wait, walk, face, sound, flag, switch, give and
take — the closed list SequenceStep declares, with no way to add a tenth from
here. That is on purpose: a sequence that can do anything is a script.

References are written short and resolved by the generator, so a script never
holds a res:// path: `sound thud` finds assets/audio/thud.wav, and `give
documents` finds resources/items/documents.tres. Both are checked to exist.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

DIALOGUE_DIR = Path("resources/dialogues")
SEQUENCE_DIR = Path("resources/sequences")
ITEM_DIR = Path("resources/items")
AUDIO_DIR = Path("assets/audio")

DIALOGUE_SCRIPT = "res://scripts/dialogue/dialogue.gd"
LINE_SCRIPT = "res://scripts/dialogue/dialogue_line.gd"
OPTION_SCRIPT = "res://scripts/dialogue/dialogue_option.gd"
SEQUENCE_SCRIPT = "res://scripts/sequence/sequence.gd"
STEP_SCRIPT = "res://scripts/sequence/sequence_step.gd"

# The order SequenceStep.Kind declares. An enum is stored in a .tres as its
# integer, so this list is the one place the two files have to agree — and the
# reason the project has already been bitten once, when two words were removed
# from the middle of the verb enum and every value after them shifted.
STEP_KINDS = ("say", "wait", "walk", "face", "sound", "flag", "switch",
              "give", "take")

# What a text key looks like. Only used to warn: whether a key exists is
# tools/check_texts.py's job, and it reads the generated .tres like any other.
KEY_SHAPE = re.compile(r"^[A-Z][A-Z0-9]*(?:_[A-Z0-9]+)+$")


class SourceError(Exception):
    """A mistake in a script, reported with the line it is on."""


def fail(path: Path, number: int, message: str) -> SourceError:
    return SourceError(f"{path}:{number}: {message}")


def directives(path: Path) -> list[tuple[int, str, str]]:
    """The (line number, keyword, rest) of every directive in a script."""
    out: list[tuple[int, str, str]] = []

    for number, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue

        keyword, _, rest = line.partition(" ")
        out.append((number, keyword, rest.strip()))

    return out


def quoted(value: str) -> str:
    return '"%s"' % value.replace("\\", "\\\\").replace('"', '\\"')


def string_array(values: list[str]) -> str:
    return "PackedStringArray(%s)" % ", ".join(quoted(v) for v in values)


def item_path(name: str, path: Path, number: int) -> str:
    """res:// path of the item called [param name], which has to exist.

    Items are named by id and not by file, which is the same choice the save
    game made: a file can move, an id is what a flag already refers to. That
    they happen to line up one-to-one today is a convenience, and the check
    below is what would catch the day they stop.
    """
    target = ITEM_DIR / f"{name}.tres"
    if not target.exists():
        raise fail(path, number, f"no item called '{name}' ({target})")

    return f"res://{target.as_posix()}"


def sound_path(name: str, path: Path, number: int) -> str:
    target = Path(name) if "/" in name else AUDIO_DIR / f"{name}.wav"
    if not target.exists():
        raise fail(path, number, f"no sound called '{name}' ({target})")

    return f"res://{target.as_posix()}"


def uid_of(declared: str, target: Path, path: Path) -> str:
    """The uid the generated resource must keep.

    It has to be stable, and stability cannot be left to chance: a scene names a
    resource by uid as well as by path, so a new uid on every run would quietly
    unhook console.tres from Station.tscn. Declared in the script when there is
    one, taken from the file being replaced otherwise, and refused when neither
    exists — inventing one is the only outcome that could lose a reference.
    """
    if declared:
        return declared

    if target.exists():
        found = re.search(r'uid="uid://([^"]+)"', target.read_text(encoding="utf-8"))
        if found:
            return found.group(1)

    raise SourceError(
        f"{path}: no uid. Add a line 'uid <something>' — it has to stay the "
        f"same for ever, because scenes name this resource by it.")


class Writer:
    """Collects the ext_resource and sub_resource blocks of one .tres.

    The two halves of a resource file have to be built in opposite orders — the
    header lists external files, the body lists sub-resources that refer to them
    by the ids the header gave out — so they are gathered here and assembled at
    the end.
    """

    def __init__(self) -> None:
        self._externals: dict[str, str] = {}
        self._blocks: list[str] = []

    def external(self, kind: str, path: str, hint: str) -> str:
        """The id of the ext_resource for [param path], adding it if new."""
        if path in self._externals:
            return self._externals[path]

        identifier = f"{len(self._externals) + 1}_{hint}"
        self._externals[path] = identifier
        self._header_lines = getattr(self, "_header_lines", [])
        self._header_lines.append(
            f'[ext_resource type="{kind}" path="{path}" id="{identifier}"]')
        return identifier

    def sub(self, identifier: str, properties: list[str]) -> str:
        """Adds a sub_resource and gives back the reference to it."""
        body = "\n".join(properties)
        self._blocks.append(f'[sub_resource type="Resource" id="{identifier}"]\n{body}')
        return f'SubResource("{identifier}")'

    def render(self, uid: str, script_class: str, resource: list[str]) -> str:
        header = getattr(self, "_header_lines", [])
        # Counted as externals plus sub-resources plus the resource itself.
        # Godot uses it to size a progress bar and tolerates it being generous,
        # which is why one number is used everywhere rather than reproducing the
        # off-by-one that the two hand-written files disagree about.
        steps = len(header) + len(self._blocks) + 1

        parts = [
            f'[gd_resource type="Resource" script_class="{script_class}" '
            f'load_steps={steps} format=3 uid="uid://{uid}"]',
            "",
            "\n".join(header),
            "",
        ]
        for block in self._blocks:
            parts += [block, ""]

        parts += ["[resource]", "\n".join(resource), ""]
        return "\n".join(parts)


def build_dialogue(path: Path, target: Path) -> str:
    """Reads a .dlg and returns the text of the .tres it describes."""
    uid = ""
    colour = (1.0, 1.0, 1.0)
    lines: list[dict] = []
    current: dict | None = None
    option: dict | None = None

    for number, keyword, rest in directives(path):
        if keyword == "uid":
            uid = rest
            continue

        if keyword == "colour":
            pieces = rest.split()
            if len(pieces) != 3:
                raise fail(path, number, "colour wants three numbers, 0 to 1")
            colour = tuple(float(p) for p in pieces)
            continue

        if keyword == "line":
            if not rest:
                raise fail(path, number, "line wants an id")
            current = {"id": rest, "says": "", "options": [], "at": number}
            option = None
            lines.append(current)
            continue

        if current is None:
            raise fail(path, number, f"'{keyword}' before any line")

        if keyword == "says":
            if option is not None:
                raise fail(path, number,
                           "says belongs to a line; an option answers with reply")
            current["says"] = rest
            continue

        if keyword == "option":
            if not rest:
                raise fail(path, number, "option wants the text key the player says")
            option = {"text": rest, "if": [], "reply": "", "goto": "",
                      "raise": [], "on": [], "off": [], "give": "", "take": "",
                      "end": False, "at": number}
            current["options"].append(option)
            continue

        if option is None:
            raise fail(path, number, f"'{keyword}' outside an option")

        if keyword == "if":
            option["if"] += rest.split()
        elif keyword == "reply":
            option["reply"] = rest
        elif keyword == "goto":
            option["goto"] = rest
        elif keyword == "raise":
            option["raise"] += rest.split()
        elif keyword == "switch":
            pieces = rest.split()
            if len(pieces) < 2 or pieces[-1] not in ("on", "off"):
                raise fail(path, number, "switch wants names then 'on' or 'off'")
            option[pieces[-1]] += pieces[:-1]
        elif keyword == "give":
            option["give"] = rest
        elif keyword == "take":
            option["take"] = rest
        elif keyword == "end":
            option["end"] = True
        else:
            raise fail(path, number, f"unknown directive '{keyword}'")

    if not lines:
        raise SourceError(f"{path}: no lines")

    known = {line["id"] for line in lines}
    if len(known) != len(lines):
        raise SourceError(f"{path}: two lines share an id")

    writer = Writer()
    dialogue_id = writer.external("Script", DIALOGUE_SCRIPT, "dialogue")
    line_id = writer.external("Script", LINE_SCRIPT, "line")
    option_id = writer.external("Script", OPTION_SCRIPT, "option")

    line_refs: list[str] = []

    for index, line in enumerate(lines):
        option_refs: list[str] = []

        for spot, opt in enumerate(line["options"]):
            at = opt["at"]

            if opt["reply"] and opt["goto"]:
                raise fail(path, at,
                           "reply and goto are exclusive: arriving somewhere says "
                           "that line's own says, staying says reply")
            if opt["goto"]:
                if opt["goto"] not in known:
                    raise fail(path, at, f"goto names no line: '{opt['goto']}'")
                if opt["end"]:
                    raise fail(path, at, "goto and end contradict each other")

            if not KEY_SHAPE.match(opt["text"]):
                warn(f"{path}:{at}: '{opt['text']}' does not look like a text key")

            properties = [f'script = ExtResource("{option_id}")',
                          f'text = {quoted(opt["text"])}']
            if opt["if"]:
                properties.append(f'conditions = {string_array(opt["if"])}')
            if opt["reply"]:
                properties.append(f'reply = {quoted(opt["reply"])}')
            if opt["goto"]:
                properties.append(f'goes_to = &{quoted(opt["goto"])}')
            if opt["raise"]:
                properties.append(f'raises = {string_array(opt["raise"])}')
            if opt["on"]:
                properties.append(f'switches_on = {string_array(opt["on"])}')
            if opt["off"]:
                properties.append(f'switches_off = {string_array(opt["off"])}')
            for field, key in (("give", "gives"), ("take", "takes")):
                if opt[field]:
                    reference = writer.external(
                        "Resource", item_path(opt[field], path, at), opt[field])
                    properties.append(f'{key} = ExtResource("{reference}")')
            if opt["end"]:
                properties.append("ends = true")

            option_refs.append(
                writer.sub(f'Option_{line["id"]}_{spot}', properties))

        properties = [f'script = ExtResource("{line_id}")',
                      f'id = &{quoted(line["id"])}']
        if line["says"]:
            if not KEY_SHAPE.match(line["says"]):
                warn(f"{path}:{line['at']}: '{line['says']}' does not look like a key")
            properties.append(f'says = {quoted(line["says"])}')
        if option_refs:
            properties.append('options = Array[ExtResource("%s")]([%s])'
                              % (option_id, ", ".join(option_refs)))
        elif index == 0:
            warn(f"{path}: the opening line offers nothing, so the conversation "
                 f"ends the moment it starts")

        line_refs.append(writer.sub(f'Line_{line["id"]}', properties))

    resource = [f'script = ExtResource("{dialogue_id}")',
                "speaker_color = Color(%s, %s, %s, 1)" % colour,
                'lines = Array[ExtResource("%s")]([%s])'
                % (line_id, ", ".join(line_refs))]

    return writer.render(uid_of(uid, target, path), "Dialogue", resource)


def build_sequence(path: Path, target: Path) -> str:
    """Reads a .seq and returns the text of the .tres it describes."""
    uid = ""
    steps: list[tuple[int, str, str]] = []

    for number, keyword, rest in directives(path):
        if keyword == "uid":
            uid = rest
            continue

        if keyword not in STEP_KINDS:
            raise fail(path, number, f"unknown step '{keyword}'")

        steps.append((number, keyword, rest))

    if not steps:
        raise SourceError(f"{path}: no steps")

    writer = Writer()
    sequence_id = writer.external("Script", SEQUENCE_SCRIPT, "sequence")
    step_id = writer.external("Script", STEP_SCRIPT, "step")

    refs: list[str] = []

    for spot, (number, kind, rest) in enumerate(steps):
        properties = [f'script = ExtResource("{step_id}")',
                      f"kind = {STEP_KINDS.index(kind)}"]

        if kind == "say":
            if not KEY_SHAPE.match(rest):
                warn(f"{path}:{number}: '{rest}' does not look like a text key")
            properties.append(f"text = {quoted(rest)}")
        elif kind == "wait":
            properties.append(f"seconds = {float(rest)}")
        elif kind in ("walk", "face"):
            if not rest:
                raise fail(path, number, f"{kind} wants the name of a point")
            properties.append(f"point = &{quoted(rest)}")
        elif kind == "sound":
            reference = writer.external(
                "AudioStream", sound_path(rest, path, number), rest.split("/")[-1
                ].split(".")[0])
            properties.append(f'sound = ExtResource("{reference}")')
        elif kind == "flag":
            properties.append(f"name = &{quoted(rest)}")
        elif kind == "switch":
            pieces = rest.split()
            if len(pieces) != 2 or pieces[1] not in ("on", "off"):
                raise fail(path, number, "switch wants a name then 'on' or 'off'")
            properties.append(f"name = &{quoted(pieces[0])}")
            # Written out either way. SequenceStep.on defaults to true, so the
            # "off" case is the one that must be stated — but stating both is
            # what makes the generated file say what the script says.
            properties.append(f"on = {'true' if pieces[1] == 'on' else 'false'}")
        elif kind in ("give", "take"):
            reference = writer.external(
                "Resource", item_path(rest, path, number), rest)
            properties.append(f'item = ExtResource("{reference}")')

        refs.append(writer.sub(f"Step_{spot}_{kind}", properties))

    resource = [f'script = ExtResource("{sequence_id}")',
                'steps = Array[ExtResource("%s")]([%s])'
                % (step_id, ", ".join(refs))]

    return writer.render(uid_of(uid, target, path), "Sequence", resource)


WARNINGS: list[str] = []


def warn(message: str) -> None:
    WARNINGS.append(message)


def sources(arguments: list[str]) -> list[Path]:
    if arguments:
        return [Path(a) for a in arguments]

    return sorted(DIALOGUE_DIR.glob("*.dlg")) + sorted(SEQUENCE_DIR.glob("*.seq"))


def main(arguments: list[str]) -> int:
    chosen = sources(arguments)
    if not chosen:
        print("nessun copione da convertire")
        return 0

    # Every source is read and built before anything is written. A run that
    # fails half way through would leave the project with some resources from
    # the new scripts and some from the old ones, which is the one state nobody
    # could reason about.
    written: list[tuple[Path, str]] = []
    problems: list[str] = []

    for path in chosen:
        if not path.exists():
            problems.append(f"{path}: not there")
            continue

        target = path.with_suffix(".tres")
        try:
            if path.suffix == ".dlg":
                written.append((target, build_dialogue(path, target)))
            elif path.suffix == ".seq":
                written.append((target, build_sequence(path, target)))
            else:
                problems.append(f"{path}: not a .dlg or a .seq")
        except SourceError as error:
            problems.append(str(error))
        except ValueError as error:
            problems.append(f"{path}: {error}")

    for message in WARNINGS:
        print(f"attenzione  {message}")

    if problems:
        for message in problems:
            print(f"ERRORE  {message}")
        print(f"\n{len(problems)} copioni da correggere, niente scritto")
        return 1

    for target, text in written:
        target.write_text(text, encoding="utf-8")
        print(f"{target}")

    print(f"\n{len(written)} risorse scritte"
          + (f", {len(WARNINGS)} avvisi" if WARNINGS else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
