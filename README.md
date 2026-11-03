# SciEntsBank-Grader
本项目为深度学习前沿课程中简答题自动评分任务参考代码，包含数据处理、基线运行和评价脚本，使用 SemEval-2013 Task 7 的 SciEntsBank 三分类数据。数据来源、引用和许可说明见文末。

## 项目内容

- 将上游原始数据转换为课程使用的 JSONL 文件
- 基础提示词与推理脚本模板
- 统一评价脚本
- 报告与实验建议

## 推荐目录结构

```text
project/
├─ README.md
├─ requirements.txt
├─ prompts/
│  └─ baseline_zh.txt
├─ scripts/
│  ├─ prepare_data.py
│  ├─ run_baseline.py
│  └─ evaluate.py
├─ data/
│  ├─ raw/              # 下载的原始压缩包
│  └─ processed/        # 生成的 JSONL 文件
└─ outputs/
   └─ predictions/      # 模型预测结果
```

## 快速开始

以下命令均在项目根目录执行。

### 1. 下载原始数据

从上游仓库下载 `semeval-3way.zip`：

[myrosia/semeval-2013-task7](https://github.com/myrosia/semeval-2013-task7)

建议保存为：

```text
data/raw/semeval-3way.zip
```

### 2. 生成课程数据

```bash
python scripts/prepare_data.py --archive data/raw/semeval-3way.zip --output_dir data/processed
```

脚本读取 SciEntsBank 的训练集和 UQ（未见题目）测试集，提取题目、参考答案、学生回答及标签。

运行后将生成：

- `data/processed/train.jsonl`
- `data/processed/test_uq.jsonl`
- `data/processed/label_info.json`

### 3. 运行基线

`run_baseline.py` 提供输入输出模板。请先接入所选的云端或本地模型，再执行：

```bash
python scripts/run_baseline.py --input data/processed/test_uq.jsonl --output outputs/predictions/baseline.jsonl --prompt_file prompts/baseline_zh.txt
```

API 密钥请通过环境变量或本地配置提供，不要提交到仓库。

### 4. 评价结果

```bash
python scripts/evaluate.py --gold data/processed/test_uq.jsonl --pred outputs/predictions/baseline.jsonl
```

## JSONL 格式说明

每行一个 JSON 对象。以下为格式示例，非数据集原始样本；为便于阅读，展开显示：

```json
{
  "id": "sample-0001",
  "split": "train",
  "question_id": "Q1",
  "question": "What is photosynthesis?",
  "reference_answer": "Photosynthesis is the process by which green plants make food using sunlight.",
  "student_answer": "Plants use sunlight to make food.",
  "label": "correct"
}
```

模型输入应包含题目、参考答案和学生回答，**不要包含 `label` 字段**。

## 实验建议

- 从训练集中划分开发集，用于选择提示词和参数。
- 方法确定后，再在 UQ 测试集上进行最终评价。
- 对非法标签、缺失预测和调用失败采用统一处理规则。
- 报告中记录数据版本、模型版本、提示词和参数，并分析典型评分错误。

## 数据来源与学术引用

本项目使用 SemEval-2013 Task 7 数据集中的 SciEntsBank 部分。原始数据及相关说明见：

[myrosia/semeval-2013-task7](https://github.com/myrosia/semeval-2013-task7)

根据上游说明，该数据为 SemEval-2013 Task 7 开发，基于 Myroslava Dzikovska 与 Rodney Nielsen 收集的语料。

使用该数据开展实验或撰写课程报告时，请按上游要求引用以下文献：

1. Dzikovska et al. (2013).  
   [SemEval-2013 Task 7: The Joint Student Response Analysis and 8th Recognizing Textual Entailment Challenge](https://aclanthology.org/S13-2045/).

2. Dzikovska, Nielsen, and Leacock.  
   [The joint student response analysis and recognizing textual entailment challenge: making sense of student responses in educational applications](https://doi.org/10.1007/s10579-015-9313-8).

## 数据许可与项目说明

- 上游数据采用 **CC BY-SA** 许可，具体版本及条款以上游仓库的许可说明为准。
- 本仓库不直接包含完整原始数据，课程使用的 JSONL 文件由用户在本地生成。
- 如公开再分发处理后的数据，应遵守上游许可，包括保留必要的署名及许可说明、注明修改，并按适用条款以相同许可分发。

本项目仅提供课程实验代码，非 SemEval-2013 Task 7 或 SciEntsBank 数据集的官方项目。
