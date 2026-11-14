# Academic Humanizer

A rule book that any AI can follow to remove the "AI tone" from a research paper, without touching the science.

It fixes things like em dashes, "Moreover", "crucial", "these results highlight…", dramatic colons and summary sentences that repeat the paragraph. It does **not** rewrite your paper. Every number, citation, equation, technical term and claim stays exactly as it was.

## What's in here

| File | What it is |
|---|---|
| `SKILL.md` | The rule book. This is the only file the AI really needs. |
| `scripts/humanizer_check.py` | Optional checker. Confirms that no number, citation or equation changed during the edit. |
| `tests/test_checker.py` | Tests for the checker. Only needed if you change the checker. |

## How to use it

### Option 1: Any chat AI (ChatGPT, Claude, Gemini, DeepSeek…)

1. Upload `SKILL.md` and your paper.
2. Send this prompt:

   > Remove the AI tone from the attached paper using `SKILL.md`. Follow its rules exactly and give me the report it asks for.

3. You get back two files: your edited paper and a separate report.

### Option 2: Coding agents (Codex, Claude Code, Cursor, Gemini CLI…)

`SKILL.md` follows the open Agent Skills format, so these tools can load it as a skill.

1. Put this folder in your tool's skills folder and name it `academic-humanizer`. For example:
   - Claude Code: `~/.claude/skills/academic-humanizer/`
   - Codex: `~/.codex/skills/academic-humanizer/`

   (Other tools use similar locations; check your tool's docs.)
2. Open your paper's folder in the tool and ask: *"Humanize this paper."*
3. The agent follows the rules and runs the checker on its own.

## Keeping exact wording

If some sentences must not change at all, either:

- tell the AI in your prompt: *"Don't change these: …"*, or
- mark them in the file:
  - LaTeX: put `% keep` on the line before and `% /keep` on the line after
  - Markdown: wrap them in `<!-- keep -->` … `<!-- /keep -->`

## What you get back

1. **The edited paper**, in the same format you gave it. For a LaTeX project with several files, you get an edited copy of the whole folder.
2. **A report** (`…_humanizer_report.md`), starting with the most important part:
   - edits that might have changed meaning (check these first)
   - problems only you can fix (missing citations, suspicious references, numbers that disagree)
   - what was checked
   - pattern counts before and after

## The checker (optional)

Needs Python 3, nothing else to install.

```
python scripts/humanizer_check.py paper.tex                   # count AI-tone patterns
python scripts/humanizer_check.py original/ edited/           # compare two versions
```

The result line tells you:

- **0, match:** all numbers, citations and math are the same and in the same order.
- **1, CHANGED:** something was added, lost or altered. Don't use that edit until it's fixed.
- **2, REVIEW:** the same items are there but in a different order. Check that no number or citation moved to the wrong claim.

The checker counts and compares. It can't tell whether a number still belongs to the right claim, so always read through the edits listed at the top of the report.

## Good to know

- Works best for English papers in computer science, engineering and other quantitative fields. For humanities or medical papers, add to your prompt: *"Follow the conventions of [your field] where they conflict with Part 2."*
- This is an editing aid, not a way to hide AI use. If your venue requires an AI-use statement, you still need it.
