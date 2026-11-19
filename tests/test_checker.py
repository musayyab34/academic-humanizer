#!/usr/bin/env python3
"""Regression tests for scripts/humanizer_check.py.

Run from the repository folder:  python tests/test_checker.py

Each case writes a 'before' and 'after' version to a temporary folder, runs the checker
on them and checks BOTH the exit code and the RESULT line, so a crash can never pass as
a detected change. The checker runs with a Windows-style output encoding (cp1252) to
make sure Chinese output does not crash it.
"""
import os
import subprocess
import sys
import tempfile
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
CHECKER = os.path.join(HERE, "..", "scripts", "humanizer_check.py")
RESULT_TEXT = {0: "RESULT: recognized", 1: "RESULT: CHANGED", 2: "RESULT: REVIEW", 3: "RESULT: INCOMPLETE"}
ENV = dict(os.environ, PYTHONIOENCODING="cp1252")


def run_checker(*args):
    r = subprocess.run([sys.executable, CHECKER, *args], capture_output=True, encoding="utf-8",
                       errors="replace", env=ENV)
    return r.returncode, r.stdout, r.stderr


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def make_docx(path, body_xml, footnotes_xml=None):
    """Minimal .docx. body_xml is the inside of <w:body>."""
    ns = ('xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" '
          'xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math"')
    with zipfile.ZipFile(path, "w") as z:
        z.writestr("[Content_Types].xml",
                   '<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
                   '<Default Extension="xml" ContentType="application/xml"/></Types>')
        z.writestr("word/document.xml", f'<?xml version="1.0" encoding="UTF-8"?><w:document {ns}><w:body>{body_xml}</w:body></w:document>')
        if footnotes_xml:
            z.writestr("word/footnotes.xml", f'<?xml version="1.0" encoding="UTF-8"?><w:footnotes {ns}>{footnotes_xml}</w:footnotes>')


def para(text):
    return f"<w:p><w:r><w:t>{text}</w:t></w:r></w:p>"


def script_eq_para(kind):
    """x with a superscript 2 (sSup) or a subscript 2 (sSub)."""
    part = "sup" if kind == "sSup" else "sub"
    return (f"<w:p><m:oMath><m:{kind}><m:e><m:r><m:t>x</m:t></m:r></m:e>"
            f"<m:{part}><m:r><m:t>2</m:t></m:r></m:{part}></m:{kind}></m:oMath></w:p>")


def eq_para(expr):
    return f"<w:p><w:r><w:t>Loss:</w:t></w:r><m:oMath><m:r><m:t>{expr}</m:t></m:r></m:oMath></w:p>"


BASE = r"""We train with 8 seeds. The baseline reaches 72% and our model reaches 85%.
ResNet fails on small images \cite{he2016deep}. ViT scales to large datasets \cite{dosovitskiy2021image}.
Latency changes by -2 ms. The loss is \(x+y\) for each batch.
"""
ZH = """本章研究模型压缩方法。值得注意的是，剪枝后模型的准确率为85.3%，比基线低1.2个百分点（张伟等，2021）。

实验在3个数据集上进行，结果见表2[4]。
"""

