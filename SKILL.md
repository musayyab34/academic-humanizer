---
name: academic-humanizer
description: Line-edit an academic paper (LaTeX, Markdown or Word) to remove AI-writing tone while keeping every number, citation, equation, term and claim unchanged. Use when asked to humanize, de-AI or fix the tone of a research paper.
---

# Humanizer: a rule book for removing AI tone from academic papers

Version 1.4 · November 2026

## Part 0. What this is for

The goal is prose that reads like a careful researcher wrote it: specific, plain, varied and confident where the evidence allows. AI-generated academic text has a recognisable texture. It favours connective tissue over content: dramatic colons, balanced contrasts, stock intensifiers, summary sentences that repeat the paragraph, and sentences that all run the same length. Removing that texture is mostly a matter of finding the fact a stock phrase is standing in for, and letting the fact speak.

Surface patterns are symptoms. The underlying problem in AI-drafted text is usually genericness: sentences that could sit unchanged in any paper on the topic. Deleting stock words without making the text more specific gives text that is harder to flag but no better to read.

This guide is **not**:

- **A rewrite tool.** The paper's structure, argument and claims stay as they are. You change wording at the sentence level.
- **A casualiser.** Generic "humanizer" tools push text toward chatty blog prose (contractions, "honestly", rhetorical questions). That is wrong for a paper.
- **A detector-evasion tool.** The target is good writing, judged by a human reader. Do not add typos, odd word choices or random noise to fool a classifier.
- **A replacement for disclosure.** If a venue requires an LLM usage statement, it is still required after this edit.

---

## Part 1. Hard constraints (never break these)

These outrank every rule below. If a style fix would touch one of them, skip the fix.

1. **Numbers.** Every number, percentage, unit, range, sign and decimal place stays exactly as written, attached to the same quantity and condition. Do not round, convert ("half" for "50%"), or move a number into a different claim.
2. **Citations.** Every citation marker (`[12]`, `\cite{key}`, `[@key]`, "Smith et al. (2022)") stays, attached to the same claim. Do not add, drop, merge or move citations between sentences that make different claims.
3. **Equations and math.** Do not touch anything in math mode, equation environments, variable names or symbols. Prose that defines a symbol keeps the definition word for word in meaning.
4. **Technical terms.** One concept, one name. Never swap a defined term for a synonym to "vary" the prose (see C6). Model, dataset, method and metric names are fixed.
5. **Claim strength and scope.** Do not make a claim stronger, weaker, broader or narrower, and do not add a causal or quantitative relationship the authors did not state. "Suggests" stays "suggests"; "outperforms on 4 of 5 datasets" does not become "consistently outperforms"; "is associated with" does not become "causes".
6. **Protected spans.** Text the user marks as protected is copied character for character. In files, protected spans are marked `<!-- keep -->` … `<!-- /keep -->` (Markdown) or with `% keep` and `% /keep` on their own lines (LaTeX).
7. **Structure.** Keep the order of sections, paragraphs and the main moves inside each paragraph. Keep headings, tables, figure references, labels, `\ref{}` targets and footnotes. You may split a sentence or reorder clauses inside a sentence. You may not move content between paragraphs.
8. **Markup.** In LaTeX or Markdown, never break commands, environments, labels or list syntax. Edit only the words between them.
9. **No new content.** Never add facts, numbers, citations, examples or reasoning the authors did not give. Sentences may be deleted only when they are pure restating closers (C2), meta-commentary (C3) or generic sentences that carry no fact, number or citation (D5).

If any constraint is ambiguous for a sentence, leave the sentence alone and list it in the report.

---

## Part 2. The target register

Human academic prose in ML/CV/NLP papers has these features. Move the text toward them.

