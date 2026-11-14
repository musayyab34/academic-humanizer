#!/usr/bin/env python3
"""humanizer_check.py: count AI-tone patterns and check that an edit kept the facts.

Usage:
  python humanizer_check.py PAPER
  python humanizer_check.py BEFORE AFTER [--terms terms.txt] [--protect protect.txt]

PAPER, BEFORE and AFTER can be a file or a folder.
  - A .tex file is followed through \\input{} and \\include{}.
  - A folder is read from its main .tex file (the one with \\documentclass),
    or as all .tex/.md files in it if there is no main file.
--terms    key terms that must appear the same number of times, one per line
--protect  exact text that must survive unchanged, one span per line
           (spans can also be marked in the files: <!-- keep -->...<!-- /keep -->
            in Markdown, or lines "% keep" ... "% /keep" in LaTeX)

Exit codes:
  0  recognized numbers, citations, math, terms and protected spans match in count and order
  1  something was added, lost or changed: fix it
  2  the same items appear in a different order: check that no number or citation
     moved to a different claim

Standard library only. It counts and compares; it cannot tell whether a number still
belongs to the same claim. Read the diff for that.
"""
import os
import re
import sys
import statistics
from collections import Counter

# ---------------------------------------------------------------- word lists
STOCK = [  # HARD: remove (Part 3 B1, B2, B3, E)
    "delve", "delves", "delving", "stark", "starkly", "crucial", "crucially", "pivotal",
    "notably", "moreover", "furthermore", "additionally", "importantly", "interestingly",
    "leverage", "leverages", "leveraging", "underscore", "underscores", "underscoring",
    "showcase", "showcases", "showcasing", "intricate", "intricacies", "tapestry", "realm",
    "landscape", "seamless", "seamlessly", "multifaceted", "paramount", "foster", "fosters",
    "harness", "harnesses", "harnessing", "unlock", "unlocks", "unleash", "bolster",
    "bolsters", "elevate", "meticulous", "meticulously", "commendable", "noteworthy",
    "invaluable", "holistic", "synergy", "groundbreaking", "cutting-edge", "game-changing",
    "transformative", "unprecedented", "nuanced", "garner", "garnered", "ever-evolving",
    "enhance", "enhances", "enhancing", "insights", "valuable", "encompass", "encompasses",
    "encompassing", "endeavor", "endeavour",
    "it is worth noting", "it is important to note", "it should be noted",
    "sheds light", "shed light", "paves the way", "pave the way", "a testament to",
    "in the realm of", "the landscape of", "navigate the complexities",
    "a deeper understanding", "in today's world",
    "with the rapid development of", "has attracted increasing attention",
    "have attracted increasing attention", "widely used in various fields",
    "certainly!", "as an ai language model", "i hope this helps", "here is the revised",
    "as of my last update", "let me know if",
]
REVIEW = [  # fine when precise (B4, B8)
    "significant", "significantly", "robust", "novel", "comprehensive", "extensive",
    "effectively", "various", "remarkable", "remarkably", "dramatically", "substantially",
    "key", "essential", "vital", "serves as", "utilize", "utilization", "potential",
    "critical", "particularly", "exhibit", "exhibits", "align with",
    "plays a role", "plays a key role", "plays a vital role", "plays an important role",
]

CLOSERS = re.compile(
    r"^(overall|in summary|in short|in sum|to summarize|taken together|together, these|"
    r"collectively|in conclusion|these (results|findings|observations) "
    r"(show|suggest|demonstrate|indicate|highlight|confirm))", re.I)
ING_TAIL = re.compile(
    r",\s+(highlighting|demonstrating|indicating|suggesting|showing|underscoring|emphasizing|"
    r"emphasising|revealing|reflecting|confirming|illustrating|showcasing|making it|"
    r"thereby|ensuring)\b", re.I)
RESULT_SUBJ = re.compile(
    r"\b(these|the|our|this|such)\s+(results?|findings?|analys[ie]s|experiments?|observations?|"
    r"data|evidence|figures?|tables?|ablations?|comparisons?)\s+(further\s+)?(highlights?|"
    r"emphasi[sz]es?|underscores?|reveals?|illuminates?|showcases?)\b", re.I)

# ---------------------------------------------------------------- loading
INPUT_RE = re.compile(r"\\(?:input|include)\s*\{([^}]+)\}")


def _read(path):
    with open(path, encoding="utf-8", errors="replace") as f:
        return f.read()


def _resolve(name, root):
    for cand in (name, name + ".tex"):
        p = os.path.normpath(os.path.join(root, cand))
        if os.path.isfile(p):
            return p
    return None