# (name, before, after, extra_args, file extension, expected exit)
TEXT_CASES = [
    ("clean edit passes", BASE, BASE.replace("We train with 8 seeds.", "Training uses 8 seeds."), [], ".tex", 0),
    ("control: changed number", BASE, BASE.replace("8 seeds", "9 seeds"), [], ".tex", 1),
    ("sign and unit change: -2 ms -> +2 s", BASE, BASE.replace("-2 ms", "+2 s"), [], ".tex", 1),
    ("swapped values: 72% and 85%", BASE, BASE.replace("reaches 72% and our model reaches 85%",
                                                       "reaches 85% and our model reaches 72%"), [], ".tex", 2),
    ("swapped citation keys between claims", BASE,
     BASE.replace("he2016deep", "TMP").replace("dosovitskiy2021image", "he2016deep").replace("TMP", "dosovitskiy2021image"),
     [], ".tex", 2),
    ("inline math with \\( \\) changed", BASE, BASE.replace(r"\(x+y\)", r"\(x-y\)"), [], ".tex", 1),
    ("hedge removed inside a marked keep span",
     "Intro.\n% keep\nThe effect may persist.\n% /keep\nEnd.\n",
     "Intro.\n% keep\nThe effect persists.\n% /keep\nEnd.\n", [], ".tex", 1),
    ("English unit change: 2 cm -> 2 mm", "The gap is 2 cm wide.\n", "The gap is 2 mm wide.\n", [], ".md", 1),
    ("scientific notation sign: 1e-3 -> 1e+3", "The learning rate is 1e-3.\n", "The learning rate is 1e+3.\n", [], ".md", 1),
    ("Chinese: stock phrase removed, facts kept", ZH, ZH.replace("值得注意的是，", ""), [], ".md", 0),
    ("Chinese: number changed (85.3% -> 85.4%)", ZH, ZH.replace("85.3%", "85.4%"), [], ".md", 1),
    ("Chinese: author-year citation removed", ZH, ZH.replace("（张伟等，2021）", ""), [], ".md", 1),
    ("Chinese unit change: 2毫秒 -> 2秒", "延迟为2毫秒。\n", "延迟为2秒。\n", [], ".md", 1),
    ("Chinese author outside brackets changed, year kept", "张伟等（2021）提出了该方法。\n",
     "李明等（2021）提出了该方法。\n", [], ".md", 1),
]


