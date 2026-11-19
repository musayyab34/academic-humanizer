#!/usr/bin/env python3
"""humanizer_check.py: count AI-tone patterns and check that an edit kept the facts.

Usage:
  python humanizer_check.py DOCUMENT
  python humanizer_check.py BEFORE AFTER [--terms terms.txt] [--protect protect.txt]

DOCUMENT, BEFORE and AFTER can be a file (.tex, .md, .txt or .docx) or a folder.
  - A .tex file is followed through \\input{} and \\include{}.
  - A folder is read from its main .tex file (the one with \\documentclass),
    or as all .tex/.md/.txt/.docx files in it if there is no main file.
  - English and Chinese paragraphs are counted separately, each with its own patterns.
--terms    key terms that must appear the same number of times, one per line
--protect  exact text that must survive unchanged, one span per line
           (spans can also be marked in the files: <!-- keep -->...<!-- /keep -->
            in Markdown, or lines "% keep" ... "% /keep" in LaTeX)

Exit codes:
  0  recognized numbers, citations, math, terms and protected spans match in count and order
  1  something was added, lost or changed: fix it
  2  the same items appear in a different order: check that no number or citation
     moved to a different claim
  3  incomplete: some content could not be checked (a missing \\input file, or --protect
     text not found in the original). Nothing changed in what was checked.

What is read: LaTeX (all document roots in a folder, with their \\input/\\include files),
Markdown, plain text, and Word body text, native Word equations, footnotes and endnotes.
Not read: Word headers, footers, comments, text boxes and embedded objects.

Standard library only. It counts and compares; it cannot tell whether a number still
belongs to the same claim. Read the diff for that.
"""
import html
import os
import re
import statistics
import sys
import zipfile
from collections import Counter