- **Active voice with "we"** for what the authors did: "We train…", "We find…". Passive is fine when the agent truly doesn't matter ("The images are resized to 224×224").
- **Tense.** Present tense for what the paper shows and for general facts ("Table 2 shows…"). Past tense for specific actions taken ("we trained for 90 epochs").
- **Specific verbs.** "reduces", "doubles", "fails on", "matches", "drops by". Avoid vague verbs such as "addresses", "tackles", "enhances", "facilitates" when the sentence already contains a more precise one.
- **Confident, defensible claims.** State what the evidence supports, plainly, once.
- **No contractions, slang, humour, exclamation marks or first person singular** (unless the paper is single-authored and the venue allows "I").
- **Varied sentence length.** Mix short, medium and longer sentences. Uniformity in either direction reads as machine-made.
- **Consistent terminology,** even if it feels repetitive. Repetition of a defined term is a feature in technical writing.
- **Continuity.** Each sentence starts from something the reader already has and ends on what is new (C8).

---

## Part 3. Pattern catalogue

Patterns come in two kinds:

- **Hard rules (marked HARD).** These are house preferences with a clear fix: em dashes, colon reveals, "not only … but also", rhetorical questions, stock words and phrases, results used as subjects of thinking verbs, and chatbot leftovers. Remove every occurrence outside the listed allowed uses.
- **Targets (marked TARGET).** Everything else. Fix an occurrence when it makes the sentence worse. Leave it when it is the clearest way to say the thing.

**Stop rule.** Once a paragraph meets the hard rules and reads well, stop editing it. Do not keep changing text to hit a target number. Do not explain harmless occurrences of review words in the report.

Budgets apply to body text. Titles, tables and equations are exempt unless stated.

### A. Punctuation and syntax

#### A1. Em dashes (HARD: 0)
**Looks like:** "Three datasets — CIFAR-10, SVHN and ImageNet — were tested." Also LaTeX `---` and spaced hyphens or en dashes used as dashes (" - ", " – ").
**Fix:** Use commas, parentheses (sparingly), or split into two sentences. Do not replace every dash with " - " or with parentheses; that keeps the same rhythm.
**Before:** Our method is fast — about 3× faster than the baseline — and uses less memory.
**After:** Our method runs about 3× faster than the baseline and uses less memory.
**Allowed:** En dashes in number ranges (`1–5`, `pp. 12–20`) and compound names (Kullback–Leibler). Hyphens in compound words.

#### A2. Colon reveals (HARD: 0 in prose)
**Looks like:** A setup clause, a colon, then the "answer". "The prediction is specific: the last three layers carry the effect." "The reason is simple: …" "One thing stands out: …"
**Fix:** State the content directly. Delete the setup clause.
**Before:** The result is clear: data augmentation reduces errors by 41%.
**After:** Data augmentation reduces errors by 41%.
**Allowed:** Colons that introduce a list, a definition, a formal research question, a title/subtitle, or an algorithm field ("Input: …").

#### A3. Semicolon chains (TARGET: at most 1 per page)
**Looks like:** Independent clauses glued with semicolons to sound weighty. "The loss converges; the gap closes; the variance remains."
**Fix:** Split into separate sentences, or join with a real connective ("and", "but", "because", "so").
**Allowed:** Separating list items that themselves contain commas.

#### A4. "X, not Y" and "rather than" contrasts (TARGET: at most 1 per section)
**Looks like:** "It is not X; it is Y", "This is not merely X but Y", and contrasts whose negated half adds nothing.
**Fix:** If the negated half is rhetorical, state the positive claim. If the contrast carries information (a scope decision, a design choice, a comparison the paper tests), keep it and state it once, plainly.
**Before:** The improvement is not merely incremental; failures drop by 41%.
**After:** Failures drop by 41%.
**Leave alone:** "Our goal is to explain why existing pruning methods fail, not to propose a new one." This contrast defines the paper's scope.

#### A5. "Not only … but also" (HARD: 0)
**Fix:** "X and Y", or two sentences.
**Before:** The method not only improves accuracy but also reduces memory.
**After:** The method improves accuracy and reduces memory.

#### A6. Trailing "-ing" clauses (TARGET: 0)
**Looks like:** A finished sentence followed by ", highlighting…", ", demonstrating…", ", underscoring…", ", indicating that…", ", thereby…", ", making it…".
**Fix:** If the tail only restates the sentence, delete it. If it states an inference, give it its own sentence at the same strength the authors used. Never upgrade "highlighting the importance of" to a claim about how much something explains. If you can't tell what strength the authors meant, keep the tail and flag it.
**Before:** Accuracy drops from 78.4% to 61.2% on the shifted split, demonstrating a substantial decrease in performance.
**After:** Accuracy drops from 78.4% to 61.2% on the shifted split.

