# 两站全范围 → 漫画创作程序与 Skill 总纲

日期：2026-11-05。用户明确：包含 Blambot 和 Comicraft / Balloon Tales 全部相关内容，覆盖构图、绘画、制作，不限字体和气泡；用于 AI 按人类创作流程制作漫画，以及未来训练 AI。

这是纳入范围与实施归属清单，不是完成声明。

## 发现范围与阅读证据

- Comicraft：公开 WordPress 索引的 94 篇文章全部登记，另登记 4 个页面与 6 个旧教程入口。94 是当前 posts 端点数量，不代表所有历史 URL 或站外内容。
- Blambot：canonical sitemap 的 31 个页面、15 个集合、313 个商品 URL 已登记；24 张 Better Letterer 图卡逐张 OCR 阅读文字，37 项语法标题登记。未声称完成全部配图视觉比较。商品条目归资产分类，不冒充教程。
- 逐篇阅读状态见 JSON；新查读包括成页全流程、上色、思想泡叙事、Logo、字体制作、特殊效果、笔刷与出版。
- 视频只登记页面、主题和入口，尚未完整观看；书籍／付费课程只读公开介绍，正文未取得；外部字体商店和 YouTube 全目录未穷尽。
- 完整 URL 索引见 [机器可读索引](two-site-inventory-20261105.json)，各能力字段见 [能力表 JSON](two-site-capabilities-20261105.json)。

## 两站全部菜单归属

| 网站／菜单 | 纳入内容 | 进入哪里 |
|---|---|---|
| Blambot Fonts | 全部／Design／Dialogue／Sound Effect／Packs／Indie／Pro、安装、推荐与定制 | 字体选择、字库、风格搭配、资产管理 |
| Blambot Brushes | 气泡、SFX、Cockroacher 磨损、Perilous Pastel；安装、FAQ | 笔触、矢量笔刷、纹理、角点故障处理 |
| Blambot Licences | 字体、笔刷及用途分类 | 来源与用途台账；不假定公开教程或购入字体已授权训练 |
| Blambot Services | 排字、定制字库、Graphic Design、Logo Design、委托流程 | 成页、平面构图、封面／署名／宣传设计、协作需求 |
| Blambot Articles | Better Letterer、语法、脚本、尺寸、手写史、Black Parade、视频；另由 sitemap 找到 Successful Logo Design 和 Top 10 Fonts | 构图、叙事、字形、文字、工序、案例与规则 |
| Blambot Merch | 指南书、签名版、徽章、礼卡 | 指南书入参考入口；商品设计入衍生设计；礼卡不算创作技能 |
| Blambot Contact／About／站务页 | 作者、联络、履历；账户和订阅等页面 | 来源身份与协作背景；站务保留索引，不变成绘画功能 |
| Comicraft Articles | 成页、上色、字体、标题、Logo、思想泡与大小写讨论、历史案例、纸艺立体字 | 创作工序、构图、色彩、字体、设计、审美与扩展实验 |
| Comicraft Tips / Lettering | 所有气泡、尾巴、字形、拟声、浮动字、图层、Procreate 等 | 程序操作＋专项 Skill |
| Comicraft Tips / Production | 扫描、格式、印刷、合成、分色、旧封面、网点 | 绘画后期与交付模块 |
| Comicraft Tips / Publishing | 入行、业务、自出版、发行推广 | 协作与出版 Skill；旧信息需要更新 |
| Comicraft Interviews | 24 篇访谈记录 | 案例、方法选择、创作过程与职业判断 |
| Comicraft Glossary | 空间、节奏、字形、标题、场景字、遮挡等术语 | 能力与标注词汇表 |
| Comicraft Book／Online course／Fonts | 书籍、Illustrator 课程、字库外链 | 教材与工具入口；未读取内容保持待研 |

## 能力总表

来源前缀：B 为 Blambot，C 为 Comicraft 当前文章 ID，CL 为旧系列，CP 为页面。EXT 是完整绘画目标需要另补的来源；PROJECT-ai 是我们提出的系统设计，不能归称两站提供了 AI 训练方案。