def main():
    for stream in (sys.stdout, sys.stderr):            # Chinese test names on Windows consoles
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass
    failures = 0

    def report(name, code, out, err, expected, extra_ok=True, extra_note=""):
        nonlocal failures
        ok = code == expected and RESULT_TEXT[expected] in out and extra_ok
        failures += not ok
        print(f"{'PASS' if ok else 'FAIL'}  {name}  (exit {code}, expected {expected}){extra_note}")
        if not ok:
            print(out[-2500:])
            if err:
                print("STDERR:", err[-1500:])

    with tempfile.TemporaryDirectory() as tmp:
        for i, (name, before, after, args, ext, expected) in enumerate(TEXT_CASES):
            pb, pa = os.path.join(tmp, f"t{i}", "before" + ext), os.path.join(tmp, f"t{i}", "after" + ext)
            write(pb, before)
            write(pa, after)
            report(name, *run_checker(pb, pa, *args), expected)

        # Split manuscript: main.tex pulls in sections through \input.
        for label, changed, expected in (("split manuscript, change inside \\input file", True, 1),
                                         ("split manuscript, no change", False, 0)):
            sub = os.path.join(tmp, "split" + str(expected))
            for side in ("before", "after"):
                write(os.path.join(sub, side, "main.tex"),
                      "\\documentclass{article}\n\\begin{document}\n\\input{sections/intro}\n\\input{sections/results}\n\\end{document}\n")
                write(os.path.join(sub, side, "sections", "intro.tex"), "We study editing.\n")
                acc = "72.5" if (side == "after" and changed) else "72.4"
                write(os.path.join(sub, side, "sections", "results.tex"), f"Accuracy is {acc}% on the test split.\n")
            code, out, err = run_checker(os.path.join(sub, "before"), os.path.join(sub, "after"))
            report(label, code, out, err, expected, "results.tex" in out)

        # Folder with two LaTeX roots (paper + supplement): a change in the supplement must count.
        sub = os.path.join(tmp, "roots")
        for side in ("before", "after"):
            write(os.path.join(sub, side, "main.tex"), "\\documentclass{article}\n\\begin{document}\nMain text with 7 runs.\n\\end{document}\n")
            n = "37" if side == "after" else "36"
            write(os.path.join(sub, side, "supp.tex"), f"\\documentclass{{article}}\n\\begin{{document}}\nWe use {n} hidden units.\n\\end{{document}}\n")
        code, out, err = run_checker(os.path.join(sub, "before"), os.path.join(sub, "after"))
        report("two LaTeX roots: change in the supplement", code, out, err, 1, "supp.tex" in out)

        # Missing \input in both versions: not a clean match.
        sub = os.path.join(tmp, "missing")
        for side in ("before", "after"):
            write(os.path.join(sub, side, "main.tex"), "\\documentclass{article}\n\\begin{document}\n\\input{missingsection}\nText.\n\\end{document}\n")
        report("missing \\input gives INCOMPLETE", *run_checker(os.path.join(sub, "before"), os.path.join(sub, "after")), 3)

        # --protect text that is not in the original: INCOMPLETE.
        sub = os.path.join(tmp, "protect")
        write(os.path.join(sub, "a.md"), "Some text.\n")
        write(os.path.join(sub, "b.md"), "Some text.\n")
        write(os.path.join(sub, "p.txt"), "This sentence is not in the document.\n")
        report("--protect text not found gives INCOMPLETE",
               *run_checker(os.path.join(sub, "a.md"), os.path.join(sub, "b.md"), "--protect", os.path.join(sub, "p.txt")), 3)

        # Word files: body text, native equation, footnote.
        word_cases = [
            ("Word: clean edit", [para("第一章 绪论"), para("值得注意的是，实验在3个数据集上进行。")],
             [para("第一章 绪论"), para("实验在3个数据集上进行。")], None, None, 0),
            ("Word: number changed", [para("实验在3个数据集上进行。")], [para("实验在4个数据集上进行。")], None, None, 1),
            ("Word: native equation changed (x+y -> x-y)", [eq_para("x+y")], [eq_para("x-y")], None, None, 1),
            ("Word: superscript changed to subscript (x² -> x₂)", [script_eq_para("sSup")], [script_eq_para("sSub")], None, None, 1),
            ("Word: footnote number changed", [para("正文。")], [para("正文。")],
             '<w:footnote w:id="1">' + para("数据来自2019年的调查。") + "</w:footnote>",
             '<w:footnote w:id="1">' + para("数据来自2020年的调查。") + "</w:footnote>", 1),
        ]
        for i, (name, body_a, body_b, fn_a, fn_b, expected) in enumerate(word_cases):
            pb, pa = os.path.join(tmp, f"w{i}_before.docx"), os.path.join(tmp, f"w{i}_after.docx")
            make_docx(pb, "".join(body_a), fn_a)
            make_docx(pa, "".join(body_b), fn_b)
            report(name, *run_checker(pb, pa), expected)

        # Single-document scans: (name, file name, text, required substrings in the output)
        scans = [
            ("abstract on its own lines is scanned", "abs1.tex",
             "\\documentclass{article}\n\\begin{document}\n\\begin{abstract}\nWe study pruning. "
             "It keeps accuracy. It works on three datasets.\n\\end{abstract}\n\\end{document}\n",
             ["Paragraphs: 1 English"]),
            ("abstract on one line is scanned", "abs2.tex",
             "\\documentclass{article}\n\\begin{document}\n\\begin{abstract}We study pruning. It works.\\end{abstract}\n\\end{document}\n",
             ["Paragraphs: 1 English"]),
            ("pseudocode semicolons are not counted as prose", "algo.tex",
             "\\documentclass{article}\n\\begin{document}\nWe describe the method.\n\n\\begin{algorithmic}\n"
             "\\State $a \\gets 0$; $b \\gets 1$; $c \\gets 2$;\n\\end{algorithmic}\n\\end{document}\n",
             ["semicolons                              0"]),
            ("English sentence quoting a long Chinese reply stays English", "quote.md",
             "The model replied: “这个问题的答案是模型无法确定输入图像中的物体类别，因为特征太弱了，需要更多数据来训练。” "
             "We count this as a failure.\n",
             ["Paragraphs: 1 English, 0 Chinese"]),
        ]
        for name, fname, text, needles in scans:
            path = os.path.join(tmp, fname)
            write(path, text)
            code, out, err = run_checker(path)
            ok = code == 0 and all(n in out for n in needles)
            failures += not ok
            print(f"{'PASS' if ok else 'FAIL'}  {name}")
            if not ok:
                print(out[-2000:], err[-1000:])

        # Weekly report written as a bullet list: items must be read, not dropped.
        pw = os.path.join(tmp, "weekly.md")
        write(pw, "## 本周工作\n\n- 本周取得了一定进展。\n- 遇到了一些问题。\n")
        code, out, err = run_checker(pw)
        ok = code == 0 and "取得了一定进展" in out and "遇到了一些问题" in out
        failures += not ok
        print(f"{'PASS' if ok else 'FAIL'}  weekly report bullets are scanned for evasive writing")
        if not ok:
            print(out[-2000:], err[-1000:])

    print("\nAll tests passed." if not failures else f"\n{failures} test(s) failed.")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