#### A7. "Therefore / thus / hence" (TARGET: at most 1 per page outside derivations)
**Fix:** Delete it when the order of the sentences already makes the logic plain. Use "so" or "because" where a link is needed. Do not swap in "consequently" or "accordingly", which are the same device.
**Keep a connective** when deleting it would leave two observations whose relationship the reader has to guess (see C8).
**Allowed:** Mathematical derivations and proofs.

#### A8. Rhetorical questions (HARD: 0)
**Looks like:** "But does this hold for larger models?" "Why does this happen?"
**Fix:** State the question as a statement of what you test. "We next test whether the effect holds for larger models."
**Allowed:** Formally numbered research questions (RQ1, RQ2).

### B. Vocabulary

#### B1. Stock AI words (HARD: 0)
Remove or replace: delve, stark, crucial, pivotal, notably, moreover, furthermore, additionally, importantly, interestingly, leverage, underscore, showcase, intricate, tapestry, realm, landscape, seamless(ly), multifaceted, paramount, foster, harness, unlock, unleash, bolster, elevate, meticulous, commendable, noteworthy, invaluable, holistic, synergy, groundbreaking, cutting-edge, game-changing, transformative, unprecedented, nuanced, garner, ever-evolving, enhance, insights, valuable, encompass, endeavour.
Replacement table: Appendix A. The usual best fix is deletion, not a synonym.

#### B2. Stock phrases (HARD: 0)
"It is worth noting that", "It is important to note", "It should be noted", "sheds light on", "paves the way for", "a testament to", "in the realm of", "the landscape of", "navigate the complexities", "a deeper understanding of", "in today's world".
**Fix:** Delete the frame and keep the content.
**Before:** It is worth noting that accuracy fell on the shifted split.
**After:** Accuracy fell on the shifted split.

"Plays a crucial/key/vital role in" is a special case: it is often a vague stand-in for a claim the authors never made precise. Remove "crucial" (B1). Replace the frame with a plain verb only when the verb says exactly what the authors claimed. Otherwise keep "plays a role in" and flag the sentence. Never turn it into "causes" or "determines".

#### B3. Template openers (HARD: 0)
"With the rapid development of…", "In recent years, X has attracted increasing attention", "has been widely used in various fields", "a large number of", "effectively improves", "aiming at".
**Why they fail:** they postpone the research problem, repeat the section heading, or make a trend claim with no support.
**Fix:** Delete the frame so the paragraph starts with its specific problem. If the trend claim carries a citation, keep it in plain form ("X is an active research area [5]").
**Before:** With the rapid development of deep learning, model compression has attracted increasing attention. Model compression reduces the memory and compute a trained network needs [3, 7].
**After:** Model compression reduces the memory and compute a trained network needs [3, 7].

#### B4. Words that are fine only when precise (review every hit)
- **significant / significantly:** only for statistical significance with a test. Otherwise use "large", "clear", or the number the sentence already gives.
- **robust:** only when robustness was actually tested. Say to what, if the paper says.
- **novel:** keep only if the authors insist; reviewers decide novelty.
- **comprehensive / extensive:** prefer the counts the paper already reports ("on 6 datasets and 3 model sizes").
- **effectively, various, remarkably, dramatically, substantially, key, essential, vital, serves as, utilize:** replace with the plain word ("works", "several", "uses", "is") when it means the same.

#### B5. Intensifier and hedge stacks (TARGET)
**Intensifiers:** "very", "highly", "extremely", "truly", "clearly". Delete them.
**Hedge stacks:** "may potentially", "could possibly", "might suggest that it is possible". Keep one hedge, at the strength of the strongest original hedge.

#### B6. Nominalisations (TARGET)
"the utilisation of" → "using"; "perform an evaluation of" → "evaluate"; "achieve an improvement in" → "improve"; "make a comparison" → "compare".