# ================================================================ word lists
STOCK_EN = [  # HARD: remove (Part 3 B1, B2, B3, E)
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
REVIEW_EN = [  # fine when precise (B4, B8)
    "significant", "significantly", "robust", "novel", "comprehensive", "extensive",
    "effectively", "various", "remarkable", "remarkably", "dramatically", "substantially",
    "key", "essential", "vital", "serves as", "utilize", "utilization", "potential",
    "critical", "particularly", "exhibit", "exhibits", "align with",
    "plays a role", "plays a key role", "plays a vital role", "plays an important role",
]
STOCK_ZH = [  # HARD: remove (Part 3 H1, H2 first list, H3, H4, H8, E)
    "随着", "受到越来越多的关注", "受到了越来越多的关注", "受到广泛关注", "日益受到",
    "在当今社会", "众所周知",
    "值得注意的是", "值得一提的是", "需要指出的是", "不难看出", "显而易见", "毋庸置疑",
    "从多个维度来看", "从更深层次来看",
    "具有重要意义", "具有重要的意义", "发挥着关键作用", "发挥着重要作用", "起到了重要作用",
    "至关重要", "不可或缺", "奠定了坚实基础", "奠定坚实基础", "提供了有力支撑", "提供有力支撑",
    "开辟了新路径", "彰显了",
    "赋能", "助力", "深度融合", "全方位", "多维度", "全链条", "抓手", "底层逻辑", "一站式", "新赛道",
    "未来可期", "任重而道远", "机遇与挑战并存", "需要多方共同努力", "具有广阔的应用前景",
    "以下是修改后的", "希望对您有帮助", "根据您的要求", "作为AI语言模型", "如需进一步修改",
]
REVIEW_ZH = [  # fine when precise or when they mark a real sequence (H2, H7)
    "此外", "与此同时", "综上所述", "由此可见", "总而言之", "具体而言",
    "显著", "极大地", "深刻地", "全面地", "前所未有", "毫无疑问", "必然", "闭环", "重塑", "生态",
]
PROMPT_LEFTOVERS = [  # Part 3 E: possible prompt text left in the document (check each)
    "请帮我", "帮我润色", "请润色", "请改写", "请修改以下", "以下内容", "字数要求", "要求：",
    "rewrite the following", "please rewrite", "please revise", "make it sound", "word count:",
]
EVASIVE = [  # Part 3 I: flag for the author, never fill in
    "取得了一定进展", "取得一定进展", "取得了一定的进展", "做了大量工作", "进行了深入研究",
    "进行深入研究", "进行了探索", "效果较好", "效果良好", "取得了较好的效果", "性能有所提升",
    "下一步将继续", "继续深入研究", "进一步完善", "遇到了一些问题", "存在一定不足",
    "大量实践证明", "相关研究表明", "研究普遍认为", "在一定程度上", "具有一定的",
    "made good progress", "made some progress", "conducted an in-depth study", "explored",
    "performed well", "promising results", "improved performance", "will continue to investigate",
    "further work will focus on", "some issues were encountered", "studies have shown",
    "it is widely believed", "to some extent", "could potentially",
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

CJK = r"\u3400-\u4dbf\u4e00-\u9fff"
CJK_RE = re.compile(f"[{CJK}]")

# ================================================================ loading
INPUT_RE = re.compile(r"\\(?:input|include)\s*\{([^}]+)\}")
TEXT_EXT = (".tex", ".md", ".txt", ".docx")


DOCX_PARTS = ("word/document.xml", "word/footnotes.xml", "word/endnotes.xml")


OMML_STRUCT = {"sSup", "sSub", "sSubSup", "sPre", "f", "num", "den", "rad", "deg", "e", "sup", "sub",
               "nary", "d", "m", "mr", "func", "fName", "acc", "bar", "limLow", "limUpp", "lim",
               "eqArr", "groupChr", "box", "borderBox"}
OMML_PROPS = re.compile(r"<(m|w):(\w*Pr)\b[^>]*/>|<(m|w):(\w*Pr)\b.*?</\3:\4>", re.S)


def _omath_to_text(m):
    """Native Word equation -> \\( ... \\) keeping its structure, so x² and x₂ differ."""
    xml = OMML_PROPS.sub("", m.group(0))
    out = []
    for close, name, selfclose, text in re.findall(r"<(/?)m:(\w+)[^>]*?(/?)>|([^<]+)", xml):
        if text:
            out.append(text)
        elif name in OMML_STRUCT and not selfclose:
            out.append("}" if close else name + "{")
    inner = html.escape("".join(out).strip(), quote=False)
    return "<w:t>\\(" + inner + "\\)</w:t>"


def read_docx(path):
    """Text of a .docx file: body, native equations, footnotes and endnotes.
    Paragraphs are separated by blank lines; heading-styled paragraphs get a '# ' prefix."""
    paras = []
    with zipfile.ZipFile(path) as z:
        names = set(z.namelist())
        for part in DOCX_PARTS:
            if part not in names:
                continue
            xml = z.read(part).decode("utf-8", errors="replace")
            xml = re.sub(r"<m:oMath(?:\s[^>]*)?>.*?</m:oMath>", _omath_to_text, xml, flags=re.S)
            for p in re.findall(r"<w:p[ >].*?</w:p>", xml, re.S):
                style = re.search(r'<w:pStyle w:val="([^"]*)"', p)
                p = re.sub(r"<w:tab/>", "\t", p)
                p = re.sub(r"<w:br[^>]*/>", "\n", p)
                text = "".join(re.findall(r"<w:t(?:\s[^>]*)?>(.*?)</w:t>", p, re.S))
                text = html.unescape(text).strip()
                if not text:
                    continue
                if style and re.search(r"heading|title|标题|^[1-9]$", style.group(1), re.I):
                    text = "# " + text
                paras.append(text)
    return "\n\n".join(paras)


def _read(path):
    if path.lower().endswith(".docx"):
        return read_docx(path)
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
    """Return (text, files_examined, missing_inputs, is_latex) for a file or folder."""
    files, missing = [], []
    if os.path.isdir(path):
        texs = sorted(os.path.join(dp, f) for dp, _, fs in os.walk(path)
                      for f in fs if f.endswith(".tex"))
        mains = [p for p in texs if re.search(r"^[^%\n]*\\documentclass", _read(p), re.M)]
        if mains:
            seen, parts = set(), []
            for main in mains:          # every document root (e.g. main paper and supplement)
                parts.append(_expand_tex(main, os.path.dirname(main), seen, files, missing))
            return "\n\n".join(parts), files, missing, True
        docs = sorted(os.path.join(dp, f) for dp, _, fs in os.walk(path)
                      for f in fs if f.lower().endswith(TEXT_EXT))
        return "\n\n".join(_read(p) for p in docs), docs, missing, any(d.endswith(".tex") for d in docs)
    if path.endswith(".tex"):
        ap = os.path.abspath(path)
        return _expand_tex(ap, os.path.dirname(ap), set(), files, missing), files, missing, True
    return _read(path), [path], missing, False


# ================================================================ text helpers
KEEP_RE = re.compile(r"<!--\s*keep\s*-->(.*?)<!--\s*/keep\s*-->|^[ \t]*%[ \t]*keep[ \t]*\n(.*?)^[ \t]*%[ \t]*/keep",
                     re.S | re.M)


def keep_spans(t):
    return [(m.group(1) if m.group(1) is not None else m.group(2)) for m in KEEP_RE.finditer(t)]


def strip_comments(t, is_latex):
    t = re.sub(r"<!--.*?-->", " ", t, flags=re.S)
    if is_latex:
        t = re.sub(r"(?<![\\\d])%.*", "", t)      # LaTeX comments; keeps \% and "82.4%"
    return t


MATH_RE = re.compile(
    r"\$\$.*?\$\$|\\\[.*?\\\]|\\\(.*?\\\)|"
    r"\\begin\{(equation|align|gather|multline|eqnarray|math|displaymath)\*?\}.*?\\end\{\1\*?\}|"
    r"(?<![\\$])\$[^$\n]+?\$", re.S)

STRUCT_LINE = re.compile(
    r"^\s*\\(documentclass|usepackage|begin\{document\}|end\{document\}|input|include|"
    r"maketitle|bibliography|bibliographystyle|label|newcommand|renewcommand|title|author|date|"
    r"includegraphics|centering|vspace|hspace|hline|toprule|midrule|bottomrule|resizebox|setlength|"
    r"(sub)*section\*?|paragraph\*?|chapter\*?)\b.*$", re.M)


CODE_ENVS = r"(?:algorithm|algorithmic|algorithm2e|lstlisting|verbatim|minted|tabular|tabularx|tikzpicture|comment)\*?"
MATH_ENVS = r"(?:equation|align|gather|multline|eqnarray|math|displaymath)\*?"


def prose(t):
    if "\\begin{document}" in t:
        t = t.split("\\begin{document}", 1)[1]
    # pseudocode, code and tables are not prose: drop them
    t = re.sub(r"\\begin\{(" + CODE_ENVS + r")\}.*?\\end\{\1\}", "\n\n", t, flags=re.S)
    # other environments (abstract, itemize, figure...): keep their text, drop the delimiters
    t = re.sub(r"\\(?:begin|end)\{(?!" + MATH_ENVS + r"\})[^}]*\}(?:\[[^\]]*\])?", "\n\n", t)
    t = re.sub(r"\\caption\*?(?:\[[^\]]*\])?\{", "", t)
    t = STRUCT_LINE.sub("\n", t)
    t = re.sub(r"```.*?```", " ", t, flags=re.S)
    t = MATH_RE.sub("MATH", t)          # no padding, so $a$--$b$ stays a range
    t = re.sub(r"\\(cite[pt]?\*?|ref|eqref|label|autoref|cref|Cref|input|include)(\[[^\]]*\])?\{[^}]*\}",
               " REF ", t)
    return "\n".join(l for l in t.split("\n") if not l.lstrip().startswith("|"))


QUOTES = re.compile(r"“[^”]*”|「[^」]*」|『[^』]*』|``.*?''|\"[^\"]*\"")


def language(p):
    """'zh' if Chinese characters outnumber Latin words in the paragraph's own prose, else 'en'
    (Part 2B). Quotations are left out of the count unless nothing else is left."""
    q = QUOTES.sub(" ", p)
    if CJK_RE.search(q) or re.search(r"[A-Za-z]", q):
        p = q
    cjk = len(CJK_RE.findall(p))
    latin = len(re.findall(r"[A-Za-z]+", p))
    return "zh" if cjk > latin else "en"


LIST_MARK = re.compile(r"^\s*(?:[-*+•]|\\item|\d+[.)、]|[（(]\d+[)）]|[一二三四五六七八九十]+、)\s*")


def paragraphs(t):
    """List of (language, text, is_body). List items become their own paragraphs.
    Short unpunctuated lines are kept for phrase counts but left out of sentence statistics."""
    out = []
    for block in re.split(r"\n\s*\n", t):
        lines = [l for l in block.split("\n") if l.strip()]
        if not lines:
            continue
        if any(LIST_MARK.match(l) for l in lines):
            items = [LIST_MARK.sub("", l).strip() for l in lines]
        else:
            items = [" ".join(l.strip() for l in lines)]
        for s in items:
            if not s or s.startswith(("#", "\\section", "\\subsection", "\\begin", "\\end",
                                      "|", "\\documentclass", "\\usepackage")):
                continue
            s = re.sub(r"\s+", " ", s)
            lang = language(s)
            is_body = bool(re.search(r"[。！？.!?]$|[。！？]", s)) or len(s) >= 40
            out.append((lang, s, is_body))
    return out


def sentences_en(p):
    p = re.sub(r"\b(e\.g|i\.e|et al|Fig|Figs|Eq|Eqs|Sec|Tab|vs|cf|approx)\.", r"\1<DOT>", p)
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z\\])", p)
    return [s.replace("<DOT>", ".") for s in parts if s.strip()]