| ID | 能力 | 全部纳入的内容 | 程序责任 | Skill 归属 | 当前状态 |
|---|---|---|---|---|---|
| A01 | 整本制作与工序 | 剧本→缩略草图→铅笔／墨线→排字与上色→校样→交付 | 工序状态、版本、依赖与资产追溯 | comic-production-entry | 已有制作入口；独立程序尚未接通整本工序 |
| A02 | 剧本与文字交接 | 页格编号、角色、动作说明、台词、参考链接、旁白、拟声、强调 | 富文本导入、冻结原文、稳定 ID | comic-production-entry / comic-lettering | 已有 JSON 与原文冻结；富文本导入待做 |
| A03 | 叙事与阅读时间 | 思想与独白的用途、悬念、反差、信息揭示、停顿与对白节奏 | 叙事意图字段、读序图、对照方案 | american-comic-layout / comic-visual-language | 已有原则；系统案例与评测待补 |
| A04 | 缩略草图与方案探索 | 整页缩略草图、多个构图方案、保留修改过程 | 缩略稿画板、方案比较与版本 | american-comic-layout | 已有 Skill 方法；独立程序未实现 |
| A05 | 整页构图与分格 | 格框、留白、主次、阅读路线、跨格、跨页与翻页节奏 | 布局编辑与阅读路线检测 | american-comic-layout | 已有 Skill；程序仅显式分格与初步读序检查 |
| A06 | 单格构图与图文协同 | 人物、动作、背景、负空间、对白与 SFX 共同构图；避免贴纸感 | 构图区域、焦点／保护区与候选布局 | american-comic-layout / comic-visual-language | 保护区与摆位已有；v0.7中英文600px整页改版实际修复溢出、遮字与歌唱短尾；自动画面理解待补 |
| A07 | 连续动作与镜头 | 景别、角度、轴线、方向、动作因果、相邻格时间关系 | 相邻格状态与空间检查 | comic-continuity-acting / cinematography | 项目已有方法；两站不能提供完整课程，另补来源 |
| A08 | 人物表演与造型 | 人体、重心、手势、表情、视线、动作剪影 | 身份／表演参考管理与局部诊断 | comic-continuity-acting / comic-visual-language | 项目有方法；绘画课程与系统训练集待补 |
| A09 | 角色与道具连续性 | 身份、服装、比例、道具状态、多人一致性 | 角色／道具资产版本与检查 | comic-continuity-acting | 项目已有参考流程；不是 Letterer v0.3 能力 |
| A10 | 场景、透视与空间 | 场景布局、透视、机位、遮挡、光源、必要白模 | 原画关联、空间导图与状态约束 | comic-production-entry / comic-continuity-acting | 项目已有原画先行和白模规则；基础透视另补来源 |
| A11 | 铅笔、墨线与笔触 | 草稿清稿、墨线层级、黑白形状、笔锋及干湿笔触 | 分层画稿、路径和笔刷接口 | comic-visual-language | Skill 有线面原则；绘画引擎与完整训练待补 |
| A12 | 平涂与区域蒙版 | 线稿与颜色分离、平涂区域、选择蒙版、保留高分辨率线稿 | 区域 ID、平涂层与可重选蒙版 | comic-visual-language | 尚未在独立程序实现 |
| A13 | 光影、色彩与明度 | 上色、阴影、色板、图文对比、灰阶与多背景检查 | 色板与对比检查、渐变及着色层 | comic-visual-language | 已有固定填色；配色系统与绘画光影课程待补 |
| A14 | 材质与复古漫画外观 | 网点、纸张老化、折痕、磨损、混合模式 | 独立纹理层、强度与媒介预览 | comic-visual-language | 未实现 |
| B01 | 文字形状与适配 | 断行、词组、长词、行距、字距、负空间、局部字宽 | 字体度量、断行与轮廓适配 | comic-lettering / comic-letterer | 语义词组由AI/排字者选择并保护；新增逐行宽度/比例和标点断句建议，两页中英文剧情已验证；通用自动语义理解未声称实现 |
| B02 | 真实字体与高级排版 | 粗斜体、字偶距、基线、OpenType、替代字形、跨行强调 | 字形塑形、每行／片段基线及字体特性 | comic-lettering / comic-letterer | 真实字体、基线、OpenType度量/渲染及替代字形、逐行字宽已实现；中文/英文实页验证，复杂脚本/竖排仍不支持 |
| B03 | 语言与漫画标点 | 37 项语法传统；外语、数字、引号、拖音、中断、注释、审查符号 | 按语言和书籍样式检查；保留原文、修改另列建议 | comic-lettering | 新增按语言的只读标点/引号/I建议和剧情语法工作流；不自动改文，37项传统保留上下文人工/AI判断 |
| B04 | 气泡形状与自然度 | 椭圆、TV、自然不对称、爆炸、锯齿、火焰、平边；齿距保持 | 可编辑路径、可缩放样式与轮廓密度 | comic-letterer / comic-visual-language | 新增圆角平边、可拖控制点的闭合曲线及实际尾根/留白检查，剧院标题和耳语实页验证；病态路径不作精确几何保证 |
| B05 | 特殊声音体系 | 思想、弱声、耳语、设备、怪物、心灵、喘息、歌唱、机械虚线 | 声线形状、装饰及匹配文字表现 | comic-visual-language / comic-letterer | 两页剧院补证咳嗽、心灵、思想、耳语、弱声、歌唱；修复标记不可见，守灯人另验证双轮廓；机械和粗糙声沿用既有实页 |
| B06 | 尾巴与声源 | 嘴／头／设备、根宽、长度、间隙、曲线、隐藏声源、画外 | 尾巴编辑、认主与交叉检查 | comic-letterer / comic-lettering | 实际尾根/认主/间隙已有实页；自定义路径新增射线交点；跨页样式核对进入D04 |
| B07 | 连泡、插话与层叠 | 连贯发言、连接桥、打断、叠放顺序、人物前后层次 | 显式连接关系、叠放模式、读序验证 | comic-lettering / comic-letterer | 连泡/插话沿用既有剧情证据；新增显式前后叠放、独立完整壳层与遮字拒绝，剧院思想后耳语实页验证 |
| B08 | 旁白与装饰框 | 时地、内心、说话、编辑、无框旁白、首字、破损／卷轴框 | 旁白语义、首字排版、装饰轮廓 | comic-letterer / comic-visual-language | 旁白类型、浮动字、破损/卷轴、首字已有实页；新增平边/手修旁白在连续剧院页面验证 |
| B09 | 边框、遮挡与空间层次 | 贴边、跨边、前景遮罩、避免气泡成为错误实体、相切 | 裁切与遮罩、墨线相切检查、图层顺序 | comic-letterer / comic-lettering | 前景蒙版、贴边沿用既有证据；新增显式跨边壳且文字仍留在格内，剧院结尾实页验证；自动图像分割仍未实现 |
| B10 | 拟声字的叙事设计 | 声音来源、力度、节奏、材质、方向与力线 | 声音元数据、字形布局与源点 | comic-visual-language | 新增声音事件/源点/材质/力度/持续性元数据；琴声根据剧情修轻，与既有撞击形成对照；大规模声音语料未建立 |
| B11 | 拟声字造型与渲染 | 手绘、字体变形、逐字、空心、多描边、阴影、透视、渐变、磨损 | 字形编辑、透视与材质、路径布尔运算 | comic-letterer / comic-visual-language | 新增四角透视字形路径、双色渐变和有限可复现磨损，门牌/琴声实页验证；任意布尔编辑/复杂塑形非本工具能力 |
| B12 | 字体创作与虚构文字 | 手写采样、矢量化、字形结构、基准线、字偶距、家族、虚构字母 | 字形编辑与字体导出、字库来源 | comic-visual-language（新增字体创作参考） | 新增原创笔触字形到TTF、字偶距与ss01；HOME小字库实际用于剧院门牌；不宣称完整中文/拉丁字族已制作 |
| B13 | 手写工具与自然变化 | 笔尖、方向、Ames 辅助线、有限变化、保留活力 | 笔触／轨迹记录、替代字形与自然路径 | comic-visual-language | 笔触坐标/压力/方向保留，生成有限变化轮廓并实际制成门牌；完整数位板应用/自动手写识别仍未实现 |
| C01 | 标题页与署名构图 | 标题与故事气质、主次词、画面融合、署名、装饰首字 | 标题画板、文字形状与署名模块 | american-comic-layout / comic-visual-language | 没有专用系统，基础字形操作可复用 |
| C02 | 封面与 Logo | 轮廓识别、草图方案、字形重叠、远读、小图、黑白和多背景 | Logo／封面编辑及多尺寸对照 | comic-visual-language / american-comic-layout | 尚无专门能力与验收样本 |
| C03 | 场景内文字 | 路牌、报纸、屏幕、信件、容器标签、建筑文字 | 表面锚点、透视和材质合成 | comic-visual-language / comic-lettering | 普通文字可放；表面透视未做 |
| C04 | 出版与衍生平面设计 | 扉页、目录、署名页、宣传图、衣服／海报等载体 | 多尺寸画板、版式模板与输出 | comic-visual-language（平面设计参考） | 未做；服务案例只有展示，不等于完整教学 |
| D01 | 字体笔刷资产 | 设计／对白／SFX 字体；气泡／SFX／磨损／粉彩笔刷；安装和角点故障 | 资产清单、外部资源加载、笔刷和描边参数 | comic-lettering / comic-visual-language | 字体加载已有；笔刷系统未做 |
| D02 | 软件工具操作 | Illustrator／Photoshop／Procreate／排版软件；页面、字体、尾巴、效果、遮罩 | 操作接口与可回放工具调用 | comic-production-entry / comic-letterer | 独立编辑器已有；外部工具适配与完整课程待补 |
| D03 | 校样、修改与本地化 | 读稿、全页校样、局部纠错、翻译后重排、不损坏原画 | 差异、修订、撤销重做与语言版本 | comic-production-entry / comic-letterer | 保存重载／导出／冻结已有；整本校样和翻译工作流待补 |
| D04 | 全书一致性 | 角色声线、字体、尾根、描边、齿距、色板与版本 | 全书样式库、依赖更新、例外记录 | comic-production-entry / comic-visual-language | 规则/例外、字体哈希与逐页校样已有；v0.7新增带来源/前值保护的显式批量修订和完整前后对照，四页600px剧情验证；多人协作与自动验收未实现 |
| D05 | 文件、扫描与数字交付 | 扫描线稿、分辨率、位图／矢量、可编辑母版、低清校样和高清合成 | 文件导入、分辨率检查、多格式导出 | comic-lettering / comic-production-entry | JSON／SVG／PNG 已有；扫描与 PDF 等未做 |
| D06 | 印前与成品尺寸 | 原稿尺寸、出血、裁切、安全区、分色、黑版、叠印、陷印、浅字增益 | 印前预检、色彩配置与输出配置 | comic-lettering（印前参考） | 未实现完整印前；历史参数须按当前介质重核 |
| D07 | 出版、协作与职业流程 | 作品集、编辑反馈、职责、排期、报价、署名、印刷发行推广 | 项目计划、交付单、署名与预算数据 | comic-production-entry（出版协作参考） | 未实现；历史公司／费率不能当现行标准 |
| D08 | 历史、审美与案例批评 | 大小写争论、思想泡选择、手写／数字、作品复盘、访谈经验 | 案例索引与比较展示 | comic-visual-language / comic-production-entry | 已有少量原则；全部文章尚需逐篇提炼 |
| D09 | 来源、授权与使用方式 | 字体／笔刷使用、嵌入、商业范围；教程与训练资料分别记账 | 来源、许可证、允许用途和素材版本 | comic-production-entry | 目前不附带商业字体；完整资产授权台账待做 |
| E01 | 可检索知识库 | 索引→核读→方法→适用条件／反例→程序／Skill→实图证据 | 来源版本与能力台账 | 沿用入口及专项 Skill | 本轮建立全站发现索引；未声称全内容掌握 |
| E02 | 模仿人类的制作过程记录 | 输入、意图、操作、前后图、失败诊断、修订与验收 | 工具轨迹、图层／矢量状态及阶段资产记录 | comic-production-entry | v0.7保存显式目的、35项修改、10项规则变更、前后漫画和失败修订；是单个原创案例过程记录，非完整训练语料 |
| E03 | 练习课程与反例 | 从局部到单格、连续页、整章；同剧情多方案和纠错 | 任务集、难度、失败类别、评审表 | 现有专项 Skill 加训练参考 | 本轮规划；未训练新模型 |
| E04 | AI 训练与数据 | 原创／授权样本；分镜、构图、动作、线稿、平涂、文字图层与修订配对 | 数据集版本、按作品切分、训练适配接口 | 新增训练规范应独立于制作 Skill | 待建；模型与训练方式依据目标另选，未启动训练 |
| E05 | 评测与回归 | 故事可读性、构图、身份／空间连续性、声源、文字正确性、印刷表现 | 客观检查＋盲评＋跨页回归；与不使用 Skill 基线比较 | 现有制作验收扩展 | 175项Letterer测试及多部剧情实页；新增四页600px修订、陈旧输入/冻结文字/规则/例外保护回归；全绘画评测和AI训练未建立 |