#### B7. Results used as the subject of "thinking" verbs (HARD: 0)
**Looks like:** "These results highlight…", "This finding emphasizes…", "Figure 3 reveals…", "The analysis underscores…", "Our experiments illuminate…". A result cannot highlight or emphasise anything; people do. This is one of the strongest single tells.
**Fix:** State the result directly, or make the authors the subject ("We find…"). Keep any reference the sentence had.
**Before:** These results highlight the sensitivity of the model to batch size (Table 3).
**After:** The model is sensitive to batch size (Table 3).
**Allowed:** "Figure 3 shows…", "Table 2 lists…". Plain reporting verbs are fine.

#### B8. Academic excess vocabulary (review every hit)
Large studies of millions of abstracts found that after LLMs became common, the increase was mostly in style words (verbs and adjectives), not content words. Treat these as review words: potential, critical, particularly, exhibit, align with, comprehensive. Each is fine when it is the most precise word. Each is a tell when several appear in one paragraph doing no work.
Prepositions such as "across" and "within" are not tells: "across seeds" and "within each seed" distinguish two levels of analysis. The test is whether the reader gets the distinction right on first reading.

### C. Sentence and paragraph shape

#### C1. Long sentences (TARGET: none over ~35 words)
Split anything over about 35 words at a natural joint, then apply C8 so the pieces still connect. After splitting, check the paragraph: if every sentence is now 10–14 words, it reads as choppy. Re-join where two short sentences make one thought.
The checker reports mean sentence length and spread. Treat these as information for your own reading, not as pass/fail tests.

#### C2. Paragraph-closing summary sentences (TARGET)
**Looks like:** The last sentence restates the paragraph. "Overall, these results show that…", "Taken together, …", "In short, …", "Collectively, …".
**Fix:** If it only repeats what the paragraph already said, delete it. If it is the first place the paragraph draws its inference, keep it. You may remove the stock opener ("Overall, these results show that X" → "X") as long as the claim keeps the same strength.
**Allowed:** The final paragraph of the Conclusion; the contribution list in the Introduction.

#### C3. Signposting and meta-commentary (TARGET)
"In this section, we delve into…", "Let us now turn to…", "As mentioned above, …", "As we will see, …".
**Fix:** Delete. Section headings already signpost. Keep one-line roadmaps where the venue expects them (for example at the end of the Introduction).

#### C4. Reflex triplets (TARGET)
Lists of exactly three adjectives used for rhythm ("efficient, scalable and robust"). Drop items the paper does not support with evidence, by flagging them rather than deleting them yourself.
**Leave alone:** lists whose items are real components. "The pipeline has three parts: a data loader, a feature encoder and a classifier head." Every item names part of the method.

#### C5. "This" openers without a noun (TARGET)
"This shows…", "This suggests…" at the start of many sentences. Add the noun the paragraph already uses ("This gap shows…") or merge with the previous sentence.

#### C6. Synonym cycling (TARGET)
Models rotate names to avoid repetition: "the model", "the method", "our approach", "the technique", "the framework" for one thing. This creates doubt about whether these are different objects.
**Fix:** Pick the defined name and use it throughout. If you can't tell whether two names mean the same thing, flag it.

#### C7. Identical paragraph templates (TARGET)
Every paragraph built as topic sentence, three supporting sentences, summary. Vary the shape where the content allows: lead with the number, lead with the comparison, end on the evidence. Do not move content between paragraphs.

#### C8. Continuity between sentences (always check)
After you split a sentence, delete a transition or delete a closer, read the previous sentence, the edited one and the next one together. The reader must still be able to tell what carries over and what is new.
- Start a sentence with information the reader already has (the condition, the model, the setting) and end it on the new result.
- Repeating a condition is worth it when it tells the reader which setting a number belongs to.
- Add such a phrase only when the original makes the condition clear (in the text or a cited table). If it doesn't, flag the ambiguity instead.

**Before:** Raising the learning rate from 1e-4 to 3e-4 increases training accuracy from 88.1% to 90.3% while lowering validation accuracy from 81.2% to 79.0%, and with warm-up validation accuracy at that rate improves to 83.5%.
**After:** Raising the learning rate from 1e-4 to 3e-4 increases training accuracy from 88.1% to 90.3% while lowering validation accuracy from 81.2% to 79.0%. At 3e-4, adding warm-up improves validation accuracy to 83.5%.
The split works because the manipulation changes (learning rate, then warm-up). "At 3e-4" carries the condition the original stated ("at that rate") into the new sentence.