def sentences_zh(p):
    return [s for s in re.split(r"(?<=[。！？])", p) if s.strip()]


def count_phrase(text, phrase):
    if CJK_RE.search(phrase):
        return text.count(phrase)
    return len(re.findall(r"(?<![\w-])" + re.escape(phrase) + r"(?![\w-])", text, re.I))


# ================================================================ markers
def _stats(lens):
    return {
        "sentences": len(lens),
        "mean length": round(statistics.mean(lens), 1) if lens else 0,
        "spread (stdev)": round(statistics.pstdev(lens), 1) if lens else 0,
    }


def markers_en(paras, all_paras):
    sents = [s for p in paras for s in sentences_en(p)]
    lens = [len(s.split()) for s in sents]
    body = " ".join(all_paras)
    stock = {w: count_phrase(body, w) for w in STOCK_EN}
    review = {w: count_phrase(body, w) for w in REVIEW_EN}
    closer = sum(1 for p in paras if len(sentences_en(p)) > 1 and CLOSERS.match(sentences_en(p)[-1]))
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
    info = _stats(lens)
    info["mean length"] = f"{info['mean length']} words"
    return hard, target, info, {k: v for k, v in stock.items() if v}, {k: v for k, v in review.items() if v}


def markers_zh(paras, all_paras):
    sents = [s for p in paras for s in sentences_zh(p)]
    lens = [len(re.sub(r"\s", "", s)) for s in sents]
    body = "".join(all_paras)
    stock = {w: count_phrase(body, w) for w in STOCK_ZH}
    stock["随着"] = len(re.findall(r"随着[^。，]{1,20}的(快速|不断|飞速|迅速|蓬勃)?发展", body))
    review = {w: count_phrase(body, w) for w in REVIEW_ZH}
    hard = {
        "套话/空泛词 stock phrases": sum(stock.values()),
    }
    target = {
        "破折号 dashes (check each)": body.count("——"),
        "一是……二是 template lists": len(re.findall(r"一是[^。]{1,80}二是", body)),
        "首先……其次 sequences": len(re.findall(r"首先[^。]{0,200}?其次", body)),
        "不是……而是 contrasts": len(re.findall(r"不是[^。！？]{1,30}而是", body)),
        "对……进行 frames": len(re.findall(r"对[^。，；]{1,20}进行", body)),
        "half-width punctuation": len(re.findall(f"[{CJK}][,;:?!]|[,;:?!][{CJK}]", body)),
        "sentences > 100 chars (reread)": sum(1 for n in lens if n > 100),
    }
    info = _stats(lens)
    info["mean length"] = f"{info['mean length']} chars"
    return hard, target, info, {k: v for k, v in stock.items() if v}, {k: v for k, v in review.items() if v}


