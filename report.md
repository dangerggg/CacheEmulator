## Cache 算法设计、实现与比较实验报告

2020310822 曾军

### 实验总述

不同的 Cache 组织方式会影响其命中率和命中时间，为了减少直接映射 Cache 中某一块被频繁换入换出造成的冲突缺失，研究者提出了组关联 Cache。组关联 Cache 将直接映射组织方式中的一个偏移只对应一个 Cache 块改进为一个偏移对应一组 Cache 块，这大大减少了上述冲突缺失。然而缺失的减少是有代价的，多路组关联 Cache 的多组数据不能像直接映射那样在标签比较的同时上线，这增加了命中时间。因此有研究者提出了多种多样的路预测方法，旨在于降低组关联 Cache 的命中时间。路预测算法在标签比对的同时将预测的路上线，如果预测成功，组关联 Cache 的命中时间便几乎等同于直接映射方法，预测失败会有一定的惩罚，因此一个高效准确的路预测算法是非常必要的。为了加深对上述 Cache 替换算法的理解，本实验尝试编写一个 Cache 模拟器，用软件程序来模拟Cache 行为，并针对真实的测试用例给出其命中率。

### 实验环境

本实验使用 Python3 编写，本机版本为 `Python 3.8.5`，项目组织见下：

```bash
|---- emulator				# 模拟器包
|---- |---- __init__.py
|---- |---- cache.py
|---- |---- log.py
|---- main.py				# 主程序
|---- log
|---- |---- *.txt			# 缺失日志
|---- output.txt			# 程序输出
```

### 实验设计

1. 设计理念

   本实验采用**面向对象程序设计**的思路，即从定义最基本的 Cache 类开始，慢慢派生定义出如直接映射Cache、组关联 Cache、MRU 路预测和多列路预测 Cache 等不同组织方式的 Cache 类。这种方式在做到代码复用的同时降低了增加新的 Cache 种类的复杂度，下面就各类的设计和部分细节做简单展开。