### D. Claims

#### D1. Inflated significance (TARGET)
"profound implications", "fundamentally changes", "opens new avenues", "a paradigm shift". Delete the inflation and keep the concrete consequence the authors state. If none is stated, flag it.

#### D2. Overclaiming words (flag)
"irreducible", "universal", "always", "proves", "solves", "consistently" when the paper's own evidence covers only some settings. Do not narrow the claim yourself. Flag it with the evidence that seems to limit it, and let the authors decide.

#### D3. Vague attribution
"Studies have shown", "It is widely believed", "Researchers argue". If the paper cites a source for this exact claim nearby, you may attach that existing citation. Otherwise leave the claim as it is and flag it (Part 3 F). Never delete the claim and never invent a citation.

#### D4. Over-hedging (TARGET)
Results the paper measured directly can be stated plainly: "Accuracy drops by 7.3 points", not "It appears that accuracy may decrease". Remove a hedge only when it qualifies a direct measurement. Keep hedges on mechanisms and explanations ("We hypothesise that…").

#### D5. Generic sentences (the swap test)
Ask of each sentence: could it appear unchanged in a different paper on the same topic? "Model compression is an important problem with many applications." "Our results provide valuable insights for future research." If it carries no fact, number or citation, delete it. If it does, keep the fact and remove the generic frame. Never add new facts to make it specific.

### E. Chatbot leftovers (HARD: remove on sight)

These are the most damaging tells because they prove unreviewed AI output:
- Assistant phrases: "Certainly!", "Here is the revised paragraph", "I hope this helps", "As an AI language model", "Let me know if…", "Great question".
- Knowledge-cutoff disclaimers: "As of my last update…".
- Markdown in LaTeX source: `**bold**`, `*italics*`, `#` headings, backtick code. Use the LaTeX the paper already uses.
- Curly quotes in LaTeX source (“ ” ‘ ’). Use ``` `` ``` and `''`. Emojis anywhere.

Placeholders are different: "[citation needed]", "[insert dataset]", "XX%", "TODO". Do not fill them. List them in the report.

### F. Flag, do not fix

These problems need the authors, not an editor. This section takes precedence over any rule above that seems to allow a fix. Leave the text as it is and list each item in the report: the exact sentence, what is missing or wrong, and the options (supply evidence, narrow the claim, or remove it).
- **References that look fabricated or unverifiable:** wrong years, authors who don't match the title, venues that don't exist, a reference cited for a claim it probably doesn't support.
- **Claims without evidence:** a factual claim with no citation, table or figure behind it.
- **Overclaims** the paper's own evidence seems to limit (D2).
- **Discussion that only restates results:** paragraphs with no interpretation, limitation or comparison. Don't write the interpretation yourself.
- **Terminology conflicts you can't resolve:** two names that might or might not be the same object.
- **Numbers that disagree** between the text, tables and abstract.

### G. Formatting inside prose (TARGET)

- No bold or italics for emphasis in running text, except defined terms on first use if the venue allows.
- No bullet lists where the venue expects paragraphs (Related Work, Discussion).
- No scare quotes around ordinary words.
- Headings: keep the paper's convention.

---

## Part 4. Procedure

Follow these steps in order. Do not skip step 1 or step 6.

1. **Find every file and lock the invariants.** If the paper is a LaTeX project, open the main file and list every file it pulls in through `\input` and `\include`; all of them are the paper. List the numbers, citation markers, math, key terms (from the user, or the most frequent technical nouns) and protected spans. If you can run code, run the checker (Appendix B) on the original and keep the output.
2. **Note the hard-rule hits.** Record where the HARD patterns occur (the checker counts them).
3. **Edit paragraph by paragraph.** For each paragraph:
   a. Read it once for meaning. Write down (to yourself) its main claim and its strength.
   b. Remove the HARD patterns.
   c. Fix TARGET patterns where they make a sentence worse.
   d. Check continuity (C8) around every split or deletion.
   e. Re-read: the main claim must be identical in content and strength, and each number and citation must still belong to the same claim.
   f. Apply the stop rule: when the paragraph reads well, move on.
