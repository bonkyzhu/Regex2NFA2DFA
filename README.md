# 编译原理项目-正则到NFA到DFA

## 环境配置

本项目经测试在以下环境下可以正常运行：

- `macOS Mojave 10.14.2`
- `Python 3.7.1`
- `graphviz: stable 2.40.1 对应的Python包版本为0.13`

## 原理介绍

> 主要参考：https://cn.charlee.li/parse-regex-with-dfa.html

### Thompson构造法 - 将正则式转换为NFA

- 输入: 字母表`Σ`上的正则表达式`r`

- 输出: 能够接受`L(r)`的NFA `N`

- 方法: 首先将构成`r`的各个元素分解，对于每一个元素，按照下述**规则1**和**规则2**生成NFA。

  **注意**: 如果`r`中记号`a`出现了多次，那么对于`a`的每次出现都需要生成一个单独的NFA。 之后依照正则表达式r的文法规则，将生成的NFA按照下述**规则3**组合在一起。

  - 规则1: 对于空记号`ε`，生成下面的NFA。

    ![fig01.png](http://bonky-picture.oss-cn-beijing.aliyuncs.com/pic/1u6xw.png)

  - 规则2: 对于`Σ`的字母表中的元素`a`，生成下面的NFA。

    ![fig02.png](http://bonky-picture.oss-cn-beijing.aliyuncs.com/pic/a4xri.png)

  - 规则3: 令正则表达式`s`和`t`的NFA分别为`N(s)`和`N(t)`。

    1. 对于`s|t`，按照以下的方式生成NFA `N(s|t)`。

       ![fig03.png](http://bonky-picture.oss-cn-beijing.aliyuncs.com/pic/xbdck.png)

    2. 对于`st`，按照以下的方式生成NFA `N(st)`。

       ![fig04.png](http://bonky-picture.oss-cn-beijing.aliyuncs.com/pic/rconu.png)

    3. 对于`s*`，按照以下的方式生成NFA `N(s*)`。

       ![fig05.png](http://bonky-picture.oss-cn-beijing.aliyuncs.com/pic/hell0.png)

    4. 对于`(s)`，使用`s`本身的NFA `N(s)`。

- 代码实现则使用递归的方法，将N(S)看做一个函数或者说子正则式，向下递归。对于返回的值再根据规则3连接在一起即可



## 将NFA转化为DFA

- 输入: NFA `N`

- 输出: 能够接受与N相同语言的DFA `D`

- 方法: 本算法生成D对应的状态迁移表`Dtran`。DFA的各个状态为NFA的状态集合， 对于每一个输入符号，`D`模拟`N`中可能的状态迁移。

  定义以下的操作。

  | 操作           | 说明                                                         |
  | -------------- | ------------------------------------------------------------ |
  | `ε-closure(s)` | 从NFA的状态`s`出发，仅通过`ε`迁移能够到达的NFA的状态集合     |
  | `ε-closure(T)` | 从`T`中包含的某个NFA的状态`s`出发，仅通过`ε`迁移能够到达的NFA的状态集合 |
  | `move(T, a)`   | 从`T`中包含的某个NFA的状态`s`出发，通过输入符号`a`迁移能够到达的NFA的状态集合 |

  令 Dstates 中仅包含ε-closure(s), 并设置状态为未标记;

  ```fortran
    while Dstates中包含未标记的状态T do
    begin
      标记T;
      for 各输入记号a do
      begin
        U := ε-closure(move(T, a));
        if U不在Dstates中 then
          将 U 追加到 Dstates 中，设置状态为未标记;
        Dtrans[T, a] := U;
      end
    end
  ```

  `ε-closure(T)`的计算方法如下：

  ```fortran
    将T中的所有状态入栈;
    设置ε-closure(T)的初始值为T;
    while 栈非空 do
    begin
      从栈顶取出元素t;
      for 从t出发以ε为边能够到达的各个状态u do
        if u不在ε-closure(T)中 then
        begin
          将u追加到ε-closure(T)中;
          将u入栈;
        end
    end
  ```



## 性质

算法1生成的NFA能够正确地识别正则表达式，并且具有如下的性质：

1. `N(r)`的状态数最多为`r`中出现的记号和运算符的个数的2倍。
2. `N(r)`的开始状态和结束状态有且只有一个。
3. `N(r)`的各个状态对于`Σ`中的一个符号，或者拥有一个状态迁移，或者拥有最多两个`ε`迁移。

## 测试

这里我们利用：https://cyberzhg.github.io/toolbox/nfa2dfa，来检验产生的dfa是否正确

- 测试`abc*`

![屏幕快照 2019-09-25 上午7.28.43](http://bonky-picture.oss-cn-beijing.aliyuncs.com/pic/pfz19.png)



![屏幕快照 2019-09-25 上午7.28.37](http://bonky-picture.oss-cn-beijing.aliyuncs.com/pic/bwd70.png)

- 测试 `((ab)*|b)*`

![屏幕快照 2019-09-25 上午7.31.47](http://bonky-picture.oss-cn-beijing.aliyuncs.com/pic/s7o6q.png)

![屏幕快照 2019-09-25 上午7.31.45](http://bonky-picture.oss-cn-beijing.aliyuncs.com/pic/pxuzk.png)

- 测试`abcdefghijk`

![屏幕快照 2019-09-25 上午7.33.10](http://bonky-picture.oss-cn-beijing.aliyuncs.com/pic/ii2tj.png)

![屏幕快照 2019-09-25 上午7.33.19](http://bonky-picture.oss-cn-beijing.aliyuncs.com/pic/nkekc.png)

## 总结

通过这次作业，不仅加深了我对课内知识的理解，同时也锻炼了我的代码能力，让我受益匪浅。

![屏幕快照 2019-09-25 上午7.34.57](http://bonky-picture.oss-cn-beijing.aliyuncs.com/pic/j1vfs.png)