## 人类流程与 AI 训练的对应

制作目标是：理解剧本→分析已批准参考→缩略方案→整页／单格构图→人物与空间表演→线稿／上色→文字与声音→校样修订→交付。使用端到端生图、分层绘图或混合方式，应按任务选择；不把模拟每一笔作为唯一实现方式。

技能检索是运行时指导，不等于训练模型。训练准备要保存输入、叙事意图、可观察的选择理由、工具操作、前后状态和评价；不要求记录模型私有思维链。已批准原画、台词和身份约束随样本保留。

数据首选原创或明确授权的过程样本；教程只提炼方法和来源，商品字体、商业笔刷和第三方漫画页不自动进入训练集。测试按作品／角色／场景分组，防止相邻格同时出现在训练和测试中。

课程任务需要包含：构图选择、读序修复、姿态／场景连续性、线稿与平涂、声音表现、标题页、成页纠错；每类有成功、失败及修订案例。评测同时检查叙事、构图、文字与实际阅读效果。87 项排字测试不能代表这些能力已通过。

两站并非系统人体、透视、镜头与动作课程：这些能力仍列入 A07–A11，复用现有制作 Skill 并补专业来源，不编造网站依据。

## 内容吸收与完成标准

每项按“索引→读正文／看图／看视频→提炼适用条件与反例→程序实现或 Skill 方法→完整漫画验证”记录。本文只完成范围归档与部分核读。用户2026-11-05指定顺序：先补完气泡与文字，并用完整剧情漫画验证；之后继续构图、画稿工序、色彩、整本流程和AI训练。最新实施证据见 [流水账](IMPLEMENTATION_LEDGER.md)，接续先读 [工作入口](../WORK_INDEX.md)。