4. **Read the section through.** Fix choppiness: if three short sentences in a row share a subject, join two of them.
5. **Recheck the hard rules.** Run the checker on the edited version. Every HARD pattern should be gone except allowed uses.
6. **Verify the invariants.** Run the checker on the original and the edited version together. Then read the diff yourself, sentence by sentence, for what no counter can see: which model, metric, condition and citation each number belongs to.
7. **Write the outputs** described in Part 7.

For long documents, work one section at a time.

---

## Part 5. Mistakes humanizers make (avoid all of these)

- **Rewriting instead of editing.** If more than about a third of a paragraph's words change, you are rewriting. Back off.
- **Editing past the point of improvement.** A paragraph that already reads well is finished, even if it contains a semicolon or a review word.
- **Swapping one stock word for another.** "Moreover" → "Additionally" → "Furthermore" fixes nothing. Delete the connective.
- **Casual tone:** contractions, "pretty", "a lot", "basically", "honestly", "turns out".
- **Deliberate errors** (typos, broken grammar) to look human.
- **Thesaurus edits to technical terms:** "accuracy" → "precision", "fine-tuning" → "adjustment". These change meaning.
- **Tortured phrases.** Paraphrasing tools turn established terms into nonsense synonyms ("counterfeit consciousness" for "artificial intelligence", "profound learning" for "deep learning", "irregular woodland" for "random forest"). Research-integrity screeners search for exactly these. An established term is never paraphrased.
- **Dash laundering:** replacing every em dash with a spaced hyphen, a pair of parentheses or a colon.
- **Choppy output:** every sentence 8–12 words, with the links between them deleted.
- **Changing hedges:** adding them to sound modest, or removing ones the evidence needs.
- **Deleting content** that looks like filler but carries a fact, number or citation.
- **Adding content:** new examples, claims, citations, or transitions that introduce reasoning the authors did not give.
- **Editing protected spans** or quotations.
- **Touching the LLM usage statement** beyond grammar.

---

## Part 6. Section-specific notes

- **Title.** Leave it unless asked.
- **Abstract.** Keep its moves in the same order (typically context, gap, approach, results, implication). Tighten wording only. Every number stays with its condition. Delete a generic opener (B3) if the next sentence already states the problem.
- **Introduction.** Keep the flow and the contribution list. Remove adjectives from contributions ("a novel, effective framework") without adding claims.
- **Related work.** Keep it organised by research line. Remove "has attracted attention" frames.
- **Method.** Mostly leave alone. Edit only connective prose between equations. Never paraphrase a definition.
- **Experiments.** Keep each comparison like-for-like (same model, same setting on both sides) exactly as the original states it. Splitting long result sentences helps most here; apply C8 every time.
- **Figure and table captions.** Light edits only: stock words and dashes. Captions must still describe exactly what is plotted.
- **Limitations and conclusion.** One closing summary paragraph is allowed.
- **LLM usage statement, ethics statement, acknowledgements.** Grammar only.

---

## Part 7. Output and report

**Produce the edited paper and a separate standalone report. Nothing else.**

1. **The edited paper.**
   - Single-file paper: one file in the same format, named `<original name>_humanized.<ext>` (`paper.tex` → `paper_humanized.tex`).
   - Multi-file LaTeX project: one edited copy of the source tree in a folder named `<project name>_humanized/`, with the same file names and structure.
   - If you were given LaTeX, Word or Markdown source, edit the source. The paper contains the paper and nothing else.
2. **The report.** A separate, standalone Markdown file named `<original name>_humanizer_report.md`.

**Never append the report to the paper, and never produce a second copy of the paper with the report attached.** Do not paste the edited text into the report; quote only the sentences the report discusses. In your chat reply, name the output files and give a one-line result.

Report contents, most important first:

