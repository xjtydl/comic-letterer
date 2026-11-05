"""Build the research ledger from locally recorded public source metadata."""
import json
from pathlib import Path
base=Path(__file__).parent
p=base/'two-site-inventory-20261105.json';data=json.loads(p.read_text())
# Original topic summaries, not copied tutorial text.
tips=[
'英文横杠 I 与上下文选择','字偶间距 Kerning','拟声字从声音源与力线构图','尾巴交叉与隐含交叉','文字堆叠与长词布局','全页尾根宽度一致、防针尖尾','行距与气泡负空间','外语对白与特殊字形','对白和连续旁白的引号','斜体的叙事用途','拖音与中断标点','局部行宽压缩','对话气泡叠放与节奏／景深','阅读顺序、保护人物、图文统一','图层法与复合描边法','设备声尖齿／思想泡瓣随尺寸保持一致','字号的视觉差异与实尺寸试印','字形结构术语','自然不对称气泡','OpenType 连字与上下文替代','拟声字色板与画面配色','手写笔尖与笔画方向','排字前的脚本整理','浅字深底的小字印刷增益'
]
for card,title in zip(data['blambot_tip_cards'],tips):
 card['topic_zh']=title;card.setdefault('review','OCR text reviewed 2026-11-05; full visual example comparison pending');card['training_media']='not copied'
