---
name: academic-humanizer
description: Line-edit academic writing in English or Chinese (papers, theses, proposals, midterm, lab and weekly reports; LaTeX, Markdown or Word) to remove AI-writing tone and flag evasive writing, while keeping every number, citation, equation, term and claim unchanged. Use when asked to humanize, de-AI, 去AI味 or fix the tone of academic writing.
---

# Humanizer: a rule book for removing AI tone from academic writing

Version 1.6 · November 2026

## Part 0. What this is for

The goal is prose that reads like a careful researcher wrote it: specific, plain, varied and confident where the evidence allows. AI-generated academic text has a recognisable texture. It favours connective tissue over content: dramatic colons, balanced contrasts, stock intensifiers, summary sentences that repeat the paragraph, and sentences that all run the same length. Removing that texture is mostly a matter of finding the fact a stock phrase is standing in for, and letting the fact speak.

Surface patterns are symptoms. The underlying problem in AI-drafted text is usually genericness: sentences that could sit unchanged in any paper on the topic. Deleting stock words without making the text more specific gives text that is harder to flag but no better to read.

**Scope.** The guide covers academic writing in English and Chinese: journal and conference papers, theses, research proposals (开题报告), midterm reports (中期报告), lab reports and weekly progress reports. Part 1, the procedure and the report apply to all of them. Some pattern rules apply to one language only (Part 2B decides which), and each document type has its own allowances (Part 6).

This guide is **not**:

- **A rewrite tool.** The document's structure, argument and claims stay as they are. You change wording at the sentence level.
- **A casualiser.** Generic "humanizer" tools push text toward chatty blog prose (contractions, "honestly", rhetorical questions). That is wrong for a paper.
- **A detector-evasion tool.** The target is good writing, judged by a human reader. Do not add typos, odd word choices, slang or random noise to fool a classifier. This includes AIGC checks such as CNKI (知网), VIP (维普) or Wanfang (万方): the guide does not target any detector score, and no result is guaranteed.
- **A translator.** Edit each passage in the language it is written in. Never translate.
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
7. **Structure.** Keep the order of sections, paragraphs and the main moves inside each paragraph. Keep every heading of a school or venue template exactly as written. Keep headings, tables, figure references, labels, `\ref{}` targets and footnotes. You may split a sentence or reorder clauses inside a sentence. You may not move content between paragraphs.
8. **Markup.** In LaTeX or Markdown, never break commands, environments, labels or list syntax. Edit only the words between them.
9. **No new content.** Never add facts, numbers, citations, examples or reasoning the authors did not give. Sentences may be deleted only when they are pure restating closers (C2), meta-commentary (C3) or generic sentences that carry no fact, number or citation (D5).

If any constraint is ambiguous for a sentence, leave the sentence alone and list it in the report.

---

## Part 2. The target register (English)

Human academic prose in English ML/CV/NLP papers has these features. For Chinese register, see Part 3 H11. Move the text toward them.

- **Active voice with "we"** for what the authors did: "We train…", "We find…". Passive is fine when the agent truly doesn't matter ("The images are resized to 224×224").
- **Tense.** Present tense for what the paper shows and for general facts ("Table 2 shows…"). Past tense for specific actions taken ("we trained for 90 epochs").
- **Specific verbs.** "reduces", "doubles", "fails on", "matches", "drops by". Avoid vague verbs such as "addresses", "tackles", "enhances", "facilitates" when the sentence already contains a more precise one.
- **Confident, defensible claims.** State what the evidence supports, plainly, once.
- **No contractions, slang, humour, exclamation marks or first person singular** (unless the paper is single-authored and the venue allows "I").
- **Varied sentence length.** Mix short, medium and longer sentences. Uniformity in either direction reads as machine-made.
- **Consistent terminology,** even if it feels repetitive. Repetition of a defined term is a feature in technical writing.
- **Continuity.** Each sentence starts from something the reader already has and ends on what is new (C8).

---

## Part 2B. Language: which rules apply

Decide the language of each paragraph before editing it. Count each Chinese character as one unit and each run of Latin letters as one unit, leaving out quotations, formulas and protected spans. A paragraph whose own prose is mostly Chinese gets the Chinese rules; otherwise it gets the English rules. An English sentence that quotes a long Chinese passage is still English. English terms, model names and formulas inside a Chinese paragraph stay exactly as they are.