def _expand_tex(path, root, seen, files, missing):
    """Inline \\input/\\include files, depth first, paths relative to the main file's folder."""
    if path in seen:
        return ""
    seen.add(path)
    files.append(path)
    text = _read(path)
    out, last = [], 0
    for m in INPUT_RE.finditer(text):
        line_start = text.rfind("\n", 0, m.start()) + 1
        if "%" in re.sub(r"\\%", "", text[line_start:m.start()]):   # commented out
            continue
        out.append(text[last:m.end()])
        child = _resolve(m.group(1).strip(), root)
        if child:
            out.append("\n" + _expand_tex(child, root, seen, files, missing) + "\n")
        else:
            missing.append(m.group(1).strip())
        last = m.end()
    out.append(text[last:])
    return "".join(out)


def load(path):
    """Return (text, files_examined, missing_inputs) for a file or folder."""
    files, missing = [], []
    if os.path.isdir(path):
        texs = sorted(os.path.join(dp, f) for dp, _, fs in os.walk(path)
                      for f in fs if f.endswith(".tex"))
        mains = [p for p in texs if re.search(r"^[^%\n]*\\documentclass", _read(p), re.M)]
        if mains:
            main = mains[0]
            return _expand_tex(main, os.path.dirname(main), set(), files, missing), files, missing
        docs = sorted(os.path.join(dp, f) for dp, _, fs in os.walk(path)
                      for f in fs if f.endswith((".tex", ".md")))
        return "\n\n".join(_read(p) for p in docs), docs, missing
    if path.endswith(".tex"):
        return _expand_tex(os.path.abspath(path), os.path.dirname(os.path.abspath(path)),
                           set(), files, missing), files, missing
    return _read(path), [path], missing


# ---------------------------------------------------------------- text helpers
KEEP_RE = re.compile(r"<!--\s*keep\s*-->(.*?)<!--\s*/keep\s*-->|^[ \t]*%[ \t]*keep[ \t]*\n(.*?)^[ \t]*%[ \t]*/keep",
                     re.S | re.M)


def keep_spans(t):
    return [(m.group(1) if m.group(1) is not None else m.group(2)) for m in KEEP_RE.finditer(t)]


def strip_comments(t):
    t = re.sub(r"<!--.*?-->", " ", t, flags=re.S)
    return re.sub(r"(?<![\\\d])%.*", "", t)          # LaTeX comments; keeps \% and "82.4%"


MATH_RE = re.compile(
    r"\$\$.*?\$\$|\\\[.*?\\\]|\\\(.*?\\\)|"
    r"\\begin\{(equation|align|gather|multline|eqnarray|math|displaymath)\*?\}.*?\\end\{\1\*?\}|"
    r"(?<![\\$])\$[^$\n]+?\$", re.S)


STRUCT_LINE = re.compile(
    r"^\s*\\(documentclass|usepackage|begin\{document\}|end\{document\}|input|include|"
    r"maketitle|bibliography|bibliographystyle|label|newcommand|renewcommand|title|author|date|"
    r"(sub)*section\*?|paragraph\*?|chapter\*?)\b.*$", re.M)


def prose(t):
    if "\\begin{document}" in t:
        t = t.split("\\begin{document}", 1)[1]
    t = STRUCT_LINE.sub("\n", t)
    t = re.sub(r"```.*?```", " ", t, flags=re.S)
    t = MATH_RE.sub(" MATH ", t)
    t = re.sub(r"\\(cite[pt]?\*?|ref|eqref|label|autoref|cref|Cref|input|include)(\[[^\]]*\])?\{[^}]*\}",
               " REF ", t)
    return "\n".join(l for l in t.split("\n") if not l.lstrip().startswith("|"))


def paragraphs(t):
    out = []
    for p in re.split(r"\n\s*\n", t):
        s = p.strip()
        if not s or s.startswith(("#", "\\section", "\\subsection", "\\begin", "\\end",
                                  "-", "*", "|", "\\item", "\\documentclass", "\\usepackage")):
            continue
        if re.match(r"^\d+\.\s", s):
            continue
        out.append(re.sub(r"\s+", " ", s))
    return out


def sentences(p):
    p = re.sub(r"\b(e\.g|i\.e|et al|Fig|Figs|Eq|Eqs|Sec|Tab|vs|cf|approx)\.", r"\1<DOT>", p)
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z\\])", p)
    return [s.replace("<DOT>", ".") for s in parts if s.strip()]


def count_phrase(text, phrase):
    return len(re.findall(r"(?<![\w-])" + re.escape(phrase) + r"(?![\w-])", text, re.I))


