# 接口文档：产业链 / 企业 / 链主（api-chain.md，内部文档）

对应 SKILL.md 工作流 1（拆产业链）与工作流 2（盯动态）的主体部分。

## 产业与题材

| 命令 | 方法与路径 | 说明 |
|---|---|---|
| `ms.py industries` | GET `/industries` | 产业分类列表，用于定链边界 |
| `ms.py theme <id>` | GET `/components/theme/{theme_id}` | 题材/主题详情（挂在 `/components` 前缀下） |

注意：`theme` 与 `company`、`earnings-forecast`、`macro`、`chain-leaders`、`tech-substitution` 都挂在 `/components` 前缀下，这是画布组件接口的历史前缀，不要漏写。

## 设备与 BOM

| 命令 | 方法与路径 | 说明 |
|---|---|---|
| `ms.py devices` | GET `/device` | 设备列表（找锚定设备，如 iPhone） |
| `ms.py device <id>` | GET `/device/{device_id}` | 设备详情 + BOM 物料清单（拆供应关系的核心数据源） |

BOM 条目要点位（hotspot）关联到环节与企业。用于「一台设备拆出一条链」叙事。

## 企业主体

| 命令 | 方法与路径 | 说明 |
|---|---|---|
| `ms.py enterprise <id>` | GET `/enterprise/{enterprise_id}` | 企业卡：名称、上市地/代码、市值、主营、所属榜单（含 GLOBAL 非美港A股上市、UNICORN 未上市独角兽两桶，两桶不重叠） |
| `ms.py enterprise <id> --aliases` | GET `/enterprise/{id}/aliases` | 企业别名（中英文名、简称；检索匹配用） |
| `ms.py search <名>` | （见 api-discovery.md） | 不知道企业 id 时，先用全局搜索换 id |

企业 id 即 companies 表主键（如 A股 6 位代码、港股/美股 ticker 形式，以实际返回为准）。

## 链主动态

| 命令 | 方法与路径 | 说明 |
|---|---|---|
| `ms.py chain-leaders --list` | GET `/components/chain-leaders/list` | 链主清单（系统已标注的链主主体，返回 leaderId） |
| `ms.py chain-leaders --leader-id <id>` | GET `/components/chain-leaders?leaderId=` | 按链主查事件动态（题材新闻+个股研报+联网检索三路证据 → LLM 抽取 → **运营审核采纳后**入库） |

数据说明：
- 只暴露**已审核主表**（chain_events），草稿/已忽略数据不在接口中。
- 事件有去重键（route|type|period|title 的 md5），同一事件不会重复出现。
- 查询契约以 openapi 为准：已实证参数为 `leaderId`（2026-10-28），无 days/keyword 过滤参数，时间过滤在客户端做。

## 输出纪律（对应 methodology.md）

- 供应关系必须有 BOM/接口数据支撑，缺证据标「待验证」。
- 链主事件必须带原始日期；影响推演与事实分开表述。
