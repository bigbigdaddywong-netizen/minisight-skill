# 接口文档：替代技术 / 值得研究词表（api-alt-tech.md，内部文档）

对应 SKILL.md 工作流 1 第 4 步（盯变量）与工作流 3（找选题）。

## 替代技术雷达

| 命令 | 方法与路径 | 说明 |
|---|---|---|
| `ms.py alt-tech --theme-id <id>` | GET `/components/tech-substitution?themeId=` | 按题材查替代技术动态：本地新闻/研报近14天 + 联网检索三路证据 → LLM 抽取 → **运营审核采纳后**入库 |

数据说明：
- 周扫任务（周日 09:00）产出草稿，审核采纳后写主表（tech_updates）；接口只出主表。
- 去重键 route|type|period|title 的 md5，无重复条目。
- 查询契约以 openapi 为准：已实证参数为 `themeId`（2026-10-28），无 days/keyword 过滤参数。
- 判断替代路线阶段（实验室/中试/量产）需从条目正文/证据里读，接口若有阶段字段以返回为准；没有就让 AI 基于条目文本判断并标注「推断」。

## 值得研究词表

| 命令 | 方法与路径 | 说明 |
|---|---|---|
| `ms.py terms` | GET `/research-worth/window` | 词表窗口：当前值得研究的词条集合（找选题入口） |
| `ms.py term <id>` | GET `/research-worth/term/{term_id}` | 词条详情 |
| `ms.py term <id> --assoc` | GET `/research-worth/term/{term_id}/associations` | 词条关联（关联企业/题材/事件） |

数据说明：
- 词条含别名表（term_aliases）；生产增量每日过闸直写，本地运营编辑以 updated_at 新者胜。
- 工作流 3 的推荐理由要从词条的「冒头信号」（来源、频次、时间）提炼，不要空泛点评。

## 输出纪律

- 替代技术条目必须带数据日期与来源类型（新闻/研报/联网检索）。
- 新词推荐输出三要素：词、冒头信号、下一步动作（进入工作流 1 深拆 / 仅观察）。
