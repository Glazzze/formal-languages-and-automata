"""第三题边界测试，以及第一、二题的跨题独立验证。

题图数据按作业 PDF 第 1、2 页逐条录入；模拟、乘积自动机等价判定和最小性
检查均在本文件独立实现，因此不依赖 question1.py、question2.py 也能给出
预期结果。组内代码交付后，把实际自动机整理成同样的字典格式，即可复用本
文件的检查函数核对输出。

自动机字典格式与作业题面一致：
    {"Q": 状态集合, "SIGMA": 字母表, "DELTA": {(状态, 字符): 状态},
     "q0": 初态, "F": 终态集合}
"""

from itertools import product

from question3 import judge


# 第一题题图（lec4-rs1 第 34 页）：自动机 1，接受以 1 结尾的串。
Q1_MACHINE_1 = {
    "Q": {"A", "B"},
    "SIGMA": {"0", "1"},
    "DELTA": {
        ("A", "0"): "A",
        ("A", "1"): "B",
        ("B", "0"): "A",
        ("B", "1"): "A",
    },
    "q0": "A",
    "F": {"B"},
}

# 第一题题图：自动机 2，C、D 均为终态，接受全部 0/1 串。
Q1_MACHINE_2 = {
    "Q": {"C", "D"},
    "SIGMA": {"0", "1"},
    "DELTA": {
        ("C", "0"): "D",
        ("C", "1"): "C",
        ("D", "0"): "D",
        ("D", "1"): "C",
    },
    "q0": "C",
    "F": {"C", "D"},
}

# 第二题题图：7 状态 DFA D，终态为 FS2、FS5、FS6。
Q2_MACHINE_D = {
    "Q": {"IS0", "S1", "FS2", "S3", "S4", "FS5", "FS6"},
    "SIGMA": {"0", "1"},
    "DELTA": {
        ("IS0", "0"): "S1",
        ("IS0", "1"): "S1",
        ("S1", "0"): "FS2",
        ("S1", "1"): "FS5",
        ("FS2", "0"): "IS0",
        ("FS2", "1"): "IS0",
        ("S3", "0"): "S4",
        ("S3", "1"): "S4",
        ("S4", "0"): "FS5",
        ("S4", "1"): "FS6",
        ("FS5", "0"): "S3",
        ("FS5", "1"): "S3",
        ("FS6", "0"): "IS0",
        ("FS6", "1"): "IS0",
    },
    "q0": "IS0",
    "F": {"FS2", "FS5", "FS6"},
}

# 第二题的独立预期结果：长度模 3 等于 2 的串构成的语言，3 个状态即最小。
Q2_EXPECTED_MIN = {
    "Q": {"X", "Y", "Z"},
    "SIGMA": {"0", "1"},
    "DELTA": {
        ("X", "0"): "Y",
        ("X", "1"): "Y",
        ("Y", "0"): "Z",
        ("Y", "1"): "Z",
        ("Z", "0"): "X",
        ("Z", "1"): "X",
    },
    "q0": "X",
    "F": {"Z"},
}

# 核验器自检用的一对等价自动机，只用于确认检查函数本身可靠。
SELFTEST_1 = {
    "Q": {"P0", "P1"},
    "SIGMA": {"0", "1"},
    "DELTA": {
        ("P0", "0"): "P0",
        ("P0", "1"): "P1",
        ("P1", "0"): "P0",
        ("P1", "1"): "P1",
    },
    "q0": "P0",
    "F": {"P1"},
}

SELFTEST_2 = {
    "Q": {"R0", "R1", "R2"},
    "SIGMA": {"0", "1"},
    "DELTA": {
        ("R0", "0"): "R0",
        ("R0", "1"): "R1",
        ("R1", "0"): "R0",
        ("R1", "1"): "R2",
        ("R2", "0"): "R0",
        ("R2", "1"): "R2",
    },
    "q0": "R0",
    "F": {"R1", "R2"},
}


def dfa_accepts(dfa, word):
    """按字典格式模拟 DFA。要求该 DFA 完整且确定，否则抛出 ValueError。"""
    current = dfa["q0"]
    for symbol in word:
        if symbol not in dfa["SIGMA"]:
            raise ValueError(f"字符 {symbol!r} 不在字母表中")
        try:
            current = dfa["DELTA"][(current, symbol)]
        except KeyError:
            raise ValueError(f"缺少转移：({current}, {symbol})") from None
    return current in dfa["F"]


