import argparse
import json
import re
import zipfile
from pathlib import Path, PurePosixPath
from xml.etree import ElementTree as ET


def normalize_space(text):
    return re.sub(r"\s+", " ", text or "").strip()


def local_name(tag):
    return tag.rsplit("}", 1)[-1]


def find_text(elem, tag_name):
    for child in elem.iter():
        if local_name(child.tag) == tag_name:
            return normalize_space("".join(child.itertext()))
    return ""


def detect_split(path_str):
    path = PurePosixPath(path_str.replace("\\", "/").lower())
    if path.suffix != ".xml":
        return None

    parts = path.parent.parts
    if parts[-3:] == ("training", "3way", "scientsbank"):
        return "train"
    if parts[-4:] == (
        "test", "3way", "scientsbank", "test-unseen-questions"
    ):
        return "test_uq"
    return None


def extract_records_from_xml(xml_bytes, path_hint, split):
    root = ET.fromstring(xml_bytes)
    question_id = root.get("id") or PurePosixPath(
        path_hint.replace("\\", "/")
    ).stem
    question = find_text(root, "questionText")
    reference = "\n".join(
        normalize_space("".join(elem.itertext()))
        for elem in root.iter()
        if local_name(elem.tag) == "referenceAnswer"
    )

    records = []
    for elem in root.iter():
        if local_name(elem.tag) != "studentAnswer":
            continue

        answer_id = elem.get("id") or str(len(records))
        label = normalize_space(elem.get("accuracy"))
        if label not in {"correct", "contradictory", "incorrect"}:
            raise ValueError(f"非法标签：{path_hint}, {answer_id}, {label!r}")

        records.append({
            "id": f"{split}:{question_id}:{answer_id}",
            "split": split,
            "question_id": question_id,
            "question": question,
            "reference_answer": reference,
            "student_answer": normalize_space("".join(elem.itertext())),
            "label": label
        })
    return records


def write_jsonl(path, records):
    with path.open("w", encoding="utf-8") as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--archive", required=True)
    parser.add_argument("--output_dir", required=True)
    parser.add_argument("--mode", choices=["3way"], default="3way")
    args = parser.parse_args()

    archive = Path(args.archive)
    output_dir = Path(args.output_dir)

    records = []
    with zipfile.ZipFile(archive, "r") as zf:
        for name in sorted(zf.namelist()):
            split = detect_split(name)
            if split is not None:
                records.extend(
                    extract_records_from_xml(zf.read(name), name, split)
                )

    train = [r for r in records if r["split"] == "train"]
    test_uq = [r for r in records if r["split"] == "test_uq"]

    if not train or not test_uq:
        raise ValueError("训练集或 UQ 测试集为空，请检查压缩包路径和 XML 内容")

    output_dir.mkdir(parents=True, exist_ok=True)
    write_jsonl(output_dir / "train.jsonl", train)
    write_jsonl(output_dir / "test_uq.jsonl", test_uq)

    info = {
        "archive": str(archive),
        "num_records": len(records),
        "num_train": len(train),
        "num_test_uq": len(test_uq),
        "labels": sorted({r["label"] for r in records})
    }
    (output_dir / "label_info.json").write_text(
        json.dumps(info, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    print(json.dumps(info, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