rows=[]
def add(i,t,scope,program,skill,current,source):rows.append(dict(id=i,title=t,scope=scope,program=program,skill=skill,current=current,sources=source))
add('A01','整本制作与工序','剧本→缩略草图→铅笔／墨线→排字与上色→校样→交付','工序状态、版本、依赖与资产追溯','comic-production-entry','已有制作入口；独立程序尚未接通整本工序',['C502'])
add('A02','剧本与文字交接','页格编号、角色、动作说明、台词、参考链接、旁白、拟声、强调','富文本导入、冻结原文、稳定 ID','comic-production-entry / comic-lettering','已有 JSON 与原文冻结；富文本导入待做',['B-script','B-TIP-023'])
add('A03','叙事与阅读时间','思想与独白的用途、悬念、反差、信息揭示、停顿与对白节奏','叙事意图字段、读序图、对照方案','american-comic-layout / comic-visual-language','已有原则；系统案例与评测待补',['C385','C411'])
add('A04','缩略草图与方案探索','整页缩略草图、多个构图方案、保留修改过程','缩略稿画板、方案比较与版本','american-comic-layout','已有 Skill 方法；独立程序未实现',['C502','C478'])
add('A05','整页构图与分格','格框、留白、主次、阅读路线、跨格、跨页与翻页节奏','布局编辑与阅读路线检测','american-comic-layout','已有 Skill；程序仅显式分格与初步读序检查',['C502','CL4','C418','EXT-layout-depth'])
add('A06','单格构图与图文协同','人物、动作、背景、负空间、对白与 SFX 共同构图；避免贴纸感','构图区域、焦点／保护区与候选布局','american-comic-layout / comic-visual-language','保护区及局部摆位已有；画面理解待补',['B-TIP-003','B-TIP-004','B-TIP-014','CL4'])
add('A07','连续动作与镜头','景别、角度、轴线、方向、动作因果、相邻格时间关系','相邻格状态与空间检查','comic-continuity-acting / cinematography','项目已有方法；两站不能提供完整课程，另补来源',['EXT-continuity'])
add('A08','人物表演与造型','人体、重心、手势、表情、视线、动作剪影','身份／表演参考管理与局部诊断','comic-continuity-acting / comic-visual-language','项目有方法；绘画课程与系统训练集待补',['EXT-drawing'])
add('A09','角色与道具连续性','身份、服装、比例、道具状态、多人一致性','角色／道具资产版本与检查','comic-continuity-acting','项目已有参考流程；不是 Letterer v0.3 能力',['EXT-continuity'])
add('A10','场景、透视与空间','场景布局、透视、机位、遮挡、光源、必要白模','原画关联、空间导图与状态约束','comic-production-entry / comic-continuity-acting','项目已有原画先行和白模规则；基础透视另补来源',['EXT-perspective'])
add('A11','铅笔、墨线与笔触','草稿清稿、墨线层级、黑白形状、笔锋及干湿笔触','分层画稿、路径和笔刷接口','comic-visual-language','Skill 有线面原则；绘画引擎与完整训练待补',['C502','B-TIP-022','EXT-inking'])
add('A12','平涂与区域蒙版','线稿与颜色分离、平涂区域、选择蒙版、保留高分辨率线稿','区域 ID、平涂层与可重选蒙版','comic-visual-language','尚未在独立程序实现',['C413'])
add('A13','光影、色彩与明度','上色、阴影、色板、图文对比、灰阶与多背景检查','色板与对比检查、渐变及着色层','comic-visual-language','已有固定填色；配色系统与绘画光影课程待补',['C413','C392','C389','B-TIP-021','B-logo'])
add('A14','材质与复古漫画外观','网点、纸张老化、折痕、磨损、混合模式','独立纹理层、强度与媒介预览','comic-visual-language','未实现',['C371','C386','C774'])
add('B01','文字形状与适配','断行、词组、长词、行距、字距、负空间、局部字宽','字体度量、断行与轮廓适配','comic-lettering / comic-letterer','已实现并有连续漫画验证；语义断句待补',['C378','B-TIP-005','B-TIP-007','B-TIP-012'])
add('B02','真实字体与高级排版','粗斜体、字偶距、基线、OpenType、替代字形、跨行强调','字形塑形、每行／片段基线及字体特性','comic-lettering / comic-letterer','真实字体强调、对白跳动/波形及片段基线已有；OpenType、逐行字宽待做，见实施流水账',['C376','C408','C401','C406','C398','B-TIP-002','B-TIP-020'])
add('B03','语言与漫画标点','37 项语法传统；外语、数字、引号、拖音、中断、注释、审查符号','按语言和书籍样式检查；保留原文、修改另列建议','comic-lettering','有原文和禁则检查；完整语法建议器未做',['B-grammar','C406','C729'])
add('B04','气泡形状与自然度','椭圆、TV、自然不对称、爆炸、锯齿、火焰、平边；齿距保持','可编辑路径、可缩放样式与轮廓密度','comic-letterer / comic-visual-language','椭圆／TV／自然不对称和基础声线已有；火焰、锯齿密度等未完成',['C407','C373','C403','C394','C786','B-TIP-016','B-TIP-019'])
add('B05','特殊声音体系','思想、弱声、耳语、设备、怪物、心灵、喘息、歌唱、机械虚线','声线形状、装饰及匹配文字表现','comic-visual-language / comic-letterer','基本预设已有；多数缺完整剧情验收，机械分层样式未做',['B-grammar','C384','C402','C391','C401'])
add('B06','尾巴与声源','嘴／头／设备、根宽、长度、间隙、曲线、隐藏声源、画外','尾巴编辑、认主与交叉检查','comic-letterer / comic-lettering','主要操作已有整页验证；全书一致性检查待补',['C372','C396','B-TIP-004','B-TIP-006'])
add('B07','连泡、插话与层叠','连贯发言、连接桥、打断、叠放顺序、人物前后层次','显式连接关系、叠放模式、读序验证','comic-lettering / comic-letterer','连泡和中断案例已有；叠放策略库待完善',['C397','B-TIP-013'])
add('B08','旁白与装饰框','时地、内心、说话、编辑、无框旁白、首字、破损／卷轴框','旁白语义、首字排版、装饰轮廓','comic-letterer / comic-visual-language','旁白类型、浮动字及破损框已有；首字与卷轴框未做',['C409','C369','B-grammar'])
add('B09','边框、遮挡与空间层次','贴边、跨边、前景遮罩、避免气泡成为错误实体、相切','裁切与遮罩、墨线相切检查、图层顺序','comic-letterer / comic-lettering','手工遮罩贴边已有；自动识图与全局空间判断待补',['C404','C382','C390','C405','B-TIP-015'])
add('B10','拟声字的叙事设计','声音来源、力度、节奏、材质、方向与力线','声音元数据、字形布局与源点','comic-visual-language','基本 SFX 有漫画验证；系统声音设计语料未建',['CL2','B-TIP-003','C782'])
add('B11','拟声字造型与渲染','手绘、字体变形、逐字、空心、多描边、阴影、透视、渐变、磨损','字形编辑、透视与材质、路径布尔运算','comic-letterer / comic-visual-language','多描边空心逐字弧形厚度已有；透视／材质未做',['C400','C383','C374','C389','C771','C778','CL3'])
add('B12','字体创作与虚构文字','手写采样、矢量化、字形结构、基准线、字偶距、家族、虚构字母','字形编辑与字体导出、字库来源','comic-visual-language（新增字体创作参考）','未实现字体制作；已能加载与测量外部字体',['C393','C420','C415','CL1','B-black-parade'])
add('B13','手写工具与自然变化','笔尖、方向、Ames 辅助线、有限变化、保留活力','笔触／轨迹记录、替代字形与自然路径','comic-visual-language','有逐字参数；完整手写和轨迹系统未做',['B-TIP-022','CL5','C408','B-hand'])
add('C01','标题页与署名构图','标题与故事气质、主次词、画面融合、署名、装饰首字','标题画板、文字形状与署名模块','american-comic-layout / comic-visual-language','没有专用系统，基础字形操作可复用',['CL3','C412','B-graphic'])
add('C02','封面与 Logo','轮廓识别、草图方案、字形重叠、远读、小图、黑白和多背景','Logo／封面编辑及多尺寸对照','comic-visual-language / american-comic-layout','尚无专门能力与验收样本',['C478','B-logo','B-logo-gallery'])
add('C03','场景内文字','路牌、报纸、屏幕、信件、容器标签、建筑文字','表面锚点、透视和材质合成','comic-visual-language / comic-lettering','普通文字可放；表面透视未做',['C502','C418','CP241'])
add('C04','出版与衍生平面设计','扉页、目录、署名页、宣传图、衣服／海报等载体','多尺寸画板、版式模板与输出','comic-visual-language（平面设计参考）','未做；服务案例只有展示，不等于完整教学',['B-graphic','B-logo-gallery'])
add('D01','字体笔刷资产','设计／对白／SFX 字体；气泡／SFX／磨损／粉彩笔刷；安装和角点故障','资产清单、外部资源加载、笔刷和描边参数','comic-lettering / comic-visual-language','字体加载已有；笔刷系统未做',['B-brushes','B-brush-faq','B-fonts'])
add('D02','软件工具操作','Illustrator／Photoshop／Procreate／排版软件；页面、字体、尾巴、效果、遮罩','操作接口与可回放工具调用','comic-production-entry / comic-letterer','独立编辑器已有；外部工具适配与完整课程待补',['CP241','C793','C748','C757','C759','C764','C767','C771','C778','C782','C786','C789'])
add('D03','校样、修改与本地化','读稿、全页校样、局部纠错、翻译后重排、不损坏原画','差异、修订、撤销重做与语言版本','comic-production-entry / comic-letterer','保存重载／导出／冻结已有；整本校样和翻译工作流待补',['C502','B-hand','C541'])
add('D04','全书一致性','角色声线、字体、尾根、描边、齿距、色板与版本','全书样式库、依赖更新、例外记录','comic-production-entry / comic-visual-language','页样式已有；书籍级管理未做',['B-TIP-006','B-TIP-016','C394','CL2'])
add('D05','文件、扫描与数字交付','扫描线稿、分辨率、位图／矢量、可编辑母版、低清校样和高清合成','文件导入、分辨率检查、多格式导出','comic-lettering / comic-production-entry','JSON／SVG／PNG 已有；扫描与 PDF 等未做',['C375','C379','C399','C388','C380','C387'])
add('D06','印前与成品尺寸','原稿尺寸、出血、裁切、安全区、分色、黑版、叠印、陷印、浅字增益','印前预检、色彩配置与输出配置','comic-lettering（印前参考）','未实现完整印前；历史参数须按当前介质重核',['B-dimensions','C381','C413','B-TIP-024'])
add('D07','出版、协作与职业流程','作品集、编辑反馈、职责、排期、报价、署名、印刷发行推广','项目计划、交付单、署名与预算数据','comic-production-entry（出版协作参考）','未实现；历史公司／费率不能当现行标准',['C377','C370','C395','C424','C425'])
add('D08','历史、审美与案例批评','大小写争论、思想泡选择、手写／数字、作品复盘、访谈经验','案例索引与比较展示','comic-visual-language / comic-production-entry','已有少量原则；全部文章尚需逐篇提炼',['C416','C417','C411','C419','C421','C532','B-hand'])
add('D09','来源、授权与使用方式','字体／笔刷使用、嵌入、商业范围；教程与训练资料分别记账','来源、许可证、允许用途和素材版本','comic-production-entry','目前不附带商业字体；完整资产授权台账待做',['B-licenses','B-brush-licenses'])
add('E01','可检索知识库','索引→核读→方法→适用条件／反例→程序／Skill→实图证据','来源版本与能力台账','沿用入口及专项 Skill','本轮建立全站发现索引；未声称全内容掌握',['PROJECT-ai'])
add('E02','模仿人类的制作过程记录','输入、意图、操作、前后图、失败诊断、修订与验收','工具轨迹、图层／矢量状态及阶段资产记录','comic-production-entry','现有 JSON／输出可作为起点；完整过程语料未建',['PROJECT-ai'])
add('E03','练习课程与反例','从局部到单格、连续页、整章；同剧情多方案和纠错','任务集、难度、失败类别、评审表','现有专项 Skill 加训练参考','本轮规划；未训练新模型',['PROJECT-ai'])
add('E04','AI 训练与数据','原创／授权样本；分镜、构图、动作、线稿、平涂、文字图层与修订配对','数据集版本、按作品切分、训练适配接口','新增训练规范应独立于制作 Skill','待建；模型与训练方式依据目标另选，未启动训练',['PROJECT-ai'])
add('E05','评测与回归','故事可读性、构图、身份／空间连续性、声源、文字正确性、印刷表现','客观检查＋盲评＋跨页回归；与不使用 Skill 基线比较','现有制作验收扩展','已有 87 个 Letterer 测试和少量整页；全绘画评测未建',['PROJECT-ai'])
(base/'two-site-capabilities-20261105.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
# Direct source memberships; default interview routing means discovery only.
source_routes={}
for row in rows:
 for sid in row['sources']:source_routes.setdefault(sid,[]).append(row['id'])
reviewed_this={502,413,385,541,401,394,369,396,391,376,478,393,386,408,398,392,389,412,406,422,381,377,370,395,786}
reviewed_previous={418,378,407,372,390,400,387,409,402,404,374}
for post in data['comicraft_posts']:
 ident=post['id'];post['capabilities']=source_routes.get(ident,['D08'] if 'Interviews' in post['categories'] or 'Articles' in post['categories'] else ['E01'])
 num=int(ident[1:]);post['review']='public text reviewed; image/video review may remain' if num in reviewed_this else 'text reviewed in earlier implementation research' if num in reviewed_previous else 'title/category indexed; detailed review pending'
 if 'Procreate' in post['title'] or num in {420,415,774,532}:post['review']='page/topic indexed; full video not watched'
for tip in data['blambot_tip_cards']:tip['capabilities']=source_routes.get(tip['id'],['B03'] if int(tip['id'][-3:]) in {1,8,9,10,11} else ['E01'])
data['comicraft_legacy_tutorial'][0]['review']='entry indexed; detailed review pending'
p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
intro='''# 两站全范围 → 漫画创作程序与 Skill 总纲\n\n日期：2026-11-05。用户明确：包含 Blambot 和 Comicraft / Balloon Tales 全部相关内容，覆盖构图、绘画、制作，不限字体和气泡；用于 AI 按人类创作流程制作漫画，以及未来训练 AI。\n\n这是纳入范围与实施归属清单，不是完成声明。\n\n## 发现范围与阅读证据\n\n- Comicraft：公开 WordPress 索引的 94 篇文章全部登记，另登记 4 个页面与 6 个旧教程入口。94 是当前 posts 端点数量，不代表所有历史 URL 或站外内容。\n- Blambot：canonical sitemap 的 31 个页面、15 个集合、313 个商品 URL 已登记；24 张 Better Letterer 图卡逐张 OCR 阅读文字，37 项语法标题登记。未声称完成全部配图视觉比较。商品条目归资产分类，不冒充教程。\n- 逐篇阅读状态见 JSON；新查读包括成页全流程、上色、思想泡叙事、Logo、字体制作、特殊效果、笔刷与出版。\n- 视频只登记页面、主题和入口，尚未完整观看；书籍／付费课程只读公开介绍，正文未取得；外部字体商店和 YouTube 全目录未穷尽。\n- 完整 URL 索引见 [机器可读索引](two-site-inventory-20261105.json)，各能力字段见 [能力表 JSON](two-site-capabilities-20261105.json)。\n\n## 两站全部菜单归属\n\n| 网站／菜单 | 纳入内容 | 进入哪里 |\n|---|---|---|\n| Blambot Fonts | 全部／Design／Dialogue／Sound Effect／Packs／Indie／Pro、安装、推荐与定制 | 字体选择、字库、风格搭配、资产管理 |\n| Blambot Brushes | 气泡、SFX、Cockroacher 磨损、Perilous Pastel；安装、FAQ | 笔触、矢量笔刷、纹理、角点故障处理 |\n| Blambot Licences | 字体、笔刷及用途分类 | 来源与用途台账；不假定公开教程或购入字体已授权训练 |\n| Blambot Services | 排字、定制字库、Graphic Design、Logo Design、委托流程 | 成页、平面构图、封面／署名／宣传设计、协作需求 |\n| Blambot Articles | Better Letterer、语法、脚本、尺寸、手写史、Black Parade、视频；另由 sitemap 找到 Successful Logo Design 和 Top 10 Fonts | 构图、叙事、字形、文字、工序、案例与规则 |\n| Blambot Merch | 指南书、签名版、徽章、礼卡 | 指南书入参考入口；商品设计入衍生设计；礼卡不算创作技能 |\n| Blambot Contact／About／站务页 | 作者、联络、履历；账户和订阅等页面 | 来源身份与协作背景；站务保留索引，不变成绘画功能 |\n| Comicraft Articles | 成页、上色、字体、标题、Logo、思想泡与大小写讨论、历史案例、纸艺立体字 | 创作工序、构图、色彩、字体、设计、审美与扩展实验 |\n| Comicraft Tips / Lettering | 所有气泡、尾巴、字形、拟声、浮动字、图层、Procreate 等 | 程序操作＋专项 Skill |\n| Comicraft Tips / Production | 扫描、格式、印刷、合成、分色、旧封面、网点 | 绘画后期与交付模块 |\n| Comicraft Tips / Publishing | 入行、业务、自出版、发行推广 | 协作与出版 Skill；旧信息需要更新 |\n| Comicraft Interviews | 24 篇访谈记录 | 案例、方法选择、创作过程与职业判断 |\n| Comicraft Glossary | 空间、节奏、字形、标题、场景字、遮挡等术语 | 能力与标注词汇表 |\n| Comicraft Book／Online course／Fonts | 书籍、Illustrator 课程、字库外链 | 教材与工具入口；未读取内容保持待研 |\n\n## 能力总表\n\n来源前缀：B 为 Blambot，C 为 Comicraft 当前文章 ID，CL 为旧系列，CP 为页面。EXT 是完整绘画目标需要另补的来源；PROJECT-ai 是我们提出的系统设计，不能归称两站提供了 AI 训练方案。\n\n'''
lines=[intro,'| ID | 能力 | 全部纳入的内容 | 程序责任 | Skill 归属 | 当前状态 |\n|---|---|---|---|---|---|\n']
for r in rows:lines.append('| '+' | '.join(r[k] for k in ['id','title','scope','program','skill','current'])+' |\n')
lines.append('''\n## 人类流程与 AI 训练的对应\n\n制作目标是：理解剧本→分析已批准参考→缩略方案→整页／单格构图→人物与空间表演→线稿／上色→文字与声音→校样修订→交付。使用端到端生图、分层绘图或混合方式，应按任务选择；不把模拟每一笔作为唯一实现方式。\n\n技能检索是运行时指导，不等于训练模型。训练准备要保存输入、叙事意图、可观察的选择理由、工具操作、前后状态和评价；不要求记录模型私有思维链。已批准原画、台词和身份约束随样本保留。\n\n数据首选原创或明确授权的过程样本；教程只提炼方法和来源，商品字体、商业笔刷和第三方漫画页不自动进入训练集。测试按作品／角色／场景分组，防止相邻格同时出现在训练和测试中。\n\n课程任务需要包含：构图选择、读序修复、姿态／场景连续性、线稿与平涂、声音表现、标题页、成页纠错；每类有成功、失败及修订案例。评测同时检查叙事、构图、文字与实际阅读效果。87 项排字测试不能代表这些能力已通过。\n\n两站并非系统人体、透视、镜头与动作课程：这些能力仍列入 A07–A11，复用现有制作 Skill 并补专业来源，不编造网站依据。\n\n## 内容吸收与完成标准\n\n每项按“索引→读正文／看图／看视频→提炼适用条件与反例→程序实现或 Skill 方法→完整漫画验证”记录。本文只完成范围归档与部分核读。用户2026-11-05指定顺序：先补完气泡与文字，并用完整剧情漫画验证；之后继续构图、画稿工序、色彩、整本流程和AI训练。最新实施证据见 [流水账](IMPLEMENTATION_LEDGER.md)，接续先读 [工作入口](../WORK_INDEX.md)。\n\n历史软件菜单、分辨率、印刷参数、费率和发行信息仅作历史方法；实际使用须按当前软件和交付条件复核。\n\n## Blambot 24 张图卡\n\n| ID | 方法主题 | 阅读状态 |\n|---|---|---|\n''')
for c in data['blambot_tip_cards']:lines.append(f"| [{c['id']}]({c['url']}) | {c['topic_zh']} | OCR 文本已读；配图视觉比较待补 |\n")
lines.append('\n## Blambot 37 项语法主题\n\n'+ '；'.join(x['title'] for x in data['blambot_grammar_topics'])+'。\n')
lines.append('\n## Comicraft 全部 94 篇当前文章\n\n| ID | 文章 | 类别 | 能力归属 | 阅读状态 |\n|---|---|---|---|---|\n')
for c in data['comicraft_posts']:lines.append(f"| {c['id']} | [{c['title']}]({c['url']}) | {', '.join(c['categories'])} | {', '.join(c['capabilities'])} | {c['review']} |\n")
lines.append('\n## Blambot 全部 31 个 canonical 页面\n\n')
for u in data['blambot_sitemap']['pages']:lines.append(f'- [{u.rsplit("/",1)[-1]}]({u})\n')
lines.append('\n## 旧教程与站外课程入口\n\n')
for c in data['comicraft_legacy_tutorial']+data['comicraft_pages']:lines.append(f"- [{c['title']}]({c['url']})\n")
lines.append('- [Blambot 视频频道](https://www.youtube.com/@blambot_fonts)：频道入口确认，未穷尽全部视频。\n- [Blambot 指南书](https://blambot.com/pages/the-essential-guide-to-comic-book-lettering)：仅公开介绍；正文未取得。\n')
(base/'TWO_SITE_MASTER_SCOPE_20261105.md').write_text(''.join(lines))
print('Capabilities:',len(rows),'Posts:',len(data['comicraft_posts']),'Tip cards:',len(tips))