# ---------------------------------------------------------------- markers
def markers(raw):
    pr = prose(strip_comments(raw))
    paras = paragraphs(pr)
    sents = [s for p in paras for s in sentences(p)]
    lens = [len(s.split()) for s in sents]
    body = " ".join(paras)
    stock = {w: count_phrase(body, w) for w in STOCK}
    review = {w: count_phrase(body, w) for w in REVIEW}
    closer = sum(1 for p in paras if len(sentences(p)) > 1 and CLOSERS.match(sentences(p)[-1]))
    hard = {
        "em/en dashes as punctuation": len(re.findall(r"—|(?<!-)---(?!-)|\s–\s|\s--\s|\s-\s", body)),
        "colon reveals (check each)": len(re.findall(r"[a-z)\]]: [a-z]", body)),
        "'not only ... but'": count_phrase(body, "not only"),
        "rhetorical questions": sum(1 for s in sents if s.rstrip().endswith("?")),
        "stock words/phrases": sum(stock.values()),
        "result-as-subject verbs": len(RESULT_SUBJ.findall(body)),
    }
    target = {
        "semicolons": body.count(";"),
        "therefore / thus / hence": sum(count_phrase(body, w) for w in ("therefore", "thus", "hence")),
        "'rather than' / ', not'": count_phrase(body, "rather than") + len(re.findall(r",\s+not\s+(?!only\b)", body, re.I)),
        "', -ing' tails": len(ING_TAIL.findall(body)),
        "paragraph-closing summaries": closer,
        "sentences > 35 words": sum(1 for n in lens if n > 35),
    }
    info = {
        "sentences": len(lens),
        "mean words/sentence": round(statistics.mean(lens), 1) if lens else 0,
        "spread (stdev)": round(statistics.pstdev(lens), 1) if lens else 0,
    }
    return hard, target, info, {k: v for k, v in stock.items() if v}, {k: v for k, v in review.items() if v}


# ---------------------------------------------------------------- invariants
UNITS = (r"\\%|%|×|ms|μs|us|ns|s|sec|min|h|hrs?|GB|MB|KB|TB|GiB|MiB|K|M|B|k|px|dB|Hz|kHz|MHz|GHz|"
         r"G?FLOPs|T?FLOPs|pp|x")
NUM_RE = re.compile(r"(?<![\w.])([+\-−±]?)(\d+(?:[.,]\d+)*)(?:\s?(" + UNITS + r")(?![A-Za-z]))?")
CITE_CMD = re.compile(r"\\(?:cite[a-z]*\*?)(?:\[[^\]]*\])*\{([^}]*)\}")
CITE_NUM = re.compile(r"\[(\d+(?:\s*[,–-]\s*\d+)*)\]")
CITE_PANDOC = re.compile(r"\[(@[^\]]+)\]")
CITE_AUTHOR = re.compile(r"[A-Z][A-Za-z'-]+ (?:et al\.|and [A-Z][A-Za-z'-]+),? \(?\d{4}[a-z]?")


def _ctx(text, start, end, width=35):
    s = re.sub(r"\s+", " ", text[max(0, start - width):min(len(text), end + width)])
    return "..." + s.strip() + "..."


def invariants(raw):
    """Ordered lists of (token, context) for numbers, citations and math."""
    t = strip_comments(raw)
    nums = []
    for m in NUM_RE.finditer(t):
        sign = m.group(1).replace("−", "-")
        unit = (m.group(3) or "").replace("\\%", "%")
        nums.append((sign + m.group(2) + unit, _ctx(t, m.start(), m.end())))
    cites = []
    for m in sorted(list(CITE_CMD.finditer(t)) + list(CITE_NUM.finditer(t)) +
                    list(CITE_PANDOC.finditer(t)) + list(CITE_AUTHOR.finditer(t)), key=lambda m: m.start()):
        if m.re is CITE_AUTHOR:
            keys = [m.group(0)]
        else:
            keys = [k.strip() for k in re.split(r"[,;]", m.group(1)) if k.strip()]
        for k in keys:
            cites.append((k, _ctx(t, m.start(), m.end())))
    maths = [(re.sub(r"\s+", " ", m.group(0)).strip(), "") for m in MATH_RE.finditer(t)]
    return nums, cites, maths