历史软件菜单、分辨率、印刷参数、费率和发行信息仅作历史方法；实际使用须按当前软件和交付条件复核。

## Blambot 24 张图卡

| ID | 方法主题 | 阅读状态 |
|---|---|---|
| [B-TIP-001](https://cdn.shopify.com/s/files/1/0152/5779/6662/files/bl001_20322a29-29ff-46de-8c8d-6900ec9a8817_800x800.jpg?v=1723484600) | 英文横杠 I 与上下文选择 | OCR 文本已读；配图视觉比较待补 |
| [B-TIP-002](https://cdn.shopify.com/s/files/1/0152/5779/6662/files/bl002_1000x1000.jpg?v=1613697838) | 字偶间距 Kerning | OCR 文本已读；配图视觉比较待补 |
| [B-TIP-003](https://cdn.shopify.com/s/files/1/0152/5779/6662/files/bl003_1200x1200.jpg?v=1613697838) | 拟声字从声音源与力线构图 | OCR 文本已读；配图视觉比较待补 |
| [B-TIP-004](https://cdn.shopify.com/s/files/1/0152/5779/6662/files/bl004_5b1c5103-7b5e-447b-8df2-ed88cf593b2c_1200x1200.jpg?v=1723732413) | 尾巴交叉与隐含交叉 | OCR 文本已读；配图视觉比较待补 |
| [B-TIP-005](https://cdn.shopify.com/s/files/1/0152/5779/6662/files/bl005_1200x1200.jpg?v=1613697838) | 文字堆叠与长词布局 | OCR 文本已读；配图视觉比较待补 |
| [B-TIP-006](https://cdn.shopify.com/s/files/1/0152/5779/6662/files/bl006_dad23de0-cc02-44a3-9a2a-125621428ca3_1200x1200.jpg?v=1724087239) | 全页尾根宽度一致、防针尖尾 | OCR 文本已读；配图视觉比较待补 |
| [B-TIP-007](https://cdn.shopify.com/s/files/1/0152/5779/6662/files/bl007_6bdc7889-5253-439f-8767-b058e719f600_1200x1200.jpg?v=1724174065) | 行距与气泡负空间 | OCR 文本已读；配图视觉比较待补 |
| [B-TIP-008](https://cdn.shopify.com/s/files/1/0152/5779/6662/files/bl008_65c553bd-83b0-4ac8-9f52-2408e0d21393_1000x1000.jpg?v=1724252381) | 外语对白与特殊字形 | OCR 文本已读；配图视觉比较待补 |
| [B-TIP-009](https://cdn.shopify.com/s/files/1/0152/5779/6662/files/bl009_9ec084c7-dbb2-4781-a018-713b5f76e0a2_1200x1200.jpg?v=1724338062) | 对白和连续旁白的引号 | OCR 文本已读；配图视觉比较待补 |
| [B-TIP-010](https://cdn.shopify.com/s/files/1/0152/5779/6662/files/bl010_027df8ab-366c-4e35-8c30-5e1fd4bf0fae_1000x1000.jpg?v=1724418961) | 斜体的叙事用途 | OCR 文本已读；配图视觉比较待补 |
| [B-TIP-011](https://cdn.shopify.com/s/files/1/0152/5779/6662/files/bl011_a6b47b47-f689-4176-b97c-7b85e5b2c873_800x800.jpg?v=1724691013) | 拖音与中断标点 | OCR 文本已读；配图视觉比较待补 |
| [B-TIP-012](https://cdn.shopify.com/s/files/1/0152/5779/6662/files/bl012_c9779c21-2e34-44e7-882d-e26480ae6950_800x800.jpg?v=1724768546) | 局部行宽压缩 | OCR 文本已读；配图视觉比较待补 |
| [B-TIP-013](https://cdn.shopify.com/s/files/1/0152/5779/6662/files/bl013_8df524db-d27e-4334-96cb-c318a473f5f3_800x800.jpg?v=1724860421) | 对话气泡叠放与节奏／景深 | OCR 文本已读；配图视觉比较待补 |
| [B-TIP-014](https://cdn.shopify.com/s/files/1/0152/5779/6662/files/bl014_45c9d01c-93f2-4d66-b7f6-db7d5e43f200_800x800.jpg?v=1724940045) | 阅读顺序、保护人物、图文统一 | OCR 文本已读；配图视觉比较待补 |
| [B-TIP-015](https://cdn.shopify.com/s/files/1/0152/5779/6662/files/bl015_57c02468-c56c-4465-b9e8-2354d65ae5f8_1200x1200.jpg?v=1725029175) | 图层法与复合描边法 | OCR 文本已读；配图视觉比较待补 |
| [B-TIP-016](https://cdn.shopify.com/s/files/1/0152/5779/6662/files/bl016_9a98f0c7-0722-48d9-87b3-b2f58af228c8_800x800.jpg?v=1725371538) | 设备声尖齿／思想泡瓣随尺寸保持一致 | OCR 文本已读；配图视觉比较待补 |
| [B-TIP-017](https://cdn.shopify.com/s/files/1/0152/5779/6662/files/bl017_5b9ffa8a-c8d2-46d3-8289-ecef7a4f9342_1200x1200.jpg?v=1725457078) | 字号的视觉差异与实尺寸试印 | OCR 文本已读；配图视觉比较待补 |
| [B-TIP-018](https://cdn.shopify.com/s/files/1/0152/5779/6662/files/bl018_800x800.jpg?v=1613745639) | 字形结构术语 | OCR 文本已读；配图视觉比较待补 |
| [B-TIP-019](https://cdn.shopify.com/s/files/1/0152/5779/6662/files/bl019_1200x1200.jpg?v=1615305833) | 自然不对称气泡 | OCR 文本已读；配图视觉比较待补 |
| [B-TIP-020](https://cdn.shopify.com/s/files/1/0152/5779/6662/files/bl020_1321d6f4-b153-4d9e-9859-13e220410fd7_800x800.jpg?v=1725632218) | OpenType 连字与上下文替代 | OCR 文本已读；配图视觉比较待补 |
| [B-TIP-021](https://cdn.shopify.com/s/files/1/0152/5779/6662/files/bl021_1200x1200.jpg?v=1673975806) | 拟声字色板与画面配色 | OCR 文本已读；配图视觉比较待补 |
| [B-TIP-022](https://cdn.shopify.com/s/files/1/0152/5779/6662/files/bl022_1600x1600.jpg?v=1691592407) | 手写笔尖与笔画方向 | OCR 文本已读；配图视觉比较待补 |
| [B-TIP-023](https://cdn.shopify.com/s/files/1/0152/5779/6662/files/bl023_e9b52159-aff2-4bb0-b95e-8763a64ac2be_800x800.jpg?v=1726149897) | 排字前的脚本整理 | OCR 文本已读；配图视觉比较待补 |
| [B-TIP-024](https://cdn.shopify.com/s/files/1/0152/5779/6662/files/bl024_1200x1200.jpg?v=1728321324) | 浅字深底的小字印刷增益 | OCR 文本已读；配图视觉比较待补 |

## Blambot 37 项语法主题

Asterisks；Balloon Tails；Bold Italic；Breaking Borders；Breath Marks (AKA, Whiskers, Fireflies, Crow's Feet)；Burst Balloons (AKA, Shout Balloons)；Butting Balloons (AKA, Anchoring, Top-lining, Side-lining)；Captions；Crossbar "I"；Double Dash；Double Outline Balloons；Drop Caps / Decorative Caps；Ellipses；Foreign Languages；Hollow Sound Effects；Hyphenating；Italic；Joining Balloon-to-Balloon；Joining Balloons with Connectors；Music / Singing；Numbers；Off-Panel Dialogue；Overlapping Panel Borders；Question Mark / Exclamation Point；Quotation Marks；Radio Balloons (AKA, Electric Balloons, Broadcast Balloons)；Roach Chew；Rough Balloons；Sentence Spacing；Small Dialogue / Big Balloon；Sound Effects (and Sound Effects Punctuation)；Squink；Tangents；Telepathic Balloons；Thought Balloons；Wavy Balloons；Whispering。

## Comicraft 全部 94 篇当前文章

| ID | 文章 | 类别 | 能力归属 | 阅读状态 |
|---|---|---|---|---|
| C793 | [Lettering in Procreate #11 – Masking Balloons & Objects](https://balloontales.com/lettering-in-procreate-11-masking-balloons-objects/) | Lettering, Tips | D02 | page/topic indexed; full video not watched |
| C789 | [Lettering in Procreate #10 – oval & jagged burst balloons](https://balloontales.com/lettering-in-procreate-10-oval-jagged-burst-balloons/) | Lettering, Tips | D02 | page/topic indexed; full video not watched |
| C786 | [Lettering in Procreate #9 – flat-edged “evil” balloons](https://balloontales.com/lettering-in-procreate-9-flat-edged-evil-balloons/) | Lettering, Tips | B04, D02 | page/topic indexed; full video not watched |
| C782 | [Lettering in Procreate #8 – creating pen-drawn FX](https://balloontales.com/lettering-in-procreate-8-creating-pen-drawn-fx/) | Lettering, Tips | B10, D02 | page/topic indexed; full video not watched |
| C778 | [Lettering in Procreate #7 – Easy outline, shadow & color FX](https://balloontales.com/lettering-in-procreate-7-easy-outline-shadow-color-fx/) | Lettering, Tips | B11, D02 | page/topic indexed; full video not watched |
| C771 | [Lettering in Procreate #6 – creating FX with type](https://balloontales.com/lettering-in-procreate-6-creating-fx-with-type/) | Lettering | B11, D02 | page/topic indexed; full video not watched |
| C774 | [Creating Authentic Comic Pages – John on the Adobe Fonts Show](https://balloontales.com/creating-authentic-comic-pages-john-on-the-adobe-fonts-show/) | Lettering, Production, Tips | A14 | page/topic indexed; full video not watched |
| C767 | [Lettering in Procreate #5 – drawing tails](https://balloontales.com/lettering-in-procreate-5-drawing-tails/) | Lettering | D02 | page/topic indexed; full video not watched |
| C764 | [Lettering in Procreate #4 – drawing word balloons](https://balloontales.com/lettering-in-procreate-4-drawing-word-balloons/) | Lettering | D02 | page/topic indexed; full video not watched |
| C759 | [Lettering in Procreate #3 – word arrangement](https://balloontales.com/lettering-in-procreate-3-word-arrangement/) | Lettering | D02 | page/topic indexed; full video not watched |
| C757 | [Lettering in Procreate #2 – text import & point size](https://balloontales.com/lettering-in-procreate-2-text-import-point-size/) | Lettering | D02 | page/topic indexed; full video not watched |
| C748 | [Lettering in Procreate #1 – page setup & loading fonts](https://balloontales.com/lettering-in-procreate-1-page-setup-loading-fonts/) | Lettering | D02 | page/topic indexed; full video not watched |
| C729 | [Why the Crossbar I Rule?](https://balloontales.com/why-the-crossbar-i-rule/) | Lettering | B03 | title/category indexed; detailed review pending |
| C528 | [Extensis interview](https://balloontales.com/extensis-interview/) | Interviews | D08 | title/category indexed; detailed review pending |
| C525 | [MyFonts “Creative Characters” interview](https://balloontales.com/myfonts-creative-characters-interview/) | Interviews | D08 | title/category indexed; detailed review pending |
| C532 | [Vox.com: Where the ‘comic book font’ came from](https://balloontales.com/vox-com-where-the-comic-book-font-came-from/) | Articles | D08 | page/topic indexed; full video not watched |
| C541 | [Lettering Dos and Don’ts for Comixology](https://balloontales.com/lettering-dos-and-donts/) | Lettering, Tips | D03 | public text reviewed; image/video review may remain |
| C502 | [The Making of a Comic Book Page, Start to Finish](https://balloontales.com/the-making-of-a-comic-book-page-start-to-finish/) | Articles | A01, A04, A05, A11, C03, D03 | public text reviewed; image/video review may remain |
| C478 | [How I created the Angry Birds Logo](https://balloontales.com/how-i-created-the-angry-birds-logo/) | Articles | A04, C02 | public text reviewed; image/video review may remain |
| C579 | [“Why is lettering an invisible art?”](https://balloontales.com/why-is-lettering-an-invisible-art/) | Interviews | D08 | title/category indexed; detailed review pending |
| C577 | [“What makes a good logo?”](https://balloontales.com/what-makes-a-good-logo/) | Interviews | D08 | title/category indexed; detailed review pending |
| C575 | [“Why did you create Hip Flask?”](https://balloontales.com/why-did-you-create-hip-flask/) | Interviews | D08 | title/category indexed; detailed review pending |
| C573 | [“Who are your favorite creators and collaborators?”](https://balloontales.com/who-are-your-favorite-creators-and-collaborators/) | Interviews | D08 | title/category indexed; detailed review pending |
| C571 | [“How do you kern an all-uppercase font?”](https://balloontales.com/how-do-you-kern-an-all-uppercase-font/) | Interviews | D08 | title/category indexed; detailed review pending |
| C569 | [“What’s the secret to great comic book lettering?”](https://balloontales.com/whats-the-secret-to-great-comic-book-lettering/) | Interviews | D08 | title/category indexed; detailed review pending |
| C567 | [Thoughts on Thought Balloons!](https://balloontales.com/thoughts-on-thought-balloons/) | Interviews | D08 | title/category indexed; detailed review pending |
| C565 | [“Where do you get ideas for new fonts?”](https://balloontales.com/where-do-you-get-ideas-for-new-fonts/) | Interviews | D08 | title/category indexed; detailed review pending |
| C563 | [“What is the difference between pen and computer lettering?”](https://balloontales.com/what-is-the-difference-between-pen-and-computer-lettering/) | Interviews | D08 | title/category indexed; detailed review pending |
| C561 | [“What question are you asked most often”](https://balloontales.com/what-question-are-you-asked-most-often/) | Interviews | D08 | title/category indexed; detailed review pending |
| C559 | [“How do you design a logo?”](https://balloontales.com/how-do-you-design-a-logo/) | Interviews | D08 | title/category indexed; detailed review pending |
| C557 | [“What do you like most about comic book lettering?”](https://balloontales.com/what-do-you-like-most-about-comic-book-lettering/) | Interviews | D08 | title/category indexed; detailed review pending |
| C420 | [Tutorial: Font Creation](https://balloontales.com/tutorial-font-creation/) | Articles | B12 | page/topic indexed; full video not watched |
| C427 | [Has the rise of technology ruined the craft of typography?](https://balloontales.com/has-the-rise-of-technology-ruined-the-craft-of-typography/) | Interviews | D08 | title/category indexed; detailed review pending |
| C410 | [Interview with artist R. Sikoryak](https://balloontales.com/interview-with-artist-r-sikoryak/) | Interviews | D08 | title/category indexed; detailed review pending |
| C415 | [Tutorial: Creating the Moritat font](https://balloontales.com/tutorial-creating-the-moritat-font/) | Articles | B12 | page/topic indexed; full video not watched |
| C386 | [Aged Comic Cover](https://balloontales.com/aged-comic-cover/) | Production, Tips | A14 | public text reviewed; image/video review may remain |
| C385 | [Seven Uses for Thought Balloons](https://balloontales.com/seven-uses-for-thought-balloons/) | Lettering, Tips | A03 | public text reviewed; image/video review may remain |
| C384 | [Creating Thought Balloons](https://balloontales.com/creating-thought-balloons/) | Lettering, Tips | B05 | title/category indexed; detailed review pending |
| C376 | [Opentype Ligatures](https://balloontales.com/opentype-ligatures/) | Lettering, Tips | B02 | public text reviewed; image/video review may remain |
| C430 | [Heroes Comics](https://balloontales.com/heroes-comics/) | Interviews | D08 | title/category indexed; detailed review pending |
| C377 | [Getting Started in the Industry](https://balloontales.com/getting-started-in-the-industry/) | Publishing, Tips | D07 | public text reviewed; image/video review may remain |
| C392 | [Gradients in Illustrator](https://balloontales.com/gradients-in-illustrator/) | Lettering, Tips | A13 | public text reviewed; image/video review may remain |
| C425 | [Establishing a Career in Comics](https://balloontales.com/establishing-a-career-in-comics/) | Interviews | D07 | title/category indexed; detailed review pending |
| C402 | [Rough Balloons](https://balloontales.com/rough-balloons/) | Lettering, Tips | B05 | text reviewed in earlier implementation research |
| C401 | [Bouncy Text](https://balloontales.com/bouncy-text/) | Lettering, Tips | B02, B05 | public text reviewed; image/video review may remain |
| C389 | [Shaded fills in Photoshop](https://balloontales.com/shaded-fills-in-photoshop/) | Production, Tips | A13, B11 | public text reviewed; image/video review may remain |
| C423 | [Origins of Digital Lettering](https://balloontales.com/origins-of-digital-lettering/) | Interviews | D08 | title/category indexed; detailed review pending |
| C394 | [Sawtooth Balloons](https://balloontales.com/sawtooth-balloons/) | Lettering, Tips | B04, D04 | public text reviewed; image/video review may remain |
| C378 | [Word Arrangement](https://balloontales.com/word-arrangement/) | Lettering, Tips | B01 | text reviewed in earlier implementation research |
| C400 | [Multiple Outline SFX](https://balloontales.com/multiple-outline-sfx/) | Lettering, Tips | B11 | text reviewed in earlier implementation research |
| C409 | [Floating Text & Captions](https://balloontales.com/floating-text-captions/) | Lettering, Tips | B08 | text reviewed in earlier implementation research |
| C390 | [The Layer Method](https://balloontales.com/the-layer-method/) | Lettering, Tips | B09 | text reviewed in earlier implementation research |
| C393 | [Eight Steps to Creating a Lettering Font](https://balloontales.com/eight-steps-to-creating-a-lettering-font/) | Production, Tips | B12 | public text reviewed; image/video review may remain |
| C422 | [Tutorial: Pop-Up Letters](https://balloontales.com/tutorial-pop-up-letters/) | Articles | D08 | public text reviewed; image/video review may remain |
| C411 | [Lettering Roundtable: Thinking About Thought Balloons, and Other Abandoned Storytelling Techniques](https://balloontales.com/lettering-roundtable-thinking-about-thought-balloons/) | Articles | A03, D08 | title/category indexed; detailed review pending |
| C383 | [Working With Open FX Fonts](https://balloontales.com/working-with-open-fx-fonts/) | Lettering, Tips | B11 | title/category indexed; detailed review pending |
| C418 | [The Comicraft Glossary of Lettering Terms](https://balloontales.com/the-comicraft-glossary-of-lettering-terms/) | Articles | A05, C03 | text reviewed in earlier implementation research |
| C391 | [Dashed Iron Man Balloons](https://balloontales.com/dashed-iron-man-balloons/) | Lettering, Tips | B05 | public text reviewed; image/video review may remain |
| C421 | [Lettering Showcase: Ferran Delgado](https://balloontales.com/lettering-showcase-ferran-delgado/) | Articles | D08 | title/category indexed; detailed review pending |
| C375 | [Files and Formats](https://balloontales.com/files-and-formats/) | Production, Tips | D05 | title/category indexed; detailed review pending |
| C412 | [Kurt Busiek on Will Eisner](https://balloontales.com/kurt-busiek-on-will-eisner/) | Articles | C01 | public text reviewed; image/video review may remain |
| C424 | [Q&A With MCAD Students](https://balloontales.com/qa-with-mcad-students/) | Interviews | D07 | title/category indexed; detailed review pending |
| C403 | [Jagged Burst Balloons](https://balloontales.com/jagged-burst-balloons/) | Lettering, Tips | B04 | title/category indexed; detailed review pending |
| C387 | [Preparing Lettering Files for Output](https://balloontales.com/preparing-lettering-files-for-output/) | Production, Tips | D05 | text reviewed in earlier implementation research |
| C369 | [Tattered Captions](https://balloontales.com/tattered-captions/) | Lettering, Tips | B08 | public text reviewed; image/video review may remain |
| C397 | [Overlapping Balloons](https://balloontales.com/overlapping-balloons/) | Lettering, Tips | B07 | title/category indexed; detailed review pending |
| C408 | [Alternate Characters](https://balloontales.com/alternate-characters/) | Lettering, Tips | B02, B13 | public text reviewed; image/video review may remain |
| C370 | [The Business of Comics](https://balloontales.com/the-business-of-comics/) | Publishing, Tips | D07 | public text reviewed; image/video review may remain |
| C406 | [Font and Character Usage](https://balloontales.com/font-and-character-usage/) | Lettering, Tips | B02, B03 | public text reviewed; image/video review may remain |
| C373 | [TV Shape Balloon](https://balloontales.com/tv-shape-balloon/) | Lettering, Tips | B04 | title/category indexed; detailed review pending |
| C416 | [Lettering Roundtable: The Case Regarding Upper & Lower Case Lettering Part Two](https://balloontales.com/lettering-roundtable-the-case-regarding-upper-lower-case-lettering-part-two/) | Articles | D08 | title/category indexed; detailed review pending |
| C417 | [Lettering Roundtable: The Case Regarding Upper & Lower Case Lettering](https://balloontales.com/lettering-roundtable-the-case-regarding-upper-lower-case-lettering/) | Articles | D08 | title/category indexed; detailed review pending |
| C399 | [Print Resolution](https://balloontales.com/print-resolution/) | Production, Tips | D05 | title/category indexed; detailed review pending |
| C379 | [Scanning Tips](https://balloontales.com/scanning-tips/) | Production, Tips | D05 | title/category indexed; detailed review pending |
| C398 | [Emphasis Techniques](https://balloontales.com/emphasis-techniques/) | Lettering, Tips | B02 | public text reviewed; image/video review may remain |
| C388 | [Pasteup in Photoshop](https://balloontales.com/pasteup-in-photoshop/) | Production, Tips | D05 | title/category indexed; detailed review pending |
| C426 | [Like a Chained Elephant](https://balloontales.com/like-a-chained-elephant/) | Interviews | D08 | title/category indexed; detailed review pending |
| C371 | [Giving Artwork the ‘Comic Book Look’](https://balloontales.com/giving-artwork-the-comic-book-look/) | Production, Tips | A14 | title/category indexed; detailed review pending |
| C372 | [Creating Tails and Joins](https://balloontales.com/creating-tails-and-joins/) | Lettering, Tips | B06 | text reviewed in earlier implementation research |
| C396 | [‘Trapped Inside’ Balloon](https://balloontales.com/trapped-inside-balloon/) | Lettering, Tips | B06 | public text reviewed; image/video review may remain |
| C419 | [Richard Starkings’ Five Favorite Silver Age Letterers](https://balloontales.com/richard-starkings-five-favorite-silver-age-letterers/) | Articles | D08 | title/category indexed; detailed review pending |
| C404 | [Butting Balloons](https://balloontales.com/butting-balloons/) | Lettering, Tips | B09 | text reviewed in earlier implementation research |
| C382 | [Masking Behind Objects](https://balloontales.com/masking-behind-objects/) | Lettering, Tips | B09 | title/category indexed; detailed review pending |
| C395 | [Printed Comics](https://balloontales.com/printed-comics/) | Publishing, Tips | D07 | public text reviewed; image/video review may remain |
| C405 | [Layer Control](https://balloontales.com/layer-control/) | Lettering, Tips | B09 | title/category indexed; detailed review pending |
| C413 | [Tutorial: Computer Color, Step by Step](https://balloontales.com/tutorial-computer-color-step-by-step/) | Articles | A12, A13, D06 | public text reviewed; image/video review may remain |
| C381 | [Overprinting and Trapping EPS Lettering Files](https://balloontales.com/overprinting-and-trapping-eps-lettering-files/) | Production, Tips | D06 | public text reviewed; image/video review may remain |
| C380 | [Pasteup in QuarkXPress](https://balloontales.com/pasteup-in-quarkxpress/) | Production, Tips | D05 | title/category indexed; detailed review pending |
| C428 | [Letters from America](https://balloontales.com/letters-from-america/) | Interviews | D08 | title/category indexed; detailed review pending |
| C407 | [Making Word Balloons](https://balloontales.com/making-word-balloons/) | Lettering, Tips | B04 | text reviewed in earlier implementation research |
| C374 | [Curved Type](https://balloontales.com/curved-type/) | Lettering, Tips | B11 | text reviewed in earlier implementation research |
| C429 | [On Typography](https://balloontales.com/on-typography/) | Interviews | D08 | title/category indexed; detailed review pending |
| C681 | [Crafting the Comics](https://balloontales.com/crafting-the-comics/) | Interviews | D08 | title/category indexed; detailed review pending |
| C431 | [A Beginners Guide to Computer Lettering](https://balloontales.com/a-beginners-guide-to-computer-lettering/) | Articles | D08 | title/category indexed; detailed review pending |

## Blambot 全部 31 个 canonical 页面

- [about](https://blambot.com/pages/about)
- [already-subscribed-to-newsletter](https://blambot.com/pages/already-subscribed-to-newsletter)
- [blambot-brush-licenses](https://blambot.com/pages/blambot-brush-licenses)
- [brush-faq](https://blambot.com/pages/brush-faq)
- [comic-book-grammar-tradition](https://blambot.com/pages/comic-book-grammar-tradition)
- [comic-lettering](https://blambot.com/pages/comic-lettering)
- [comic-script-basics](https://blambot.com/pages/comic-script-basics)
- [contact](https://blambot.com/pages/contact)
- [custom-fonts](https://blambot.com/pages/custom-fonts)
- [data-sharing-opt-out](https://blambot.com/pages/data-sharing-opt-out)
- [graphic-design](https://blambot.com/pages/graphic-design)
- [hire-blambot](https://blambot.com/pages/hire-blambot)
- [installing-brushes](https://blambot.com/pages/installing-brushes)
- [installing-fonts](https://blambot.com/pages/installing-fonts)
- [lettering-tips](https://blambot.com/pages/lettering-tips)
- [license-options](https://blambot.com/pages/license-options)
- [licenses](https://blambot.com/pages/licenses)
- [logo-design](https://blambot.com/pages/logo-design)
- [nates-top-10-blambot-fonts](https://blambot.com/pages/nates-top-10-blambot-fonts)
- [newsletter-confirmation](https://blambot.com/pages/newsletter-confirmation)
- [newsletter-signup-success](https://blambot.com/pages/newsletter-signup-success)
- [not-subscribed-to-newsletter](https://blambot.com/pages/not-subscribed-to-newsletter)
- [original-art-dimensions-for-american-standard-comics](https://blambot.com/pages/original-art-dimensions-for-american-standard-comics)
- [recover-password](https://blambot.com/pages/recover-password)
- [social-links](https://blambot.com/pages/social-links)
- [successful-logo-design](https://blambot.com/pages/successful-logo-design)
- [the-blambot-inner-circle-secret-society-enamel-pin](https://blambot.com/pages/the-blambot-inner-circle-secret-society-enamel-pin)
- [the-essential-guide-to-comic-book-lettering](https://blambot.com/pages/the-essential-guide-to-comic-book-lettering)
- [the-language-of-the-black-parade](https://blambot.com/pages/the-language-of-the-black-parade)
- [unsubscribed-from-newsletter](https://blambot.com/pages/unsubscribed-from-newsletter)
- [what-happened-to-hand-lettering](https://blambot.com/pages/what-happened-to-hand-lettering)

## 旧教程与站外课程入口

- [Introduction](https://balloontales.com/articles/tutorial/index.html)
- [Character Study](https://balloontales.com/articles/tutorial/part1.html)
- [Fighting Words](https://balloontales.com/articles/tutorial/part2.html)
- [Title Deeds](https://balloontales.com/articles/tutorial/part3.html)
- [Electronic Lettering Composition](https://balloontales.com/articles/tutorial/part4.html)
- [Hand Lettering](https://balloontales.com/articles/tutorial/part5.html)
- [Fonts](https://balloontales.com/fonts/)
- [Book](https://balloontales.com/book/)
- [Online course](https://balloontales.com/online-course/)
- [Welcome](https://balloontales.com/)
- [Blambot 视频频道](https://www.youtube.com/@blambot_fonts)：频道入口确认，未穷尽全部视频。
- [Blambot 指南书](https://blambot.com/pages/the-essential-guide-to-comic-book-lettering)：仅公开介绍；正文未取得。