2. 具体设计

   正如前一小节所说，本实验针对每一种 Cache 都实现了一个具体的类，类之间有继承关系，这种继承关系体现了其所属的大类，继承关系如下图所示：

   ```bash
   Cache ------------- DirectMap
   			|
   			------- SetAssoc ---------- MRUAssoc
   								  |
   								  ----- MCAssoc
   								  |
   								  ----- MCPAssoc
   
   MCAssoc: Multi-Column 
   MCPAssoc: Multi-Column Partial
   ```

   1. Cache 类

      该类定义了基本参数：容量，块大小，地址位宽，替换策略和写策略等，这些是任何一个 Cache 都应该具备的性质。另外所有针对 Cache 的访问都会涉及到地址的解码，模拟器需要根据地址拆分出偏移量和标签等信息，因此地址解码器也实现在最高的抽象层次中。可以看到，Cache 类是本实验中所有 Cache 种类的抽象，体现了 Cache 的基本性质。

   2. DirectMap 类

      该类继承自 Cache 类实现，是一种具体的组织方式。我们用一个列表来组织其内容，地址中的偏移量为下标，下标中的内容为标签（需要注意，只需模拟 Cache 行为，因此数据的存储不在考虑范围之内）。当一个地址访问请求到来时，首先对其解码，然后检查相应下标中的标签是否可以比对成功，若成功，则发生命中，若失败，则发生缺失并进行直接替换。

   3. SetAssoc 类

      该类继承自 Cache 类实现，组织方式和直接映射有所不同。我们用一个二维列表来组织其内容，地址中的偏移量为下标，下标中的内容为一个关联的 Cache 组形成的列表，第二维列表存储标签。解码地址访问请求之后，在下标对应的 Cache 组中查找是否有标签可以比对成功，若成功，则发生命中，组关联 Cache 此时需要**维护 LRU 队列**为之后的替换提供保证，若失败，则发生缺失，替换出 LRU 位置的 Cache 块。

      本实验使用队列维护 LRU 关系，默认队首为 LRU，队尾为 MRU。发生命中之后需要在队列中找到命中的Cache 编号并将其移到队尾，表示其为 MRU，发生缺失之后将队首元素弹出，表示该位置为应该替换出的 LRU，替换之后将该位置添到队尾，因为刚替换上来的元素是 MRU。

   4. MRUAssoc 类

      该类继承自 SetAssoc 类实现，因为其本质上是一种加了路预测的组关联 Cache。MRU 方法在本实验的实现中较为简单，因为组关联维护的 LRU 队列的队尾就是定义上的 MRU。解码地址访问之后，首先访问 LRU 队列队尾对应的元素，若命中，则为一次命中。若不命中，继续搜索下表对应的 Cache 组，若命中，则为非一次命中，若不命中，则发生了缺失，其处理方式基本等同于基本的组关联 Cache。

   5. MCAssoc 类

      该类继承自 SetAssoc 类实现，本质是组关联 Cache。多列 Cache 增加了位向量，并且引入了标签的后若干位将初次命中的问题转化为直接映射，其定义了主位置和选择位置的概念。主位置就是“直接映射”对应的 Cache 组中的元素，和直接映射不同的是，直接映射若缺失，则需要替换，多列预测方法在主位置比对失败之后去该主位置的选择位置中继续寻找。

      该预测方法最重要的概念就是主位置和选择位置之间的关系，首先是选择位置如何生成。经过分析不难看出，只有在发生“交换”操作时，才会有主位置的选择位置的生成，并且交换只会发生在非一次命中和缺失替换，下面逐一分析。（1）非一次命中。非一次命中时，主位置的标签比对失败，并且在选择位置中比对成功，为了保证主位置的 MRU 属性，需要进行交换操作，将命中的选择位置元素移到主位置，此时原来的选择位置属性没有改变，只是元素发生改变。（2）发生缺失。缺失时需要进行 Cache 的替换，仍然采用 LRU 策略，LRU 位置的元素被换出，同时进行交换操作保证主位置的 MRU 属性，这次替换为主位置新增了一个选择位置，即作为替换的 LRU 位置，该位置存储的是该次地址访问时的主位置元素。

      本实验依然使用列表来存储位向量，并在交换操作的同时更新主位置的位向量信息。解码地址访问之后，首先访问主位置，若主位置比对成功，则发生一次命中，若比对失败，多列 Cache 在选择位置之中寻找可能命中的 Cache 块，这缩小了搜索范围，因为之前存储在 Cache 组中的块要么在选择位置上，要么已经被替换出去。缺失的替换策略仍然是 LRU，只不过需要进行“交换”操作。

      关于位向量的更新，我采用了懒惰方式，即将当前主位置的其他主位置的选择位置移除时不处理位向量，用比对的失败来承担这部分开销。

   6. MCPAssoc 类

      该类同样继承自 SetAssoc 类实现。和多列 Cache 相比差别为选择位置只有一个，因此可以维护的 Cache 块也较少，非一次命中率相对多列 Cache 较低。这是用命中率的降低来交换维护的简便。其他操作和多列 Cache 基本相同。

### 实验结果

1. 命中率报告

   命中率信息已经转存成文件`output.txt`，该文件包含了所有要求的**命中率**和**搜索长度信息**，是程序输出的转存。

2. 相关问题

   （5）根据上述实验设计中的分析和介绍，MRU 预测方法最直接的好处就是简单并且省空间，并且不需要维护			选择位置的位向量。但是 MRU 的一次命中率相对 MC 要低（MC将一次命中转化成和直接映射等价），这会带来很多非一次命中的额外开销，同时 MC 方法使用位向量方法可以缩小非一次命中时的搜索空间。

   （6）命中率随着块大小的增大先上升后下降，分别为：98.2%，98.8%，99.3%，99.6%，99.7%，99.82%，99.81%。块大小的增大实际上是在解决容量缺失的问题，因为根据程序的局部性而言，越大的 Cache 块可以更好的利用程序的空间局部性。但当 Cache 块的大小达到一定程度时，Cache 的偏移量会大大减小，因为 Cache 总容量一定，这直接导致 Cache 的总行数较小，意味着**相对**较远的元素无法借助 Cache 被二次利用，因此 Cache 块大小存在着一个针对命中率的最优值。

### 实验收获

本次实验完成了一个 Cache 的模拟器，其实用软件模拟硬件还是有很多思考和认识上的差距，比如硬件的数据上线需要时间，多列 Cache 获取下一个选择位置却可以并行实现，这是软件无法体现的。这次实验让我对 Cache 有了更深刻的认识。