def compare(name, a, b):
    """0 = same, 1 = changed, 2 = same items in a different order."""
    ca, cb = Counter(x for x, _ in a), Counter(x for x, _ in b)
    if ca != cb:
        print(f"  {name:<16} CHANGED")
        lost, added = ca - cb, cb - ca
        if lost:
            print(f"    missing after edit: {dict(lost)}")
            for tok in list(lost)[:5]:
                ctx = next((c for x, c in a if x == tok), "")
                if ctx:
                    print(f"      was: {ctx}")
        if added:
            print(f"    new after edit:     {dict(added)}")
            for tok in list(added)[:5]:
                ctx = next((c for x, c in b if x == tok), "")
                if ctx:
                    print(f"      now: {ctx}")
        return 1
    seq_a, seq_b = [x for x, _ in a], [x for x, _ in b]
    if seq_a != seq_b:
        i = next(i for i, (x, y) in enumerate(zip(seq_a, seq_b)) if x != y)
        print(f"  {name:<16} ORDER CHANGED (same items, {len(seq_a)} total)")
        print(f"    first difference, before: {a[i][0]!r} {a[i][1]}")
        print(f"                      after:  {b[i][0]!r} {b[i][1]}")
        return 2
    print(f"  {name:<16} OK ({len(seq_a)})")
    return 0


# ---------------------------------------------------------------- main
def main(argv):
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return 0
    opts = {}
    for flag in ("--terms", "--protect"):
        if flag in argv:
            i = argv.index(flag)
            opts[flag] = [l.rstrip("\n") for l in open(argv[i + 1], encoding="utf-8") if l.strip()]
            argv = argv[:i] + argv[i + 2:]
    loaded = [load(p) for p in argv[:2]]
    texts = [x[0] for x in loaded]

    for label, (_, files, missing) in zip(("before", "after") if len(loaded) == 2 else ("paper",), loaded):
        print(f"Files examined ({label}): {len(files)}")
        for f in files:
            print(f"  {f}")
        for m in missing:
            print(f"  NOT FOUND: \\input{{{m}}}")

    results = [markers(t) for t in texts]
    two = len(texts) == 2
    head = (" " * (32 - 0) + "before   after") if two else ""
    for title, idx in (("HARD rules (target 0)", 0), ("TARGET patterns", 1), ("Info", 2)):
        print(f"\n{title}")
        if two:
            print(f"  {'':<30} {'before':>5}   {'after':>5}")
        for key in results[0][idx]:
            vals = [r[idx][key] for r in results]
            print(f"  {key:<30} " + "   ".join(f"{v:>6}" for v in vals))
    print("\nStock words still present:", results[-1][3] or "none")
    print("Review for precise use:   ", results[-1][4] or "none")

    if not two:
        return 0

    print("\nInvariants (before vs after)")
    a, b = invariants(texts[0]), invariants(texts[1])
    codes = [compare("numbers", a[0], b[0]), compare("citations", a[1], b[1]), compare("math", a[2], b[2])]

    terms = opts.get("--terms")
    if terms:
        changed = {t: (count_phrase(texts[0], t), count_phrase(texts[1], t)) for t in terms
                   if count_phrase(texts[0], t) != count_phrase(texts[1], t)}
        print(f"  {'key terms':<16} {'OK (' + str(len(terms)) + ')' if not changed else 'CHANGED'}")
        for t, (x, y) in changed.items():
            print(f"    '{t}': {x} -> {y}")
        codes.append(1 if changed else 0)
    else:
        print(f"  {'key terms':<16} NOT CHECKED (no --terms list given)")

    spans_a, spans_b = keep_spans(texts[0]), keep_spans(texts[1])
    extra = [s for s in opts.get("--protect", []) if s in texts[0]]
    lost = [s for s in extra if texts[1].count(s) < texts[0].count(s)]
    if spans_a or extra:
        bad = spans_a != spans_b or bool(lost)
        print(f"  {'protected spans':<16} {'CHANGED' if bad else 'OK (' + str(len(spans_a) + len(extra)) + ')'}")
        for i, (x, y) in enumerate(zip(spans_a, spans_b)):
            if x != y:
                print(f"    marked span {i + 1} differs:\n      was: {x.strip()[:200]!r}\n      now: {y.strip()[:200]!r}")
        if len(spans_a) != len(spans_b):
            print(f"    marked spans: {len(spans_a)} before, {len(spans_b)} after")
        for s in lost:
            print(f"    missing: {s[:200]!r}")
        codes.append(1 if bad else 0)
    else:
        print(f"  {'protected spans':<16} NONE MARKED")

    n = (len(a[0]), len(a[1]), len(a[2]))
    if 1 in codes:
        print("\nRESULT: CHANGED. Something was added, lost or altered. Fix it before delivering.")
        return 1
    if 2 in codes:
        print("\nRESULT: REVIEW. The same items are present but in a different order. "
              "Check that no number or citation moved to a different claim.")
        return 2
    print(f"\nRESULT: recognized numbers ({n[0]}), citations ({n[1]}) and math ({n[2]}) match in count "
          f"and order across {len(loaded[0][1])} file(s). Not verified: whether each number and "
          f"citation still belongs to the same claim. Read the diff for that.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
