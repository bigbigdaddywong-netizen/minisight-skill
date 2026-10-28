# 接口文档：搜索 / 研报 / 政策 / 宏观（api-discovery.md，内部文档）

## 全局搜索（换 id 的入口）

| 命令 | 方法与路径 | 说明 |
|---|---|---|
| `ms.py search <关键词>` | GET `/search?q=<关键词>` | 全局搜索：企业/题材/设备/词条，返回各类型命中与 id |
| `ms.py search --list`（如支持） | GET `/search/list` | 搜索列表形态 |
| — | GET `/search/news`、GET `/search/news/stats` | 新闻检索与统计（需要新闻证据时用） |

工作流约定：**先 search 换 id，再进各域详情接口**。中文名优先，别名匹配由服务端处理（企业别名表已补录中文名，如 LEGN=传奇生物）。

## 研报

| 命令 | 方法与路径 | 说明 |
|---|---|---|
| `ms.py reports <关键词>` | GET `/reports/search?q=` | 研报检索（标题/摘要匹配） |
| — | GET `/reports/pdf`、GET `/reports/fulltext` | 原文/全文（cookie 会话态接口，skill 通道不可用，仅列已知） |

skill 内只承诺 search 元数据检索；需要原文时引导用户到 minisight.cn。

## 政策

| 命令 | 方法与路径 | 说明 |
|---|---|---|
| `ms.py policies <关键词>` | GET `/policies/search?q=` | 政策检索（federal_register/国内政府源） |
| — | GET `/policies/{policy_id}` | 政策详情 |

## 宏观罗盘

| 命令 | 方法与路径 | 说明 |
|---|---|---|
| `ms.py compass` | GET `/components/macro/compass` | 宏观指标罗盘 |
| — | GET `/components/macro/compass/{indicator_id}/themes` | 指标关联题材 |

## 输出纪律

- 研报/政策/新闻证据引用时带发布日期与标题，不写「据悉」「有报道称」。
- 宏观数据只做背景板，不作为产业链结论的直接依据。