```
# Humanizer report: <paper name>

## 1. Edits that may change meaning
<every edit where the claim, its strength, or which condition a number or citation belongs to
could have shifted, with before and after. Write "none" if none.>

## 2. Flags for the authors
<Part 3 E placeholders and Part 3 F items: location, the exact sentence, what is missing,
the options>

## 3. What was verified
Files examined: <list, including every \input/\include file; list any file not examined and why>
Checker result: <its RESULT line>, or "checker not run" and how you checked by hand
Key terms: checked / not checked (no list given)
Protected spans: checked / none marked
Not verifiable by counting: which claim each number and citation belongs to; you checked this
by reading the diff

## 4. Hard-rule hits kept on purpose
<only HARD patterns left in place because they are allowed uses: pattern, location, reason>

## 5. Pattern counts
| Pattern | Before | After |
<the checker's marker table>
```

If any invariant changed, fix it before returning. Never return a paper with a changed number, citation, equation or protected span.

---

## Part 8. Final checklist

- [ ] Every file of the paper was examined (including `\input`/`\include` files)
- [ ] All numbers, signs, units, citations, equations and key terms identical to the original
- [ ] Each number and citation still attached to the same claim and condition
- [ ] Protected spans identical, character for character
- [ ] Same sections, same paragraphs, same order
- [ ] No claim stronger, weaker, broader or narrower than before; nothing added
- [ ] Every HARD pattern removed, or kept as an allowed use and listed
- [ ] Continuity checked around every split and deletion
- [ ] Register is formal academic: no contractions, slang, humour or rhetorical questions
- [ ] Markup compiles (LaTeX) or renders (Markdown) exactly as before
- [ ] Output is the edited paper plus a separate standalone report, nothing appended

---

## Appendix A. Replacement table

The first option is almost always to delete the word. Use a replacement only if it means exactly what the original meant.

| Remove | Use instead (or delete) |
|---|---|
| moreover, furthermore, additionally | delete; or "also"; or start a new sentence |
| notably, importantly, interestingly | delete |
| crucial, pivotal, paramount, vital | delete; or "main" or "necessary" when the original means exactly that |
| stark (contrast, difference) | delete; the numbers the sentence gives show the size |
| delve into | examine, study |
| leverage | use |
| underscore, highlight (about results) | delete and state the result; or "show" |
| showcase | show |
| foster, bolster, elevate, enhance | improve, increase, support (whichever the authors mean) |
| harness, unlock, unleash | use |
| seamless(ly) | delete |
| robust (untested) | delete |
| significant (no test) | large, clear |
| comprehensive, extensive | delete, or the counts the paper gives |
| intricate, multifaceted, nuanced | complex; or delete |
| landscape, realm, tapestry | delete; name the field |
| insights, valuable | delete, or say what was learned if the paper states it |
| plays a crucial role in | see B2; never "causes" or "determines" |
| sheds light on | shows, explains (whichever the authors mean) |
| paves the way for | delete, or "enables" only if the authors claim that |
| a testament to | shows |
| it is worth noting that | delete |
| utilise / utilisation | use |
| in order to | to |
| due to the fact that | because |
| a large number of | many; or the number the paper gives |
| therefore, thus, hence | delete; or "so" (see A7) |

---

## Appendix B. Checker script

The checker is `scripts/humanizer_check.py` in this skill's folder: Python 3, standard library only, Markdown or LaTeX source. If you can run code, use it. If you can't, do the same checks by hand.

```
python scripts/humanizer_check.py paper.tex                          # hard-rule and pattern counts
python scripts/humanizer_check.py before/ after/                     # compare two versions (files or folders)
python scripts/humanizer_check.py before.tex after.tex --terms terms.txt --protect protect.txt
```

- A LaTeX main file is followed through `\input` and `\include`. A folder is read from its main `.tex` file (the one with `\documentclass`), or as all `.tex`/`.md` files if there is none. The output lists every file examined and any file it could not find.
- **Verifies:** numbers with their signs and units, citation keys and markers, math (including `$…$`, `\(…\)`, `\[…\]` and equation environments), protected spans (marked in the file or listed one per line in `--protect`), and key terms (one per line in `--terms`). Each is checked for count and for order.
- **Does not verify:** whether each number and citation still belongs to the same claim. Read the diff for that.
- **Exit codes:** 0 = recognized items match in count and order. 1 = something was added, lost or changed: fix it. 2 = the same items appear in a different order: check whether a number or citation moved to a different claim.
