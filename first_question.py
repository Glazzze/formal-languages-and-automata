#拼接函数定义
def concatenate_language(L1,L2):
    result_language=set()
    for x in L1:
        for y in L2:
            result_language.add(x+y)
    return result_language
#拼接
if __name__=='__main__':
    #自行构造L1，L2
    L1={"a","AB","cde","FGHI"}
    L2={"10","211","3222","43333"}
    print("语言L1=",L1)
    print("语言L2=",L2)
    L3=concatenate_language(L1,L2)
    print("串接后的语言 L1L2 中的所有字符串如下：")
    for string in L3:
        print(string)