def _candidates(paras, phrases):
    """One candidate per sentence containing any phrase: (location, phrases, has_number, snippet)."""
    found = []
    for i, (lang, p, _) in enumerate(paras, 1):
        for sent in (sentences_zh(p) if lang == "zh" else sentences_en(p)):
            hits = [w for w in phrases if count_phrase(sent, w)]
            hits = [w for w in hits if not any(w != o and w in o for o in hits)]   # drop overlaps
            if hits:
                found.append((f"paragraph {i}", hits, bool(re.search(r"\d", sent)), sent.strip()[:90]))
    return found


def markers(raw, is_latex):
    paras = paragraphs(prose(strip_comments(raw, is_latex)))
    en = [p for lang, p, body in paras if lang == "en" and body]
    zh = [p for lang, p, body in paras if lang == "zh" and body]
    en_all = [p for lang, p, _ in paras if lang == "en"]
    zh_all = [p for lang, p, _ in paras if lang == "zh"]
    return {
        "en": markers_en(en, en_all) if en_all else None, "n_en": len(en_all),
        "zh": markers_zh(zh, zh_all) if zh_all else None, "n_zh": len(zh_all),
        "evasive": _candidates(paras, EVASIVE),
        "prompts": _candidates(paras, PROMPT_LEFTOVERS),
        "length": {"words": sum(len(p.split()) for p in en_all),
                   "chars": sum(len(CJK_RE.findall(p)) for p in zh_all)},
    }


