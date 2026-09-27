"""Measures how accurate the NER is on test_notes.txt.

    python evaluate.py              # dictionary + Hugging Face model
    USE_HF=0 python evaluate.py     # dictionary only (to compare)

Exact  = the highlighted text and label match the answer exactly.
Overlap = the label matches and the text overlaps the answer
          (e.g. "fever" for the answer "high fever").
"""
import re
from pathlib import Path

from NER import USE_HF, perform_ner

LABELS = ["SYMPTOM", "DRUG", "DISEASE"]
MARK = re.compile(r"\[([^\]]+)\]\((SYMPTOM|DRUG|DISEASE)\)")


def load_notes(path):
    """Turn '[fever](SYMPTOM)' marks into plain text + answer spans."""
    notes = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        text, gold, pos = "", [], 0
        for m in MARK.finditer(line):
            text += line[pos:m.start()]
            gold.append((len(text), len(text) + len(m.group(1)), m.group(2)))
            text += m.group(1)
            pos = m.end()
        notes.append((text + line[pos:], gold))
    return notes


def overlaps(a, b):
    return a[2] == b[2] and a[0] < b[1] and b[0] < a[1]


def prf(tp, n_pred, n_gold):
    p = tp / n_pred if n_pred else 0.0
    r = tp / n_gold if n_gold else 0.0
    f = 2 * p * r / (p + r) if p + r else 0.0
    return p, r, f


def main():
    notes = load_notes(Path(__file__).parent / "test_notes.txt")
    counts = {label: {"exact": 0, "overlap": 0, "pred": 0, "gold": 0} for label in LABELS}
    mistakes = []

    for text, gold in notes:
        pred = [(e["start"], e["end"], e["label"]) for e in perform_ner(text)["ents"] if not e["negated"]]
        for label in LABELS:
            g = [s for s in gold if s[2] == label]
            p = [s for s in pred if s[2] == label]
            counts[label]["gold"] += len(g)
            counts[label]["pred"] += len(p)
            counts[label]["exact"] += len(set(g) & set(p))
            counts[label]["overlap"] += sum(any(overlaps(x, y) for y in g) for x in p)
        for s in pred:
            if not any(overlaps(s, g) for g in gold):
                mistakes.append(f"  wrong:  '{text[s[0]:s[1]]}' as {s[2]}")
        for g in gold:
            if not any(overlaps(g, s) for s in pred):
                mistakes.append(f"  missed: '{text[g[0]:g[1]]}' ({g[2]})")

    print(f"\n{len(notes)} notes · model: {'dictionary + Hugging Face' if USE_HF else 'dictionary only'}\n")
    print(f"{'':10}{'Exact P':>9}{'R':>7}{'F1':>7}   {'Overlap P':>10}{'R':>7}{'F1':>7}")
    total = {"exact": 0, "overlap": 0, "pred": 0, "gold": 0}
    for label in LABELS + ["ALL"]:
        c = total if label == "ALL" else counts[label]
        if label != "ALL":
            for k in total:
                total[k] += c[k]
        ep, er, ef = prf(c["exact"], c["pred"], c["gold"])
        op, orr, of = prf(c["overlap"], c["pred"], c["gold"])
        print(f"{label:10}{ep:9.0%}{er:7.0%}{ef:7.0%}   {op:10.0%}{orr:7.0%}{of:7.0%}")

    print(f"\nMistakes ({len(mistakes)}):")
    print("\n".join(mistakes) if mistakes else "  none")


if __name__ == "__main__":
    main()