def words(alphabet, max_length):
    """按长度、字典序生成所有长度不超过 max_length 的串。"""
    if max_length < 0:
        raise ValueError("max_length 不能为负数")
    for length in range(max_length + 1):
        for symbols in product(sorted(alphabet), repeat=length):
            yield "".join(symbols)


def check_dfa(dfa, name="自动机"):
    """检查状态引用、转移完整性与确定性。"""
    problems = []
    if not dfa["Q"]:
        problems.append("状态集合为空")
    if dfa["q0"] not in dfa["Q"]:
        problems.append(f"初态 {dfa['q0']} 不在状态集合中")
    if not set(dfa["F"]) <= set(dfa["Q"]):
        problems.append(f"终态 {sorted(set(dfa['F']) - set(dfa['Q']), key=str)} 不在状态集合中")
    for state in dfa["Q"]:
        for symbol in dfa["SIGMA"]:
            target = dfa["DELTA"].get((state, symbol))
            if target is None:
                problems.append(f"缺少转移 ({state}, {symbol})")
            elif target not in dfa["Q"]:
                problems.append(f"转移 ({state}, {symbol}) 指向未知状态 {target}")
    for state, symbol in dfa["DELTA"]:
        if state not in dfa["Q"] or symbol not in dfa["SIGMA"]:
            problems.append(f"转移 ({state}, {symbol}) 的起点或字符不合法")
    if problems:
        raise AssertionError(f"{name} 数据有误：" + "；".join(problems))


def _show(word):
    """空串显示为 ε，避免打印出空引号。"""
    return word if word else "ε"


def _witness(parent, pair):
    symbols = []
    while parent[pair] is not None:
        pair, symbol = parent[pair]
        symbols.append(symbol)
    return "".join(reversed(symbols))


def _search(first, second, start, symbols, is_final):
    """在状态对图上广度优先搜索，返回最短可区分串；不可区分时返回 None。"""
    parent = {start: None}
    frontier = [start]
    while frontier:
        next_frontier = []
        for pair in frontier:
            if is_final(pair[0], pair[1]):
                return _witness(parent, pair)
            for symbol in symbols:
                child = (first(pair[0], symbol), second(pair[1], symbol))
                if child not in parent:
                    parent[child] = (pair, symbol)
                    next_frontier.append(child)
        frontier = next_frontier
    return None


def equivalent_by_product(dfa_a, dfa_b):
    """按乘积自动机判定等价；返回 (是否等价, 最短区分串或 None)。"""
    if dfa_a["SIGMA"] != dfa_b["SIGMA"]:
        raise ValueError("两个 DFA 必须使用相同字母表")
    check_dfa(dfa_a, "第一个自动机")
    check_dfa(dfa_b, "第二个自动机")
    witness = _search(
        lambda state, symbol: dfa_a["DELTA"][(state, symbol)],
        lambda state, symbol: dfa_b["DELTA"][(state, symbol)],
        (dfa_a["q0"], dfa_b["q0"]),
        sorted(dfa_a["SIGMA"]),
        lambda state_a, state_b: (state_a in dfa_a["F"]) != (state_b in dfa_b["F"]),
    )
    return witness is None, witness


def reachable_states(dfa):
    seen = {dfa["q0"]}
    stack = [dfa["q0"]]
    while stack:
        state = stack.pop()
        for symbol in dfa["SIGMA"]:
            target = dfa["DELTA"][(state, symbol)]
            if target not in seen:
                seen.add(target)
                stack.append(target)
    return seen


def distinguishing_string(dfa, state_a, state_b):
    """返回两个状态的最短区分串；空串表示接受性不同；不可区分时返回 None。"""
    return _search(
        lambda state, symbol: dfa["DELTA"][(state, symbol)],
        lambda state, symbol: dfa["DELTA"][(state, symbol)],
        (state_a, state_b),
        sorted(dfa["SIGMA"]),
        lambda left, right: (left in dfa["F"]) != (right in dfa["F"]),
    )


def check_minimality(dfa, name="自动机"):
    """独立检查最小性：全部状态可达，且任意两个不同状态都可区分。"""
    check_dfa(dfa, name)
    unreachable = set(dfa["Q"]) - reachable_states(dfa)
    if unreachable:
        raise AssertionError(f"{name} 存在不可达状态：{sorted(unreachable, key=str)}")
    states = sorted(dfa["Q"], key=str)
    for index, state_a in enumerate(states):
        for state_b in states[index + 1:]:
            if distinguishing_string(dfa, state_a, state_b) is None:
                raise AssertionError(f"{name} 中状态 {state_a} 与 {state_b} 不可区分")
    return len(states)


