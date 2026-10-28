# MiniSight 数据接口总览

本文件描述 MiniSight 用户态只读接口。所有路径基于 `MINISIGHT_API_BASE`（生产：`https://www.minisight.cn/api/v1`，ms.py 已内置该默认值）。

**重要约定：**
1. 查询参数名以实际为准——拿不准时先执行 `ms.py openapi --grep <路径片段>` 看该端点在 OpenAPI 里声明的参数，再调用。
2. 所有接口当前要求鉴权（JWT 或 API Key，见下）。
3. 响应为 JSON，统一带 `created_at/updated_at` 时间戳字段，输出时引用数据日期。

**鉴权（双通道）：**
- `X-API-Key: <key>` —— skill 正式通道。生产部署时需后端在 `get_current_user` 旁挂 API-Key 放行中间件（guest key 阶段为服务端统一 key，存环境变量，不进任何仓库）。
- `Authorization: Bearer <jwt>` —— 调试通道。

**额度（guest key 阶段）：**
- 服务端全局限流（部署时配置）。客户端 429 处理见 SKILL.md。
- 后续演进：按账号发 key → free/prime/alpha 档位差异化额度 → 剩余额度随响应头返回。

## 域索引

| 文档 | 覆盖命令 | 数据域 |
|---|---|---|
| api-chain.md | industries / theme / devices / device / enterprise / chain-leaders | 产业链、设备BOM、企业主体、链主动态 |
| api-alt-tech.md | alt-tech / terms / term | 替代技术雷达、值得研究词表 |
| api-companies.md | financial / earnings | 财务三表、盈利预测 |
| api-discovery.md | search / reports / policies / compass | 全局搜索、研报、政策、宏观 |

## 故障排查速查

| 现象 | 处置 |
|---|---|
| 401 | key 未配置/错误；或后端未部署 API-Key 放行中间件（见 SKILL 包发布清单） |
| 404 路径 | 用 `ms.py openapi --grep` 核对；注意部分接口挂在 `/components` 前缀下（见各文档） |
| 429 | 触发限流，等待或提额 |
| 数据为空 | 该域数据在本地/生产不同步时会出现；画布上能看到的数据接口才有 |
