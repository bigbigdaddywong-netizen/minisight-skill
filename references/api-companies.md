# 接口文档：财务 / 盈利预测（api-companies.md，内部文档）

对应拆链五步法第五步（财务验证）。

## 企业财务

| 命令 | 方法与路径 | 说明 |
|---|---|---|
| `ms.py financial <company_id>` | GET `/financial/company/{company_id}` | 单企业财务数据（营收结构/毛利率/资本开支等验证字段） |

数据覆盖说明：
- 完整三表目前**仅覆盖 A 股**；港美股财务以 companies 行内字段（市值/营收/净利）存在。给港美股做财务验证时，明确告知用户「港美股仅市值/营收/净利概要，无三表明细」，不要装作有。
- A 股三表任务财报季日频、淡季周频更新；引用时带 updated_at 日期。

## 盈利预测

| 命令 | 方法与路径 | 说明 |
|---|---|---|
| `ms.py earnings` | GET `/components/earnings-forecast` | 盈利预测列表 |
| `ms.py earnings <id> --details` | GET `/components/earnings-forecast/{company_id}/details` | 单企业预测明细 |

## 财务验证纪律（对应 methodology.md 第五步）

- 验证三问：该业务营收占比够不够大？毛利率有没有定价权证据？资本开支是否在押注扩产？
- 逻辑受益但财务看不到证据 → 结论降级为「逻辑受益、待验证」，不许写成事实。
- 美股/港股/独角兽缺数据时如实说明，禁止用旧数据或他企数据凑。
