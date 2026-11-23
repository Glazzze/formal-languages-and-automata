# 形式语言与自动机 · 第二次 Python 编程作业

## 小组分工

| 成员 | 分工 | 代码与记录 |
| --- | --- | --- |
| 廖敏佳（A） | 公共自动机类、题图数据、基础测试 | `dfa.py`、`dfa_examples.py`、`test_dfa.py`、[接口说明](接口说明.md) |
| 黄爱心（B） | 第一题语言等价判定、自构正例、第二题等价性复核 | `question1_dfa_equivalence.py`、`verify_minimization_equivalence.py`、[第一题运行结果](question1运行结果.txt)、[等价性复核](question2等价性复核运行结果.txt) |
| 刘倪羽晗（C） | 第二题最小化、合并映射、自构 DFA | `question2_dfa_minimization.py`、`test_dfa_minimization.py`、[第二题说明](第二题说明.md)、[第二题运行结果](第二题运行结果.txt) |
| 刘嘉瑜（D） | 第三题堆栈判定、边界测试、跨题独立核验 | `question3_stack_membership.py`、`verify_submission.py`、[第三题说明与测试记录](第三题说明与测试记录.md)、[第三题运行结果](第三题运行结果.txt) |
| 刘雅静（组长） | 第二题完整输出、接口整合与验收 | `dfa_display.py`、[基础测试结果](基础测试结果.txt) |

Python 源码和验证脚本位于 [提交版](提交版/)，说明和运行记录位于本目录。第一、二题共用 `dfa.py` 中的 `Automaton`，从 `dfa_examples.py` 读取题图与自构用例。第二题通过 `dfa_display.py` 输出初态、终态、完整转移表与合并关系。第三题可独立运行。

## 运行

使用 Python 3.9 或以上版本，仅依赖标准库。在仓库根目录执行以下命令。

```bash
cd homework2/提交版
python3 question1_dfa_equivalence.py
python3 question2_dfa_minimization.py
python3 question3_stack_membership.py
```

| 题目 | 预期结果 |
| --- | --- |
| 第一题 | 题图自动机不等价，最短区分串为 `ε`。自构的 2 状态与 3 状态 DFA 等价，都识别以 `0` 结尾的串。 |
| 第二题 | 题图 DFA D 从 7 个状态缩减到 3 个状态，初态为 `Q1`，唯一终态为 `Q0`。两个自构用例分别检查合并与删除不可达状态、保留已最小结构。 |
| 第三题 | `01`、`0011`、`000111` 输出“接受”，`011`、`0101` 和空串输出“拒绝”。 |

## 验证

在 `homework2/提交版` 中运行以下命令。

```bash
python3 -m unittest -v test_dfa test_dfa_minimization
python3 verify_minimization_equivalence.py
python3 verify_submission.py
```

单元测试覆盖公共类、题图输入及两题的互操作。等价性复核检查 3 组最小化前后的 DFA，并使用清空终态的错误结果作对照。独立核验逐项比较题图数据，检查最小化结果的可达性和状态可区分性，并核对第三题的 16 个边界用例与 9,841 个短串。

## 电子版材料

[提交版 README](提交版/README.md)和[自构用例](提交版/自构用例.txt)与 Python 源码一同放在 `提交版`。电子版邮件标题和压缩包基础名称均使用 `刘雅静-<组长学号>-形式语言第二次编程作业`，将学号替换为真实值后使用。
