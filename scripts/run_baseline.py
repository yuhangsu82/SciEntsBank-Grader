import argparse
import json
from pathlib import Path

from openai import OpenAI
from tqdm import tqdm

# 请在运行前设置以下环境变量：
API_KEY = "xxxxxxxx"
BASE_URL = "xxxxxxxx"
MODEL = "xxxxxxxx"  # 例如 "gpt-4o-mini"
VALID_LABELS = {"correct", "contradictory", "incorrect"}


def load_jsonl(path):
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def predict(sample, prompt_text, client):
    result = {
        "id": sample["id"],
        "model": MODEL,
        "messages": None,
        "prediction": None,
        "raw_response": None,
        "usage": None,
        "error": None,
    }

    try:
        messages = [
            {
                "role": "system",
                "content": (
                    prompt_text
                    + "\n只输出一个标签：correct、contradictory 或 incorrect。"
                    + "不要输出解释、引号或其他内容。"
                ),
            },
            {
                "role": "user",
                "content": json.dumps({
                    "question": sample["question"],
                    "reference_answer": sample["reference_answer"],
                    "student_answer": sample["student_answer"],
                }, ensure_ascii=False),
            },
        ]
        result["messages"] = messages

        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            max_tokens=1024,
            stream=False,
        )

        result["usage"] = (
            response.usage.model_dump()
            if response.usage is not None else None
        )
        result["raw_response"] = response.choices[0].message.content
        pred = (result["raw_response"] or "").strip()

        if pred not in VALID_LABELS:
            raise ValueError(f"非法预测：{pred!r}")

        result["prediction"] = pred

    except Exception as exc:
        result["error"] = f"{type(exc).__name__}: {exc}"
        tqdm.write(f"[ERROR] {sample['id']}: {result['error']}")

    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--prompt_file", required=True)
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args()

    if args.limit is not None and args.limit <= 0:
        parser.error("--limit 必须大于 0")

    data = load_jsonl(args.input)
    prompt_text = Path(args.prompt_file).read_text(encoding="utf-8")

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # 默认恢复：跳过已有成功结果，失败样本重新尝试。
    previous = load_jsonl(output_path) if output_path.exists() else []
    done_ids = {
        x["id"] for x in previous
        if x.get("prediction") in VALID_LABELS
        and not x.get("error")
    }

    pending = [x for x in data if x["id"] not in done_ids]
    pending = pending[:args.limit]

    print(f"总样本 {len(data)}，本次处理 {len(pending)}")

    with OpenAI(
        api_key=API_KEY,
        base_url=BASE_URL,
        timeout=120,
        max_retries=2,
    ) as client:
        with output_path.open("a", encoding="utf-8") as f:
            for sample in tqdm(pending, desc="Predicting", unit="sample"):
                result = predict(sample, prompt_text, client)
                f.write(json.dumps(result, ensure_ascii=False) + "\n")
                f.flush()

    print(f"结果已保存到 {output_path}")


if __name__ == "__main__":
    main()