# ================================================================ invariants
UNITS = (r"\\%|%|％|×|ms|μs|us|ns|s|sec|min|h|hrs?|GB|MB|KB|TB|GiB|MiB|K|M|B|k|px|dB|Hz|kHz|MHz|GHz|"
         r"G?FLOPs|T?FLOPs|pp|x|nm|μm|um|mm|cm|km|m|mg|kg|g|mL|ml|L|°C|°|W|kW|V|mA|A|"
         r"个百分点|百分点|毫秒|微秒|纳秒|秒|分钟|小时|天|周|月|年|毫米|厘米|千米|公里|米|毫克|千克|克|"
         r"毫升|升|倍|元|万元|亿元|万|亿|个|次|篇|层|轮|张")
NUM_RE = re.compile(r"(?<![A-Za-z0-9_.])([+\-−±]?)(\d+(?:[.,]\d+)*(?:[eE][+\-−]?\d+)?)"
                    r"(?:\s?(" + UNITS + r")(?![A-Za-z]))?")
CITE_CMD = re.compile(r"\\(?:cite[a-z]*\*?)(?:\[[^\]]*\])*\{([^}]*)\}")
CITE_NUM = re.compile(r"\[(\d+(?:\s*[,，–-]\s*\d+)*)\]")
CITE_PANDOC = re.compile(r"\[(@[^\]]+)\]")
CITE_AUTHOR = re.compile(r"[A-Z][A-Za-z'-]+ (?:et al\.|and [A-Z][A-Za-z'-]+),? \(?\d{4}[a-z]?")
CITE_ZH = re.compile(f"[{CJK}]{{2,4}}(?:等)?(?:[，,]\\s?\\d{{4}}[a-z]?|\\s?[（(]\\d{{4}}[a-z]?[）)])")


def _ctx(text, start, end, width=35):
    s = re.sub(r"\s+", " ", text[max(0, start - width):min(len(text), end + width)])
    return "..." + s.strip() + "..."


def invariants(raw, is_latex):
    """Ordered lists of (token, context) for numbers, citations and math."""
    t = strip_comments(raw, is_latex)
    nums = []
    for m in NUM_RE.finditer(t):
        sign = m.group(1).replace("−", "-")
        num = m.group(2).replace("−", "-")
        unit = (m.group(3) or "").replace("\\%", "%").replace("％", "%")
        nums.append((sign + num + unit, _ctx(t, m.start(), m.end())))
    cites = []
    found = sorted(list(CITE_CMD.finditer(t)) + list(CITE_NUM.finditer(t)) + list(CITE_PANDOC.finditer(t)) +
                   list(CITE_AUTHOR.finditer(t)) + list(CITE_ZH.finditer(t)), key=lambda m: m.start())
    for m in found:
        if m.re is CITE_AUTHOR or m.re is CITE_ZH:
            keys = [m.group(0)]
        else:
            keys = [k.strip() for k in re.split(r"[,;，]", m.group(1)) if k.strip()]
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


# ================================================================ output
def print_block(title, blocks, two):
    print(f"\n{title}")
    for heading, idx in (("HARD rules (target 0)", 0), ("TARGET patterns", 1), ("Info", 2)):
        ref = next(b for b in blocks if b)
        print(f"  {heading}")
        if two:
            print(f"    {'':<32} {'before':>8} {'after':>8}")
        for key in ref[idx]:
            vals = [(b[idx][key] if b else "-") for b in blocks]
            print(f"    {key:<32} " + " ".join(f"{str(v):>8}" for v in vals))
    print("  Stock phrases still present:", blocks[-1][3] if blocks[-1] else "-")
    print("  Review for precise use:     ", blocks[-1][4] if blocks[-1] else "-")


