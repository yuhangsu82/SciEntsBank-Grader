import argparse
import json
from sklearn.metrics import accuracy_score, f1_score, classification_report


def load_jsonl(path):
    data = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                data.append(json.loads(line))
    return data


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--gold", required=True)
    parser.add_argument("--pred", required=True)
    args = parser.parse_args()

    gold = load_jsonl(args.gold)
    pred = load_jsonl(args.pred)

    labels = ["correct", "contradictory", "incorrect"]
    pred_map = {x["id"]: x["prediction"] for x in pred}
    y_true, y_pred = [], []

    for x in gold:
        if x["id"] in pred_map:
            y_true.append(x["label"])
            y_pred.append(pred_map[x["id"]])

    if not y_true:
        raise ValueError("没有匹配的样本 ID，无法计算评价指标")

    print("num_eval =", len(y_true))
    print("accuracy =", accuracy_score(y_true, y_pred))
    print("macro_f1 =", f1_score(
        y_true, y_pred, labels=labels, average="macro", zero_division=0
    ))
    print("weighted_f1 =", f1_score(
        y_true, y_pred, labels=labels, average="weighted", zero_division=0
    ))
    print(classification_report(
        y_true, y_pred, labels=labels, digits=4, zero_division=0
    ))


if __name__ == "__main__":
    main()