def check_question1_short_strings(
    dfa_a, dfa_b, reported_equivalent, expected_equivalent, max_length=4
):
    """枚举短串核对第一题结论；不等价时要求短串中能找到区分串。"""
    if dfa_a["SIGMA"] != dfa_b["SIGMA"]:
        raise ValueError("短串比较要求两个 DFA 使用相同字母表")
    mismatches = [
        word for word in words(dfa_a["SIGMA"], max_length)
        if dfa_accepts(dfa_a, word) != dfa_accepts(dfa_b, word)
    ]
    if bool(reported_equivalent) != expected_equivalent:
        raise AssertionError("第一题等价判定结果与独立预期不符")
    if expected_equivalent and mismatches:
        raise AssertionError(f"发现区分串：{_show(mismatches[0])}")
    if not expected_equivalent and not mismatches:
        raise AssertionError(
            f"长度不超过 {max_length} 的枚举未找到区分串；请加大上界"
        )
    return len(list(words(dfa_a["SIGMA"], max_length))), mismatches


def check_question2_short_strings(original, minimized, max_length=6):
    """枚举短串，比较原 DFA 与最小化 DFA 的接受结果。"""
    if original["SIGMA"] != minimized["SIGMA"]:
        raise ValueError("原 DFA 与最小化 DFA 必须使用相同字母表")
    for word in words(original["SIGMA"], max_length):
        if dfa_accepts(original, word) != dfa_accepts(minimized, word):
            raise AssertionError(f"最小化前后语言不一致，区分串：{_show(word)}")
    return len(list(words(original["SIGMA"], max_length)))


def merge_mapping(original, minimized):
    """为原 DFA 的每个状态找出语言相同的最小化状态，用于核对合并关系。"""
    variants = [
        dict(minimized, q0=state) for state in sorted(minimized["Q"], key=str)
    ]
    mapping = {}
    for state in sorted(original["Q"], key=str):
        matches = [
            variant["q0"] for variant in variants
            if equivalent_by_product(_start_at(original, state), variant)[0]
        ]
        if len(matches) != 1:
            raise AssertionError(f"状态 {state} 无法唯一对应到最小化状态：{matches}")
        mapping[state] = matches[0]
    return mapping


def _start_at(dfa, state):
    return dict(dfa, q0=state)


def verify_question3_variable_limit():
    """自动审查判定核心的局部变量与递归，辅助人工逐行复核。"""
    print("== 第三题：变量限制审查 ==")
    code = judge.__code__
    allowed = {"s", "S", "ch"}
    extra = set(code.co_varnames) - allowed
    if extra:
        raise AssertionError(f"判定函数出现额外局部变量：{sorted(extra)}")
    if "judge" in code.co_names:
        raise AssertionError("判定函数中出现递归调用")
    print(f"  局部变量：{sorted(code.co_varnames)}；仅参数 s、堆栈 S、循环变量 ch")
    print("  未发现递归调用")


def _reference_member(word):
    """独立构造 0^k1^k（k>=1）判定，作为穷举检查的对照。"""
    zeros = len(word) - len(word.lstrip("0"))
    return zeros > 0 and word == "0" * zeros + "1" * zeros


def verify_question3_exhaustive(max_length=8):
    """在 {0,1,a} 上穷举短串，与构造式判定逐一比较。"""
    checked = 0
    for word in words("01a", max_length):
        if judge(word) != _reference_member(word):
            raise AssertionError(f"第三题穷举不一致：{_show(word)!r}")
        checked += 1
    print(f"第三题穷举（字母表 {{0,1,a}}，长度 0～{max_length}）：{checked} 个串全部一致")


def verify_question3_boundaries():
    cases = (
        ("01", True),
        ("0011", True),
        ("000111", True),
        ("", False),
        ("0", False),
        ("1", False),
        ("00", False),
        ("11", False),
        ("011", False),
        ("001", False),
        ("0101", False),
        ("00110", False),
        ("10", False),
        ("00a11", False),
        ("001111", False),
        ("00011", False),
    )
    for input_string, expected in cases:
        actual = judge(input_string)
        if actual != expected:
            raise AssertionError(
                f"第三题用例 {input_string!r} 预期 {expected}，实际 {actual}"
            )
        verdict = "接受" if expected else "拒绝"
        print(f"  第三题 {_show(input_string)!r}: 预期{verdict}，实际{verdict}（通过）")
    print(f"第三题边界测试：{len(cases)}/{len(cases)} 通过")


