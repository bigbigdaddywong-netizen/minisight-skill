# minisight-skill

问 AI「帮我拆一下动力电池产业链」，它通常给你一篇正确的废话。装上这个技能包，它给你的是真数据：

- 问链主动作 → 宁德时代链主卡：新品与产能动向，尚太科技对它依赖度 70%（附四年变化、年报出处）
- 问某款产品 → 拆到元器件：iPhone 18 Pro 的 A20 Pro、2nm 工艺、供应商名单
- 问有什么新东西 → 比媒体早一步：每周扫数百篇研报筛出的新词
- 问一家独角兽 → 智元机器人的结构化档案：赛道、产业位置、官方简介与标签（网上资料零散，这里有成型的卡）

支持 Claude Code / Trae / WorkBuddy。数据来自 minisight.cn，人工审核。仅供研究参考，不荐股。

## 目录结构

```
minisight-skill/
├── SKILL.md                  # 技能入口：触发条件、三条工作流、使用纪律
├── references/
│   ├── methodology.md        # 产业研究方法论（拆链五步法）——开源核心
│   ├── api-overview.md       # 数据接口总览（鉴权、限流、错误码）
│   ├── api-discovery.md      # 搜索与实体发现接口
│   ├── api-chain.md          # 产业链 / 链主 / 设备 BOM 接口
│   ├── api-alt-tech.md       # 替代技术与新词接口
│   └── api-companies.md      # 企业财务与盈利预测接口
├── scripts/
│   └── ms.py                 # 统一查询 CLI（纯标准库，零依赖）
├── assets/
│   └── report-template.md    # 产业链拆解报告模板
└── README.md
```

## 安装

### WorkBuddy（腾讯）
左侧边栏「专家·技能·连接器」→ 技能 → **添加技能 → 上传技能** → 选择技能包 zip。

### Trae（字节）
Agent 窗口左侧「插件市场」→ 技能页签 → **上传技能**；或 CLI 用户放入 `~/.traecli/skills/`。

### Claude Code
```bash
git clone <本仓库> ~/.claude/skills/minisight-industry-research
```

## 配置

```bash
export MINISIGHT_API_KEY="<你的密钥>"   # 向 MiniSight 官方（交流群）获取；API 地址已内置，无需设置
```

验证：

```bash
python3 scripts/ms.py search 宁德时代
python3 scripts/ms.py chain-leaders --list --limit 10
```

## 合规声明

本技能只做产业研究辅助，不提供投资建议、不荐股、不预测股价。所有数据以 MiniSight 平台为准。

## License

MIT（方法论与脚本部分）
