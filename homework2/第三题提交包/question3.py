def judge(s: str) -> bool:
    """判断 s 是否属于 {0^k 1^k | k >= 1}。"""
    S = []

    for ch in s:
        if ch == "0":
            if S and S[-1] == "|":
                return False
            S.append("0")
        elif ch == "1":
            if not S:
                return False
            if S[-1] == "|":
                S.pop()
                if not S or S[-1] != "0":
                    return False
                S.pop()
                S.append("|")
            else:
                S.append("|")
                S.pop()
                S.pop()
                S.append("|")
        else:
            return False

    return S == ["|"]


if __name__ == "__main__":
    print("01：", "接受" if judge("01") else "拒绝")
    print("0011：", "接受" if judge("0011") else "拒绝")
    print("000111：", "接受" if judge("000111") else "拒绝")
    print("011：", "接受" if judge("011") else "拒绝")
    print("0101：", "接受" if judge("0101") else "拒绝")
    print("空串：", "接受" if judge("") else "拒绝")
