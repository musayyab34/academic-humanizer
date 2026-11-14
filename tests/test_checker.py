#!/usr/bin/env python3
"""Regression tests for scripts/humanizer_check.py.

Run from the repository folder:  python tests/test_checker.py
Each case writes a 'before' and 'after' version to a temporary folder,
runs the checker on them and compares the exit code with the expected one.
"""
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
CHECKER = os.path.join(HERE, "..", "scripts", "humanizer_check.py")

BASE = r"""We train with 8 seeds. The baseline reaches 72% and our model reaches 85%.
ResNet fails on small images \cite{he2016deep}. ViT scales to large datasets \cite{dosovitskiy2021image}.
Latency changes by -2 ms. The loss is \(x+y\) for each batch.
"""

CASES = [
    # (name, before, after, extra_args, expected_exit)
    ("clean edit passes",
     BASE, BASE.replace("We train with 8 seeds.", "Training uses 8 seeds."), [], 0),
    ("control: changed number",
     BASE, BASE.replace("8 seeds", "9 seeds"), [], 1),
    ("sign and unit change: -2 ms -> +2 s",
     BASE, BASE.replace("-2 ms", "+2 s"), [], 1),
    ("swapped values: 72% and 85%",
     BASE, BASE.replace("reaches 72% and our model reaches 85%",
                        "reaches 85% and our model reaches 72%"), [], 2),
    ("swapped citation keys between claims",
     BASE, BASE.replace("he2016deep", "TMP").replace("dosovitskiy2021image", "he2016deep")
               .replace("TMP", "dosovitskiy2021image"), [], 2),
    ("inline math with \\( \\) changed",
     BASE, BASE.replace(r"\(x+y\)", r"\(x-y\)"), [], 1),
    ("hedge removed inside a marked keep span",
     "Intro.\n% keep\nThe effect may persist.\n% /keep\nEnd.\n",
     "Intro.\n% keep\nThe effect persists.\n% /keep\nEnd.\n", [], 1),
]


def run(before, after, args, tmp, name_before="before.tex", name_after="after.tex"):
    pb, pa = os.path.join(tmp, name_before), os.path.join(tmp, name_after)
    for p, t in ((pb, before), (pa, after)):
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w", encoding="utf-8") as f:
            f.write(t)
    r = subprocess.run([sys.executable, CHECKER, pb, pa] + args, capture_output=True, text=True)
    return r.returncode, r.stdout


def main():
    failures = 0
    with tempfile.TemporaryDirectory() as tmp:
        for i, (name, before, after, args, expected) in enumerate(CASES):
            sub = os.path.join(tmp, str(i))
            os.makedirs(sub)
            code, out = run(before, after, args, sub)
            ok = code == expected
            failures += not ok
            print(f"{'PASS' if ok else 'FAIL'}  {name}  (exit {code}, expected {expected})")
            if not ok:
                print(out)

        # Split manuscript: main.tex pulls in sections through \input.
        for label, changed, expected in (("split manuscript, change inside \\input file", True, 1),
                                         ("split manuscript, no change", False, 0)):
            sub = os.path.join(tmp, label.replace(" ", "_").replace("\\", ""))
            for side in ("before", "after"):
                root = os.path.join(sub, side)
                os.makedirs(os.path.join(root, "sections"))
                with open(os.path.join(root, "main.tex"), "w") as f:
                    f.write("\\documentclass{article}\n\\begin{document}\n"
                            "\\input{sections/intro}\n\\input{sections/results}\n\\end{document}\n")
                with open(os.path.join(root, "sections", "intro.tex"), "w") as f:
                    f.write("We study editing.\n")
                acc = "72.5" if (side == "after" and changed) else "72.4"
                with open(os.path.join(root, "sections", "results.tex"), "w") as f:
                    f.write(f"Accuracy is {acc}% on the test split.\n")
            r = subprocess.run([sys.executable, CHECKER, os.path.join(sub, "before"), os.path.join(sub, "after")],
                               capture_output=True, text=True)
            saw_files = "results.tex" in r.stdout
            ok = r.returncode == expected and saw_files
            failures += not ok
            print(f"{'PASS' if ok else 'FAIL'}  {label}  (exit {r.returncode}, expected {expected}, "
                  f"included files listed: {saw_files})")
            if not ok:
                print(r.stdout)

    print("\nAll tests passed." if not failures else f"\n{failures} test(s) failed.")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
