def bounded_star(L, T):
    """
    计算有界星操作S^T(L)
    L: 语言，字符串集合
    T: 上界，最多拼接T个L中的字符串
    """
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