| Rules | Apply to |
|---|---|
| Part 1 (hard constraints), Part 4 to 8 | every document, every language |
| Part 3 C2, C3, C6, C7, C8, D, E, F, G, I | every language |
| Part 2, Part 3 A, B, C1, C4, C5, Appendix A | English paragraphs only |
| Part 3 H | Chinese paragraphs only |

If a document contains no Chinese, ignore section H entirely; if it contains no English prose, ignore Part 2, sections A and B, C1, C4, C5 and Appendix A.

Never apply the English punctuation rules (A1 to A3) to Chinese. In Chinese, the dash (——), colon (：) and semicolon (；) have standard uses under GB/T 15834-2011, so zero-dash and zero-semicolon budgets would damage correct text. H9 covers Chinese punctuation.

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
**Contrast test (all languages).** For "not X but Y" and its Chinese forms, name X and Y and ask: is X something the document actually asserts, cites, tests or rules out? Would dropping X lose a real correction or exclusion? If yes, keep the contrast. Rewrite only when X is a generic downgrader ("just an engineering detail", "不仅仅是一组数字") and Y can stand alone without adding or removing a claim. If you can't tell, keep it and flag it.
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
**Allowed:** a listed word that is part of an established technical term, such as "loss landscape", "energy landscape" or "enhancer" in biology.

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
**Hedge stacks:** collapse redundant pairs that hedge the same thing ("may potentially", "could possibly") into one. Keep qualifiers that do different jobs: in "the pilot suggests that the intervention may help", "suggests" qualifies the evidence and "may" qualifies the effect, so both stay.

#### B6. Nominalisations (TARGET)
"the utilisation of" → "using"; "perform an evaluation of" → "evaluate"; "achieve an improvement in" → "improve"; "make a comparison" → "compare".

#### B7. Results used as the subject of "thinking" verbs (HARD: 0)
**Looks like:** "These results highlight…", "This finding emphasizes…", "Figure 3 reveals…", "The analysis underscores…", "Our experiments illuminate…". A result cannot highlight or emphasise anything; people do.
**Fix:** State the result directly, or make the authors the subject ("We find…"). Keep any reference the sentence had.
**Before:** These results highlight the sensitivity of the model to batch size (Table 3).
**After:** The model is sensitive to batch size (Table 3).
**Allowed:** "Figure 3 shows…", "Table 2 lists…". Plain reporting verbs are fine.

#### B8. Academic excess vocabulary (review every hit)
Large studies of millions of abstracts found that after LLMs became common, the increase was mostly in style words (verbs and adjectives), not content words. Treat these as review words: potential, critical, particularly, exhibit, align with, comprehensive. Each is fine when it is the most precise word. Each is a tell when several appear in one paragraph doing no work.
Prepositions such as "across" and "within" are not tells: "across seeds" and "within each seed" distinguish two levels of analysis. The test is whether the reader gets the distinction right on first reading.

### C. Sentence and paragraph shape

#### C1. Long sentences (TARGET: none over ~35 words)
English. For Chinese, see H10.
Split anything over about 35 words at a natural joint, then apply C8 so the pieces still connect. After splitting, check the paragraph: if every sentence is now 10–14 words, it reads as choppy. Re-join where two short sentences make one thought.
The checker reports mean sentence length and spread. Treat these as information for your own reading, not as pass/fail tests.

#### C2. Paragraph-closing summary sentences (TARGET)
**Looks like:** The last sentence restates the paragraph. "Overall, these results show that…", "Taken together, …", "In short, …", "Collectively, …".
**Fix:** If it only repeats what the paragraph already said, delete it. If it is the first place the paragraph draws its inference, keep it. You may remove the stock opener ("Overall, these results show that X" → "X") as long as the claim keeps the same strength.
**Allowed:** The final paragraph of the Conclusion; the contribution list in the Introduction; chapter summaries (本章小结) that a thesis template requires.

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
**Fix:** Use the name where the concept is defined or first formally introduced, not the most frequent one, and use it throughout, including captions and tables. Keep declared abbreviations. If you can't tell whether two names mean the same thing, flag it.

#### C7. Identical paragraph templates (TARGET)
Every paragraph built as topic sentence, three supporting sentences, summary. Vary the shape where the content allows: lead with the number, lead with the comparison, end on the evidence. Do not move content between paragraphs.
**Leave alone:** repetition that helps the reader compare. Parallel descriptions of ablations, experimental conditions or method steps should stay parallel. Repetition is a problem only when the repeated form does the same empty job each time.