def print_candidates(title, cands):
    print(f"\n{title}: {len(cands) or 'none'}")
    for loc, hits, has_num, snippet in cands[:40]:
        note = "  (has a number: may already be specific)" if has_num else ""
        print(f"  {loc}: {', '.join(hits)}{note}\n      {snippet}")
    if len(cands) > 40:
        print(f"  ... and {len(cands) - 40} more")


def main(argv):
    for stream in (sys.stdout, sys.stderr):            # Chinese output on Windows consoles
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass
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
    is_latex = any(x[3] for x in loaded)
    two = len(loaded) == 2

    for label, (_, files, missing, _) in zip(("before", "after") if two else ("document",), loaded):
        print(f"Files examined ({label}): {len(files)}")
        for f in files:
            print(f"  {f}")
        for m in missing:
            print(f"  NOT FOUND: \\input{{{m}}}")

    results = [markers(t, is_latex) for t in texts]
    counts = " / ".join(f"{r['n_en']} English, {r['n_zh']} Chinese" for r in results)
    print(f"\nParagraphs: {counts}")
    if any(r["en"] for r in results):
        print_block("ENGLISH TEXT", [r["en"] for r in results], two)
    if any(r["zh"] for r in results):
        print_block("CHINESE TEXT 中文", [r["zh"] for r in results], two)
    print_candidates("Evasive-writing candidates (Part 3 I, check each)", results[-1]["evasive"])
    print_candidates("Possible prompt leftovers (Part 3 E, check each)", results[-1]["prompts"])
    lens = " -> ".join(f"{r['length']['words']} words, {r['length']['chars']} Chinese characters" for r in results)
    print(f"\nLength (approximate; use your template's own counting rule for minimums): {lens}")

    if not two:
        return 0

    print("\nInvariants (before vs after)")
    a, b = invariants(texts[0], is_latex), invariants(texts[1], is_latex)
    codes = [compare("numbers", a[0], b[0]), compare("citations", a[1], b[1]), compare("math", a[2], b[2])]

    terms = opts.get("--terms")
    if terms:
        changed = {t: (count_phrase(texts[0], t), count_phrase(texts[1], t)) for t in terms
                   if count_phrase(texts[0], t) != count_phrase(texts[1], t)}
        print(f"  {'key terms':<16} {'OK, counts match (' + str(len(terms)) + ')' if not changed else 'CHANGED'}")
        for t, (x, y) in changed.items():
            print(f"    '{t}': {x} -> {y}")
        codes.append(1 if changed else 0)
    else:
        print(f"  {'key terms':<16} NOT CHECKED (no --terms list given)")

    spans_a, spans_b = keep_spans(texts[0]), keep_spans(texts[1])
    extra = [s for s in opts.get("--protect", []) if s in texts[0]]
    not_found = [s for s in opts.get("--protect", []) if s not in texts[0]]
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
    elif not not_found:
        print(f"  {'protected spans':<16} NONE MARKED")
    for s in not_found:
        print(f"  {'protected spans':<16} NOT FOUND IN ORIGINAL, not checked: {s[:120]!r}")

    incomplete = []
    if any(x[2] for x in loaded):
        incomplete.append("missing \\input files (listed above as NOT FOUND)")
    if not_found:
        incomplete.append("--protect text not found in the original")

    n = (len(a[0]), len(a[1]), len(a[2]))
    if 1 in codes:
        print("\nRESULT: CHANGED. Something was added, lost or altered. Fix it before delivering.")
        return 1
    if incomplete:
        print("\nRESULT: INCOMPLETE. Nothing changed in what was checked, but some content was not "
              "checked: " + "; ".join(incomplete) + ".")
        return 3
    if 2 in codes:
        print("\nRESULT: REVIEW. The same items are present but in a different order. "
              "Check that no number or citation moved to a different claim.")
        return 2
    print(f"\nRESULT: recognized numbers ({n[0]}), citations ({n[1]}) and math ({n[2]}) match in count "
          f"and order in the {len(loaded[0][1])} file(s) listed above. Not verified: whether each number and "
          f"citation still belongs to the same claim. Read the diff for that.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
