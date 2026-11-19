# Changelog

All notable changes to the Academic Humanizer. Newest first.

## 1.6 · 2026-11-20

### Fixed
- The checker now reads weekly reports written as bullet lists. Before, list items were skipped, so a weekly report could show zero text and no vague sentences.
- The checker no longer crashes when it prints Chinese on a Windows console. The tests now check the result line as well as the exit code, so a crash can never pass as "change detected".
- The checker now catches unit changes (2 cm → 2 mm, 2毫秒 → 2秒), sign changes in scientific notation (1e-3 → 1e+3), and changed author names in Chinese citations such as 张伟等（2021）.
- In a folder with more than one LaTeX document (for example a paper and its supplement), the checker now checks all of them, not only the first.
- A missing `\input` file, or `--protect` text that isn't in the original, now gives a new result, 3 (INCOMPLETE), instead of a clean match.
- Word files: native equations, footnotes and endnotes are now checked. Heading styles are recognised.
- LaTeX abstracts are now included in the pattern counts. Before (since 1.0), an abstract written inside `\begin{abstract}` was skipped entirely.
- Pseudocode, code listings and tables are left out of the prose counts, so semicolons in an algorithm no longer count as style problems.
- An English sentence that quotes a long Chinese passage is now treated as English. Quotations no longer decide a paragraph's language.
- Word equations: a superscript changed to a subscript (x² → x₂) is now detected.
- The test runner itself no longer crashes on a Windows console.
- Guide examples that changed meaning were corrected: the 具有重要意义 example is now a flag-and-ask example, the 不是……而是 example keeps scope-defining contrasts, and the translationese example keeps "输入的".

### Changed
- Evasive-writing and prompt-leftover results are listed one per sentence with their location, and sentences that already contain a number are marked as possibly complete.
- Hedges: only redundant pairs ("may potentially") are collapsed. Qualifiers that do different jobs are kept.
- Prompt leftovers: prompts that are part of the research, quotations and template labels are kept ("mention is not use").
- The Chinese sentence-length figure (100 characters) is described as a reading cue, not a rule.
- Documentation states exactly what the checker reads and verifies, and what it doesn't.

### Added
- A contrast test for "not X but Y" and 不是……而是 (A4).
- A meaning check for edited result sentences: who, condition, comparator, outcome, direction and certainty must match the original (Part 4, step 6).
- Established technical terms that contain a listed word ("loss landscape") are allowed, and parallel descriptions that help comparison are left alone (B1, C7).
- In papers, theses and proposals, the evasive-writing list only flags results with no number and claims with no source.
- A zero-edit check in the final checklist: restore any passage where the original was more accurate.
- A scope line in the report, so an excerpt is never reported as a whole-document check.
- Part 2B states that English-only documents skip the Chinese rules entirely.
- This changelog.

## 1.5 · 2026-11-20

### Added
- Chinese support: language decided per paragraph, a Chinese rule set (section H) and Chinese punctuation rules based on GB/T 15834-2011.
- Evasive-writing section (I) for all languages: vague sentences are listed with the question the author must answer, never filled in.
- Document types: papers, theses, proposals (开题报告), midterm reports (中期报告), lab reports and weekly reports.
- Checker: Word (`.docx`) files, Chinese pattern counts, evasive-phrase counts, numbers and citations inside Chinese text.
- Chinese README (`README_zh.md`).

## 1.4 · 2026-11-14

### Added
- Hard rules and targets, a stop rule, and a continuity rule (C8).
- Report written as a separate file, with meaning-changing edits first.
- Checker: signs and units, swapped values and citations, `\(...\)` math, protected spans, `\input` files, regression tests.

### Changed
- Examples rewritten so they only remove filler and never add claims.

## 1.0 to 1.3 · 2026-11-13 to 2026-11-14

- First versions of the rule book and checker for English research papers.
