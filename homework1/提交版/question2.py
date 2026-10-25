def bounded_star(L, T):
    """
    计算有界星操作S^T(L)
    L: 语言，字符串集合
    T: 上界，最多拼接T个L中的字符串
    """
    if not isinstance(L, (set, frozenset)):
        raise TypeError("L 必须是字符串集合（set 或 frozenset）")
    if any(not isinstance(w, str) for w in L):
        raise TypeError("L 中的每个元素都必须是字符串")
    if isinstance(T, bool) or not isinstance(T, int):
        raise TypeError("T 必须是非负整数，不能是布尔值")
    if T < 0:
        raise ValueError("T 不能为负数")

    result = set()

    def dfs(current, depth):
        result.add(current)
        if depth == T:
            return
        for w in L:
            dfs(current + w, depth + 1)

    dfs("", 0)
    return result


if __name__ == "__main__":
    # |L| >= 2
    L = {"q", "qu", "u"}

    T = 3
    result = bounded_star(L, T)

    print(f"L = {L}")
    print(f"T = {T}")
    print(f"S^{T}(L) 中共有 {len(result)} 个字符串：")
    for s in sorted(result, key=lambda x: (len(x), x)):
        if s == "":
            print("ε")   # 空串用ε表示
        else:
            print(s)
