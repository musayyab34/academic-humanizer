# Academic Humanizer

**中文说明请看 [README_zh.md](README_zh.md)** · **Version history: [CHANGELOG.md](CHANGELOG.md)**

A rule book that any AI can follow to remove the "AI tone" from academic writing, without touching the science.

It works on English and Chinese text, and on:

- journal and conference papers
- theses
- research proposals (开题报告) and midterm reports (中期报告)
- lab reports and weekly reports

It fixes things like em dashes, "Moreover", "crucial", "these results highlight…", "值得注意的是", "具有重要意义", "赋能" and summary sentences that repeat the paragraph. It also finds **evasive writing**, sentences like "made good progress" or "取得了一定进展" that say nothing specific, and lists exactly what you need to fill in.

It does **not** rewrite your document. Every number, citation, equation, technical term and claim stays exactly as it was.

## What's in here

| File | What it is |
|---|---|
| `SKILL.md` | The rule book. This is the only file the AI really needs. |
| `scripts/humanizer_check.py` | Optional checker. Confirms that no number, citation or equation changed during the edit. |
| `tests/test_checker.py` | Tests for the checker. Only needed if you change the checker. |

## How to use it

### Option 1: Any chat AI (ChatGPT, Claude, Gemini, DeepSeek, Kimi…)

1. Upload `SKILL.md` and your document.
2. Send this prompt:

   > Remove the AI tone from the attached document using `SKILL.md`. Follow its rules exactly and give me the report it asks for.

3. You get back two files: your edited document and a separate report.

### Option 2: Coding agents (Codex, Claude Code, Cursor, Gemini CLI…)

`SKILL.md` follows the open Agent Skills format, so these tools can load it as a skill.

1. Put this folder in your tool's skills folder and name it `academic-humanizer`. For example:
   - Claude Code: `~/.claude/skills/academic-humanizer/`
   - Codex: `~/.codex/skills/academic-humanizer/`

   (Other tools use similar locations; check your tool's docs.)
2. Open your document's folder in the tool and ask: *"Humanize this document."*
3. The agent follows the rules and runs the checker on its own.

## Keeping exact wording

If some sentences must not change at all, either:

- tell the AI in your prompt: *"Don't change these: …"*, or
- mark them in the file:
  - LaTeX: put `% keep` on the line before and `% /keep` on the line after
  - Markdown: wrap them in `<!-- keep -->` … `<!-- /keep -->`
  - Word: list them in your prompt, or in a text file for the checker's `--protect` option

## What you get back

1. **The edited document**, in the same format you gave it (Word stays Word, LaTeX stays LaTeX).
2. **A report** (`…_humanizer_report.md`), starting with the most important part:
   - edits that might have changed meaning (check these first)
   - **fill these in**: vague sentences and the exact question each one needs answered
   - problems only you can fix (missing citations, suspicious references, numbers that disagree)
   - what was checked, and how much the length changed
   - pattern counts before and after

For weekly and midterm reports, the "fill these in" list comes first.

## The checker (optional)

Needs Python 3, nothing else to install. Reads `.tex`, `.md`, `.txt` and `.docx` files, in English, Chinese or both. For Word files it reads the body text, equations, footnotes and endnotes, but not headers, footers, comments or text boxes.

```
python scripts/humanizer_check.py report.docx                 # count AI-tone patterns
python scripts/humanizer_check.py original/ edited/           # compare two versions
```

The result line tells you:

- **0, match:** all recognized numbers, citations and math in the files it lists are the same and in the same order.
- **1, CHANGED:** something was added, lost or altered. Don't use that edit until it's fixed.
- **2, REVIEW:** the same items are there but in a different order. Check that no number or citation moved to the wrong claim.
- **3, INCOMPLETE:** nothing changed in what it checked, but part of the document couldn't be checked (for example a missing `\input` file). Fix that and run it again.

The checker counts and compares. It can't tell whether a number still belongs to the right claim, so always read through the edits listed at the top of the report. Its lists of vague sentences and possible prompt leftovers are things to look at, not errors.

## Good to know

- Works best for computer science, engineering and other quantitative fields. For humanities or medical writing, add to your prompt: *"Follow the conventions of [your field] where they conflict with Part 2."*
- It does not translate. Chinese stays Chinese, English stays English.
- It is not built to beat AIGC detectors (知网, 维普, 万方 or others), and no detector result is guaranteed. The goal is writing that reads well to a human.
- This is an editing aid, not a way to hide AI use. If your school or venue requires an AI-use statement, you still need it.