#### C8. Continuity between sentences (always check)
After you split a sentence, delete a transition or delete a closer, read the previous sentence, the edited one and the next one together. The reader must still be able to tell what carries over and what is new.
- Start a sentence with information the reader already has (the condition, the model, the setting) and end it on the new result.
- Repeating a condition is worth it when it tells the reader which setting a number belongs to.
- Add such a phrase only when the original makes the condition clear (in the text or a cited table). If it doesn't, flag the ambiguity instead.

**Before:** We collect 12,000 street-scene images from four cities and label them with 19 classes, and because two of the cities have far fewer night-time images, we report night-time results only for the other two.
**After:** We collect 12,000 street-scene images from four cities and label them with 19 classes. Two of the cities have far fewer night-time images, so we report night-time results only for the other two.
The second sentence opens with something the reader already has (the cities) and ends on the new information (the reporting decision). "So" stays: without it, the reader has to guess why night-time results are limited.

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
- Assistant phrases: "Certainly!", "Here is the revised paragraph", "I hope this helps", "As an AI language model", "Let me know if…", "Great question". In Chinese: "好的！", "以下是修改后的版本", "根据您的要求", "希望对您有帮助", "作为AI语言模型", "如需进一步修改，请告诉我".
- Prompt text left in the document: instructions to the AI ("请帮我润色下面这段", "Rewrite the following"), word-count notes, or a pasted prompt above the text. Remove instructions that are clearly stray. If a sentence mixes a stray instruction with real content, remove only the instruction.
- **Mention is not use.** Keep prompts that are part of the research (an experiment's prompt shown in a table or appendix), quotations, form labels such as "要求：" in a template, and any passage that discusses these phrases as language. Flag anything ambiguous with its location.
- Knowledge-cutoff disclaimers: "As of my last update…".
- Markdown in LaTeX source: `**bold**`, `*italics*`, `#` headings, backtick code. Use the LaTeX the paper already uses.
- Curly quotes in LaTeX source (“ ” ‘ ’). Use ``` `` ``` and `''`. Emojis anywhere.

Placeholders are different: "[citation needed]", "[insert dataset]", "XX%", "TODO", "（此处补充数据）". Do not fill them. List them in the report.

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
- No bullet lists where the venue expects paragraphs (Related Work, Discussion). Weekly reports and lab procedures may use lists (Part 6).
- No scare quotes around ordinary words.
- Headings: keep the paper's convention.

### H. Chinese text (中文)

These rules apply to Chinese paragraphs only (Part 2B). They follow the same HARD/TARGET logic and the same stop rule as the English sections.

They are based on patterns that Chinese editors and writing guides report again and again, and on a corpus study that compared ChatGPT's Chinese with human Chinese (Zhu et al., CCL 2023). That study compared answers to open-domain questions, not theses or reports. It found the AI text used longer words, more nouns, far fewer modal particles, lower lexical variety and less variation in sentence length, while overall punctuation density was the same. So no single sign proves anything, and the lists below are editing cues, not proof of AI use. Look for clusters, and judge each phrase by what it does in its sentence.

#### H1. Template openers 模板化开场 (HARD: 0)
**Looks like:** "随着……的快速发展", "近年来，……受到越来越多的关注", "在……的背景下", "在当今社会", "众所周知".
**Fix:** Delete the frame so the paragraph starts with its specific problem. If the trend claim carries a citation, keep it in plain form ("……是当前的研究热点[5]").
**Before:** 随着深度学习的快速发展，模型压缩受到了越来越多的关注。模型压缩旨在降低神经网络的存储和计算开销[3,7]。
**After:** 模型压缩旨在降低神经网络的存储和计算开销[3,7]。

#### H2. Stock connectives and sentence openers 套话连接词 (HARD for the first list, TARGET for the second)
**HARD:** "值得注意的是", "值得一提的是", "需要指出的是", "不难看出", "显而易见", "毋庸置疑", "从多个维度来看", "从更深层次来看".
**TARGET:** "此外", "与此同时", "综上所述", "由此可见", "总而言之", "具体而言" stacked at the start of sentence after sentence, and "首先……其次……最后" for content that has no real order.
**Fix:** Delete them and let the order of sentences carry the logic. Keep a connective when deleting it would leave the relationship unclear (C8). Keep "首先/其次" for real steps in a procedure.
**Before:** 值得注意的是，该方法在小样本条件下的准确率下降了4.2%。
**After:** 在小样本条件下，该方法的准确率下降了4.2%。

#### H3. Empty significance 空泛拔高 (HARD: 0)
**Looks like:** "具有重要意义", "发挥着关键作用", "起到了重要作用", "至关重要", "不可或缺", "奠定了坚实基础", "提供了有力支撑", "开辟了新路径", "彰显了".
**Fix:** If the sentence already states the concrete consequence, delete the slogan and keep the consequence. Often it doesn't: "具有重要意义" is itself the authors' claim, so deleting it or turning it into a description of use changes what they say. Then keep the sentence and flag it with a question.
**Example (flag, don't edit):** 该数据集包含12类噪声样本，对提升模型鲁棒性具有重要意义。
**Report entry:** 文中哪项结果说明这12类噪声样本与模型鲁棒性有关？
**Exception:** A section a template titles 研究意义 must state significance. There, replace the slogan with the specific significance the author gives; if the author gives none, flag it.

#### H4. Hollow buzzwords 空洞大词 (HARD: 0)
**Looks like:** "赋能", "助力", "深度融合", "全方位", "多维度", "全链条", "抓手", "闭环", "底层逻辑", "重塑", "一站式", "新赛道", figurative "生态".
**Fix:** Say who does what. Keep a word when it is the field's technical term (闭环控制 in control theory, 生态 in ecology).
**Before:** 本文提出的框架全面赋能多模态检索。
**After:** 本文提出的框架用于多模态检索。

#### H5. Decorative rhetoric 修辞堆砌 (TARGET)
**Looks like:** 排比 and 对偶 used for rhythm; "不是……而是……", "不仅仅是……更是……", "与其说……不如说……" where the negated half is rhetorical; three stacked merits; runs of four-character phrases (高效便捷、精准可靠、灵活多变).
**Fix:** Apply the contrast test in A4. State the claim once when the negated half is generic. Keep real contrasts, real enumerations, established terms of the field and quotations. Flag stacked merits the paper does not support (C4).
**Before:** 这不仅仅是一组数字，更说明了数据质量的重要性。
**After:** 这组结果说明了数据质量的重要性。
**Leave alone:** 本文的目标不是提出新的模型，而是解释现有方法为何失效。 The contrast defines the paper's scope.

#### H6. Translationese 欧化与翻译腔 (TARGET)
- **Long modifier chains:** three or more 的 in front of one noun. Split into a verb phrase or two clauses.
- **被 without an agent** in neutral statements. Use the active form or drop 被.
- **进行 + verb** where the plain verb works: "对数据进行分析" → "分析数据". Keep it where it marks a procedure naturally ("进行实验", "数据经清洗后进行统计"), and keep passives in method descriptions.
- **Filler frames:** "作为一个……", "在……方面", "通过……的方式", "基于此".
- **和/与 joining whole clauses** the way English uses "and". Use a comma or a second sentence.
**Before:** 该模块被用于对输入的高分辨率的遥感的图像进行特征的提取。
**After:** 该模块用于提取输入的高分辨率遥感图像的特征。

#### H7. Emphasis and absolutes 装饰性强调与绝对化 (TARGET)
**Looks like:** "极大地", "深刻地", "全面地", "前所未有地", stacked "最"; "显著" with no statistical test.
**Fix:** Delete the intensifier. Use "显著" only for statistical significance; otherwise keep the number the sentence gives or use "明显". Treat "毫无疑问", "必然", "一定" on empirical claims as overclaims and flag them (D2).

#### H8. Stock endings 万能结尾 (HARD: 0)
**Looks like:** "未来可期", "任重而道远", "机遇与挑战并存", "需要多方共同努力", "具有广阔的应用前景", "为后续研究奠定基础" with no follow-up named.
**Fix:** Delete it, or keep only the specific future work the author names.

#### H9. Chinese punctuation 标点 (TARGET)
Chinese punctuation follows GB/T 15834-2011.
- **Dash, colon and semicolon are legitimate.** Replace a 破折号 only when it inserts a decorative aside; keep explanatory ones. Never apply A1 to A3 here.
- **Template lists:** "……主要体现在三个方面：一是……；二是……；三是……" for content that is not three real items. Write plain sentences.
- **Half-width punctuation inside Chinese prose** (`,` `;` `:` `?` `!` `()`) becomes full-width (，；：？！（）). Keep half-width in numbers, formulas, code, English text and reference lists.
- **Quotation marks around a coined term** the author never defines: flag it.
- **Ranges** such as 15～20 km or 15~20 km are standard. Leave them.

#### H10. Sentence length and rhythm 句长与节奏 (TARGET)
AI Chinese sentences tend to cluster at a similar medium length. Treat a sentence over about 100 characters as a cue to reread, not a rule: split it at a natural joint only if it is hard to follow, and join runs of very short sentences that make one thought. The 100-character figure is a practical reading cue, not a research finding. Check C8 after every split.

#### H11. Chinese register 中文语域
- Keep the document's way of referring to itself: theses and proposals usually use 本文 (sometimes 笔者), papers use 本文 or 我们, weekly reports use 我 or 本周. Don't switch between them.
- Keep written register (书面语) in theses, proposals and papers. Weekly reports can be plainer.
- Do not add colloquial phrases, internet slang, modal particles or invented personal anecdotes to "sound human". Many popular 去AI味 guides recommend exactly this. It is wrong for academic documents, and inventing experiences breaks Part 1.

### I. Evasive writing 回避性写作 (all languages: flag, do not fix)

Evasive writing reports activity or importance without the facts a reader needs: what was done, what came out of it, compared with what, and what happens next. It is the most common problem in weekly, midterm and progress reports, and it needs content, not better wording. You cannot supply that content. Never invent it.

| Kind | Chinese | English |
|---|---|---|
| Progress with no content | 取得了一定进展, 做了大量工作, 进行了深入研究, 对……进行了探索 | made good progress, explored, conducted an in-depth study |
| Results with no number | 效果较好, 性能有所提升, 取得了较好的效果 | performed well, showed promising results, improved performance |
| Plans with no deliverable | 下一步将继续深入研究, 进一步完善 | will continue to investigate, further work will focus on |
| Problems with no cause | 遇到了一些问题, 存在一定不足 | some issues were encountered |
| Support with no source | 大量实践证明, 相关研究表明, 研究普遍认为 | studies have shown, it is widely believed |
| Hedge stacks | 在一定程度上, 具有一定的, 可能在某种程度上 | may to some extent, could potentially |

**Where it applies:** in weekly, midterm, lab and progress reports, use the whole table. In papers, theses and proposals, flag only results with no number and support with no source; words like "explored" or "to some extent" are often fine there.

**What to do:**
- Leave the sentence as it is and list it in the report under "Fill these in", with the exact question the author must answer. For example, for "本周对模型进行了深入研究，取得了一定进展": 完成了哪个实验或哪部分代码？结果是多少？与上周计划相比是否完成？
- Treat each phrase as a candidate, not a verdict. Read the whole sentence or bullet first: "模型性能有所提升，准确率由71%升至76%" is already specific. A weekly item can be complete without a number (a resolved blocker, a delivered script). Ask only for the detail that is actually missing.
- Hedge stacks are the one wording fix allowed here, and only for redundant pairs (B5).
- In weekly and midterm reports, put the "Fill these in" list first in the report. For those documents it is the most useful output.

---

## Part 4. Procedure

Follow these steps in order. Do not skip step 0, step 1 or step 6.

0. **Identify the document and its language.** Decide which row of the Part 6 table the document belongs to (from what the user says, or from its headings), and the language of each paragraph (Part 2B). Note both in the report.
1. **Find every file and lock the invariants.** If the paper is a LaTeX project, open the main file and list every file it pulls in through `\input` and `\include`; all of them are the paper. List the numbers, citation markers, math, key terms (from the user, or the most frequent technical nouns) and protected spans. If you can run code, run the checker (Appendix B) on the original and keep the output.
2. **Note the hard-rule hits.** Record where the HARD patterns occur (the checker counts them).
3. **Edit paragraph by paragraph.** For each paragraph:
   a. Read it once for meaning. Write down (to yourself) its main claim and its strength.
   b. Remove the HARD patterns for that paragraph's language.
   c. Fix TARGET patterns where they make a sentence worse.
   c2. List evasive statements (Part 3 I) for the report instead of rewriting them.
   d. Check continuity (C8) around every split or deletion.
   e. Re-read: the main claim must be identical in content and strength, and each number and citation must still belong to the same claim.
   f. Apply the stop rule: when the paragraph reads well, move on.
4. **Read the section through.** Fix choppiness: if three short sentences in a row share a subject, join two of them.
5. **Recheck the hard rules.** Run the checker on the edited version. Every HARD pattern should be gone except allowed uses.
6. **Verify the invariants.** Run the checker on the original and the edited version together. Then read the diff yourself, sentence by sentence, for what no counter can see: which model, metric, condition and citation each number belongs to.
   **Meaning check for result sentences.** For every edited sentence that reports a result or comparison, answer these for the original and the edit: who or what (model, method, group), under which condition, compared with what, which outcome, in which direction, and how certain. Any different answer means the edit changed the claim: undo it or list it in report section 1.
7. **Write the outputs** described in Part 7.

For long documents such as a thesis, work one chapter or section at a time, and keep one list of key terms for the whole document.

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
- **Randomising rhythm or swapping templates:** varying sentence length for its own sake, or replacing one repeated opener with another repeated opener.
- **Changing hedges:** adding them to sound modest, or removing ones the evidence needs.
- **Deleting content** that looks like filler but carries a fact, number or citation.
- **Adding content:** new examples, claims, citations, or transitions that introduce reasoning the authors did not give.
- **Editing protected spans** or quotations.
- **Applying English rules to Chinese**, such as removing every 破折号 or 分号.
- **Translating** a passage into another language.
- **Filling in vague statements** with specifics you made up. Flag them instead (Part 3 I).
- **Shrinking a templated document** below the minimum length its template requires.
- **Touching the LLM usage statement** beyond grammar.

---

## Part 6. Document types and sections

### Document types

If the user doesn't say what the document is, infer it from its headings and state in the report which row you used.

| Document | Rules | Keep fixed | Allowed | Extra focus |
|---|---|---|---|---|
| Journal or conference paper (小论文) | the full guide | the venue's template | | Part 3 A to D (English) or H (Chinese) |
| Thesis (学位论文, 大论文) | the full guide, chapter by chapter | the school template's headings and numbering; 摘要/Abstract structure; required 本章小结; declarations | chapter summaries; 本文 | one key-term list across all chapters (C6); check the whole thesis, not one chapter |
| Research proposal (开题报告) | the full guide | every template heading (研究背景与意义, 国内外研究现状, 研究内容, 研究方案/技术路线, 可行性分析, 进度安排, 预期成果, 参考文献); minimum lengths the template sets; schedule tables | future tense for planned work; 研究意义 may state significance (H3) | the literature review still describes each cited work specifically; report the net length change |
| Midterm report (中期报告) | the full guide | template headings; schedule tables | | evasive writing in 已完成工作 and 研究进展 (Part 3 I) |
| Lab report (实验报告) | lighter edit | procedure steps, data tables, units | numbered steps; passive voice in steps | every result keeps its number and unit; observations stay separate from conclusions |
| Weekly report (周报, 每周汇报) | light edit | the writer's own format (for example 上周计划 / 本周完成 / 遇到的问题 / 下周计划) | bullet lists; short sentences; 我 and 本周 | evasive writing first (Part 3 I); next week's plan should be checkable |
| Anything else academic | the nearest row | | | |

### Sections of a paper or thesis

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

**Produce the edited document and a separate standalone report. Nothing else.**

1. **The edited paper.**
   - Single-file paper: one file in the same format, named `<original name>_humanized.<ext>` (`paper.tex` → `paper_humanized.tex`).
   - Multi-file LaTeX project: one edited copy of the source tree in a folder named `<project name>_humanized/`, with the same file names and structure.
   - If you were given LaTeX, Word or Markdown source, edit the source. A Word file comes back as a Word file with its styles intact. The document contains the document and nothing else.
2. **The report.** A separate, standalone Markdown file named `<original name>_humanizer_report.md`.

**Never append the report to the paper, and never produce a second copy of the paper with the report attached.** Do not paste the edited text into the report; quote only the sentences the report discusses. In your chat reply, name the output files and give a one-line result.

Report contents, most important first:

```
# Humanizer report: <document name>
Document type: <row of the Part 6 table> · Language: <English, Chinese or both>

## 1. Edits that may change meaning
<every edit where the claim, its strength, or which condition a number or citation belongs to
could have shifted, with before and after. Write "none" if none.>

## 2. Fill these in
<Part 3 I items: location, the exact sentence, the question the author must answer.
Write "none" if none.>

## 3. Flags for the authors
<Part 3 E placeholders and Part 3 F items: location, the exact sentence, what is missing,
the options>

## 4. What was verified
Scope: <whole document, or which part was supplied; never claim a whole-document check from an excerpt>
Files examined: <list, including every \input/\include file and every LaTeX root; list any file or part not examined and why>
Checker result: <its RESULT line>, or "checker not run" and how you checked by hand
Net length change: <words (English) or characters (Chinese), before and after>
Key terms: checked / not checked (no list given)
Protected spans: checked / none marked
Not verifiable by counting: which claim each number and citation belongs to; you checked this
by reading the diff

## 5. Hard-rule hits kept on purpose
<only HARD patterns left in place because they are allowed uses: pattern, location, reason>

## 6. Pattern counts
| Pattern | Before | After |
<the checker's marker table>
```

For weekly and midterm reports, put section 2 first.

If any invariant changed, fix it before returning. Never return a paper with a changed number, citation, equation or protected span.

---

## Part 8. Final checklist

- [ ] Document type and language identified; English rules used only on English text, Chinese rules only on Chinese text
- [ ] Every file of the paper was examined (including `\input`/`\include` files)
- [ ] All numbers, signs, units, citations, equations and key terms identical to the original
- [ ] Each number and citation still attached to the same claim and condition
- [ ] Protected spans identical, character for character
- [ ] Same sections, same paragraphs, same order
- [ ] No claim stronger, weaker, broader or narrower than before; nothing added
- [ ] Every HARD pattern removed, or kept as an allowed use and listed
- [ ] Continuity checked around every split and deletion
- [ ] Evasive statements listed under "Fill these in", none filled in with invented specifics
- [ ] Template headings unchanged and required minimum lengths still met
- [ ] Register fits the document type: formal for papers, theses and proposals; plainer is fine for weekly reports; no slang or invented anecdotes anywhere
- [ ] Markup compiles (LaTeX) or renders (Markdown) exactly as before
- [ ] Zero-edit check: for every changed passage, would the original have been more accurate? If yes, restore it
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

The checker is `scripts/humanizer_check.py` in this skill's folder: Python 3, standard library only. It reads LaTeX, Markdown, plain text and Word (`.docx`) files, in English, Chinese or both. If you can run code, use it. If you can't, do the same checks by hand.

```
python scripts/humanizer_check.py paper.tex                          # hard-rule and pattern counts
python scripts/humanizer_check.py before/ after/                     # compare two versions (files or folders)
python scripts/humanizer_check.py before.tex after.tex --terms terms.txt --protect protect.txt
```

- **Pattern counts** are reported separately for English and Chinese paragraphs (sentence length in words for English, characters for Chinese). List items count as paragraphs. It also lists evasive-writing candidates and possible prompt leftovers, each with its location. These are candidates to read, not verdicts.
- **What it reads:** a LaTeX file with every file it pulls in through `\input` and `\include`; in a folder, every LaTeX document root (for example both the main paper and the supplement), or all `.tex`/`.md`/`.txt`/`.docx` files if there is no root; Word body text, native Word equations, footnotes and endnotes. It does **not** read Word headers, footers, comments, text boxes or embedded objects. The output lists every file it examined.
- **Verifies, for the recognized items in the files listed:** numbers with their signs, units (English and Chinese) and scientific notation; citation keys and markers, including Chinese author-year forms; math (`$…$`, `\(…\)`, `\[…\]`, equation environments, native Word equations); protected spans marked in the file. Numbers, citations and math are checked for count and order. Key terms (`--terms`) are checked for count only. `--protect` text is checked only if it occurs in the original; text that doesn't is reported as not found.
- **Does not verify:** whether each number and citation still belongs to the same claim. Read the diff for that.
- **Exit codes:** 0 = recognized items match in count and order. 1 = something was added, lost or changed: fix it. 2 = the same items appear in a different order: check whether a number or citation moved to a different claim. 3 = incomplete: nothing changed in what was checked, but some content could not be checked (a missing `\input` file, or `--protect` text not found).
