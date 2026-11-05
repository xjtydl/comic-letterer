# 两站已读方法与实施判断

记录日期：2026-11-05。这里保存已提炼的研究结论；完整发现目录与逐篇阅读状态仍以 inventory 为准。中文内容是归纳，不是教程全文。方法来源、我们的软件设计、尚未阅读的内容分开记录。

## Blambot Better Letterer 24 张图卡

[官方图卡总入口](https://blambot.com/pages/lettering-tips)。逐张源图 URL 见 inventory 的 B-TIP-001…024。24 张文字经 OCR 阅读；没有把 OCR 当作全部图例已经视觉比较。

| 图卡 | 保存的方法 | 适用边界／实现判断 |
|---|---|---|
| 001 | 英文带横杠 I 要结合词义和语境选择 | 英文传统，不套到中文；不能自动改冻结原文 |
| 002 | 调整特定字偶间距，检查字形造成的光学空隙 | 总体 tracking 不等于 pair kerning；须测量真实字形 |
| 003 | SFX 的形状与方向呼应实际声源和力线 | 字大、倾斜本身不能说明声音来源 |
| 004 | 检查尾巴实体交叉及视觉上暗示的交叉 | 几何不相交也可能读错人；整页实看不可省 |
| 005 | 对白排成紧凑、合理的文字团，留意长词 | 自动行长优化不理解词意；应允许人工断行 |
| 006 | 全页尾根宽度与笔触协调，避免针尖式细尾 | 需要角色/全书样式，不能仅用一个固定百分比 |
| 007 | 行距和泡内负空间共同决定轻重与可读性 | 空间不足优先重排/放大泡，不能机械缩字号 |
| 008 | 外语声音有明确的文字表达传统 | 按语言和书籍约定，不默认每种外语同一种字形 |
| 009 | 引号要结合连续叙述及对白身份处理 | 做建议与来源标记，不静默替换已审台词 |
| 010 | 斜体承担强调、声音与叙事角色 | 真实斜体字体不同于机械斜切；中文另作判断 |
| 011 | 省略号与中断破折号表达不同的声音过程 | 输入语义由作者决定；诊断器不擅自改写 |
| 012 | 个别行可以略调字宽以改善文字团 | 卡中94%是案例，不是强制全书比例；需重测 |
| 013 | 气泡叠放带来发言先后、节奏及空间感 | 层叠顺序应支持读序，不能只看几何是否允许 |
| 014 | 阅读路线、人物保护、图文融合是基础 | 避免气泡如贴纸；人物动作和声音同时构图 |
| 015 | 图层法与复合描边法是可编辑气泡的两类组织方式 | 独立程序可生成同样结果，不照搬某软件菜单 |
| 016 | 泡变大时保持锯齿/思想瓣的视觉密度 | 固定齿数任意拉伸不够；按周长与目标间距生成 |
| 017 | 同名义字号的不同字库，视觉大小仍可不同 | 用真实阅读尺寸/必要试印判断，不能仅比数字 |
| 018 | 识别字体结构与排版术语 | 用于标注、字形诊断与字体创作课程 |
| 019 | 自然气泡可轻微不对称 | 不把普通对白做成怪物轮廓；当前 organic 为原创实现 |
| 020 | OpenType 连字与上下文替代可增加自然变化 | 需要字体实际包含特性；假随机字符替换不是等价实现 |
| 021 | SFX 色彩与原画配色协调 | 保证声音可识别，并检查灰阶与不同背景 |
| 022 | 手写笔尖、笔画方向与辅助线影响结果 | 可建手写课程与过程记录；尚未实现笔触系统 |
| 023 | 排字前整理脚本和项目交接 | 对冻结台词只报告疑点；脚本修订与排版分开 |
| 024 | 小号浅字深底印刷可能需补偿 | 文中细描边数值是案例；目标印刷介质另核 |

## Comicraft 排字方法

| 来源 | 已读结论 | 当前程序决策／尚缺 |
|---|---|---|
| [Word Arrangement](https://balloontales.com/word-arrangement/) | 行长、词组、文字团和外壳一起调整 | 已有实际字体度量、人工断行及词组保护；语义断句未做 |
| [Bouncy Text](https://balloontales.com/bouncy-text/) | 小幅交替基线位移可表达唱歌、含混或稚嫩声音 | bounce/wave 与明确幅度、分组参数；不是所有对白默认跳动。波形是本程序扩展 |
| [Font and Character Usage](https://balloontales.com/font-and-character-usage/) | 字体特性、强调基线、字偶距和局部字宽要结合语境 | 加入片段 baseline_shift；OpenType/逐行宽度仍待补 |
| [Alternate Characters](https://balloontales.com/alternate-characters/) / [OpenType Ligatures](https://balloontales.com/opentype-ligatures/) | 字形替代可以避免过度机械重复 | 自然变化应克制；需要真实字体能力，不随机改正文 |
| [Making Word Balloons](https://balloontales.com/making-word-balloons/) | 先安排文字，再形成外壳和尾巴 | 可编辑 JSON/SVG、按文字拟合；不从泡大小倒逼删台词 |
| [The Layer Method](https://balloontales.com/the-layer-method/) | 外壳、尾巴和填色分层，使接缝被正确遮盖 | 已有底层描边、连接层、填色层、文字层 |
| [Creating Tails and Joins](https://balloontales.com/creating-tails-and-joins/) | 尾巴说明归属，连泡组织一段发言 | 独立根宽、长度、间隙、曲线，允许后泡认主；需实看交叉 |
| [Rough Balloons](https://balloontales.com/rough-balloons/) | 粗糙轮廓和尾巴应形成统一声线 | 已有 rough；原始软件滤镜参数不是程序必须复刻的接口 |
| [Sawtooth Balloons](https://balloontales.com/sawtooth-balloons/) | 锯齿、火焰可以靠轮廓节点与密度调整 | 精细可编辑锯齿/火焰、缩放密度仍待做 |
| [Dashed Iron Man Balloons](https://balloontales.com/dashed-iron-man-balloons/) | 多层轮廓及中间断笔构成设备化表达 | 机械分层虚线还未实现，不能把普通 whisper 当等价 |
| [Tattered Captions](https://balloontales.com/tattered-captions/) | 小幅粗糙、局部向内缺口及圆角连接表现破损边缘 | 当前用原创确定性路径；卷轴末端只在书籍引用中出现，未取得对应书页 |
| [Floating Text & Captions](https://balloontales.com/floating-text-captions/) | 无框字和不同旁白源须靠位置、字形和对比区分 | 已有 floating、时地/内心/叙述/编辑类型；装饰首字待做 |
| [‘Trapped Inside’ Balloon](https://balloontales.com/trapped-inside-balloon/) | 隐藏声源可指向遮住它的表面 | 已有 squink；锚点必须是实际发声位置而非猜测人物 |
| [Butting Balloons](https://balloontales.com/butting-balloons/) | 泡与格框贴边可节省空间并形成构图 | 只裁指定边，文字必须留在格内 |
| [Multiple Outline SFX](https://balloontales.com/multiple-outline-sfx/) / [Curved Type](https://balloontales.com/curved-type/) | 多描边、空心、曲线排字可改变声响形态 | 已有多描边/空心/逐字弧形；须在真实画稿上检验字腔，不能仅白底样张 |

## 从排字扩展到完整漫画

| 来源 | 已读结论及纳入内容 | 边界 |
|---|---|---|
| [The Making of a Comic Book Page](https://balloontales.com/the-making-of-a-comic-book-page-start-to-finish/) | 剧本、缩略草图、画稿、墨线、排字、色彩、校样与排版输出有前后依赖 | 要建制作状态和版本，不能只堆滤镜；个案不强制固定格数 |
| [Computer Color, Step by Step](https://balloontales.com/tutorial-computer-color-step-by-step/) | 线稿、平涂选择区、颜色与黑版分开处理 | 保存可重选区域；历史软件分色流程不能当现行规格 |
| [Seven Uses for Thought Balloons](https://balloontales.com/seven-uses-for-thought-balloons/) | 思想泡能承担悬念、预期、隐藏地点等信息组织作用 | 思想泡不是“过时所以禁用”，也不是把所有画外信息塞入泡 |
| [Character Study](https://balloontales.com/articles/tutorial/part1.html)、[Fighting Words](https://balloontales.com/articles/tutorial/part2.html)、[Title Deeds](https://balloontales.com/articles/tutorial/part3.html)、[Composition](https://balloontales.com/articles/tutorial/part4.html)、[Hand Lettering](https://balloontales.com/articles/tutorial/part5.html) | 字形、声音、标题、构图与手写各有表达目的 | 已读旧网页文字；没有把全部示例插图算作已检查 |
| [Eight Steps to Creating a Lettering Font](https://balloontales.com/eight-steps-to-creating-a-lettering-font/) | 手写采样、扫描/矢量化、字形、间距和字库制作要单独建能力 | 加载字体不等于能设计/导出字体 |
| [Angry Birds Logo](https://balloontales.com/how-i-created-the-angry-birds-logo/) | 字标需要草图方案、取舍及放回真实使用场景比较 | 将草图与最终选择过程纳入训练准备 |
| [Successful Logo Design](https://blambot.com/pages/successful-logo-design) | 字标应在尺寸、色彩/灰阶及不同背景中保持识别性 | 封面/Logo不等于放大对白字体 |
| [Black Parade](https://blambot.com/pages/the-language-of-the-black-parade) | 虚构语言与字体家族是专门设计任务 | 不据此自动复制其字母或制作整套中文字体 |
| [Aged Comic Cover](https://balloontales.com/aged-comic-cover/) / [Comic Book Look](https://balloontales.com/giving-artwork-the-comic-book-look/) | 做旧、网点、纹理属于后期材料处理 | 第二项保留旧轮正文记录；新全站清单中的逐图复核仍待补。纹理不替代叙事/造型 |
| [Gradients](https://balloontales.com/gradients-in-illustrator/) / [Shaded Fills](https://balloontales.com/shaded-fills-in-photoshop/) | 渐变、阴影填色有独立的层和遮罩处理 | 程序尚无完整渐变/材质系统 |
| [Pop-Up Letters](https://balloontales.com/tutorial-pop-up-letters/) | 是实际纸张折叠的立体字方法 | 保留为衍生设计实验，不误称数字3D挤出教程 |
| [Overprinting and Trapping](https://balloontales.com/overprinting-and-trapping-eps-lettering-files/) | 印前的叠印、陷印、黑版与输出要单独检查 | 当前屏幕PNG/SVG不代表通过印前验收 |
| [Business of Comics](https://balloontales.com/the-business-of-comics/) / [Printed Comics](https://balloontales.com/printed-comics/) / [Getting Started](https://balloontales.com/getting-started-in-the-industry/) | 协作、作品集、印刷发行和职业流程纳入D07 | 历史公司、费率和渠道必须重新核实后才能用于当前业务 |

## 商品、服务及尚未获取内容

- [Blambot 笔刷](https://blambot.com/collections/all-brushes)：已发现气泡 Vol.1、SFX Vol.1/Vol.2、Cockroacher 和 Perilous Pastel 五项。对应路径、音效笔触、磨损、粉彩；不等于已购买或安装。
- [Brush FAQ](https://blambot.com/pages/brush-faq)：记录描边角点/miter 与路径造成的轮廓问题；字体、笔刷、程序生成轮廓是不同资产。
- [字体许可](https://blambot.com/pages/licenses)、[笔刷许可](https://blambot.com/pages/blambot-brush-licenses)、[用途选项](https://blambot.com/pages/license-options)：使用、嵌入和分发须分别记录。本轮未找到明确 AI 训练许可，不能推定购买或网页公开就准许训练。
- Graphic Design、Logo Design、Comic Lettering、Custom Fonts 服务页主要是能力/作品展示，不冒充完整教程。Merch 的指南书进入参考书单，礼卡/账户/订阅页仅保留站务索引。
- Procreate 1–11 相关入口已在文章表登记；没有编造未找到的第12课。页面主题不等于看完视频。Blambot 频道未穷尽所有视频。
- Comicraft 书籍/在线课、Blambot 指南只读取公开介绍；付费正文未获取。访谈与仅图片文章的详细阅读状态见逐篇索引。

## 本项目提出的AI制作／训练体系（不是两站教程原话）

1. 推理时通过 Skill 检索方法；训练模型是另一个过程，不能混称。
2. 记录可观察的剧本意图、构图选择、工具操作、版本和修订理由，不要求内部私有思维链。
3. 样本优先来自原创或有明确授权的制作过程；保存失败→诊断→修订→实看结果。
4. 训练/验证按作品、角色和场景隔离；相邻格不能泄漏到不同集合冒充泛化。
5. 课程包括读序、空间、人物表演、连续性、线色、声音、标题、整页校样；不是只有气泡分类。
6. 自动规则、图像评价、叙事阅读和人的验收分开。功能存在、单测通过、单页漂亮都不能自动推定整本稳定。
7. 人体、透视、镜头与连续表演需要补专业来源，复用既有项目 Skill；不假称两站完整教授这些内容。
8. 目前没有训练任务和训练指标；45模块是范围和状态台账。

## v0.5实施更新（保留前文历史缺口以便追溯）

机械三层断续描边、锯齿/火焰弧长密度、卷轴旁白及首字绕排现已实现并通过《守灯人》中英文六格剧情自检；前文“仍待做”对应这些项目的状态由 [v0.5验证](../v05-validation.md) 覆盖。首字另核读 Blambot Grammar 的 Drop Caps / Decorative Caps 段：装饰首字是旁白的风格选择；实际2–4行字体测量与绕排是本程序实现。

完成这五项后新增D04全书元数据检查，依据明确项目样式规则执行，不把网站的风格建议变成普适强制标准。保留精确例外和原因、报出无匹配/过期例外，原页面不改写。