def verify_question1():
    print("== 第一题：题图两个自动机 ==")
    check_dfa(Q1_MACHINE_1, "题图自动机 1")
    check_dfa(Q1_MACHINE_2, "题图自动机 2")
    equivalent, witness = equivalent_by_product(Q1_MACHINE_1, Q1_MACHINE_2)
    if equivalent:
        raise AssertionError("题图两个自动机应不等价")
    counted, mismatches = check_question1_short_strings(
        Q1_MACHINE_1, Q1_MACHINE_2, False, False, max_length=5
    )
    print(f"  乘积自动机判定：不等价，最短区分串 {_show(witness)}")
    print(f"  短串核对：枚举 {counted} 个串，首次发现差异 {_show(mismatches[0])}")
    selftest_equivalent, _ = equivalent_by_product(SELFTEST_1, SELFTEST_2)
    if not selftest_equivalent:
        raise AssertionError("核验器自检失败：构造的一对等价自动机被判为不等价")
    counted, _ = check_question1_short_strings(
        SELFTEST_1, SELFTEST_2, True, True, max_length=5
    )
    print(f"  核验器自检：一对等价自动机（2 状态与 3 状态）判定等价，枚举 {counted} 个串一致")


def verify_question2():
    print("== 第二题：7 状态自动机 D ==")
    check_dfa(Q2_MACHINE_D, "题图自动机 D")
    if len(Q2_MACHINE_D["Q"]) != 7:
        raise AssertionError("题图自动机 D 应为 7 个状态")
    unreachable = set(Q2_MACHINE_D["Q"]) - reachable_states(Q2_MACHINE_D)
    if unreachable:
        raise AssertionError(f"题图自动机 D 存在不可达状态：{sorted(unreachable, key=str)}")

    equivalent, witness = equivalent_by_product(Q2_MACHINE_D, Q2_EXPECTED_MIN)
    if not equivalent:
        raise AssertionError(f"独立预期与实际不符，区分串：{_show(witness)}")
    for word in words({"0", "1"}, 8):
        if dfa_accepts(Q2_MACHINE_D, word) != (len(word) % 3 == 2):
            raise AssertionError(f"自动机 D 接受性与长度关系不符：{word!r}")
    print("  自动机 D 的语言：长度模 3 余 2 的 0/1 串（长度 0～8 共 511 个串核对一致）")

    count = check_minimality(Q2_EXPECTED_MIN, "独立预期最小自动机")
    counted = check_question2_short_strings(Q2_MACHINE_D, Q2_EXPECTED_MIN, max_length=8)
    print(f"  独立预期：{count} 个状态，全部可达且两两可区分，短串 {counted} 个一致")

    mapping = merge_mapping(Q2_MACHINE_D, Q2_EXPECTED_MIN)
    groups = {}
    for state, target in mapping.items():
        groups.setdefault(target, []).append(state)
    for target in sorted(groups, key=str):
        print(f"  合并关系：{target} <- {{{', '.join(groups[target])}}}")
    print("  最小化 DFA 的预期转移表：")
    for state in sorted(Q2_EXPECTED_MIN["Q"], key=str):
        mark = ("->" if state == Q2_EXPECTED_MIN["q0"] else "") + (
            "*" if state in Q2_EXPECTED_MIN["F"] else ""
        )
        row = [Q2_EXPECTED_MIN["DELTA"][(state, symbol)] for symbol in sorted(Q2_EXPECTED_MIN["SIGMA"])]
        print(f"    {mark:<4}{state:<4}0->{row[0]:<4}1->{row[1]}")
    return count, mapping


if __name__ == "__main__":
    verify_question3_variable_limit()
    verify_question3_boundaries()
    verify_question3_exhaustive()
    verify_question1()
    minimum_states, merge = verify_question2()
    print(
        "第一、二题独立验证完成：题图数据已按 PDF 录入并核对；"
        f"第二题最小状态数 {minimum_states}。"
    )
    print(
        "组内 question1.py、question2.py 交付后，把实际自动机整理为 "
        "Q/SIGMA/DELTA/q0/F 字典，调用 check_question1_short_strings、"
        "check_question2_short_strings、check_minimality 与本文件预期对照。"
    )
