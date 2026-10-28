#!/usr/bin/env python3
"""MiniSight 产业研究 CLI —— skill 的统一查询入口（v1.1）。

零第三方依赖（纯标准库）。所有输出为 JSON。

环境变量：
  MINISIGHT_API_BASE   API 根地址（可选，默认已指向生产 https://www.minisight.cn/api/v1）
  MINISIGHT_API_KEY    访问密钥（向 MiniSight 官方获取）
  MINISIGHT_ACCESS_TOKEN 可选，直接使用 JWT（调试用）

用法示例：
  ms.py weekly                        # 一键本周产业情报周报（招牌场景）
  ms.py search 宁德时代
  ms.py search 智元                   # 独角兽 id 形如 unicorn-*
  ms.py chain-leaders --list --limit 10
  ms.py chain-leaders --leader-id 1
  ms.py device DVC0001
  ms.py financial CMP0001
  ms.py openapi --grep chain      # 拉取实时接口清单并按关键词过滤（仅本地调试环境可用）
"""

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

DEFAULT_BASE = "https://www.minisight.cn/api/v1"
DEFAULT_TIMEOUT = 30


def http_get(path, params=None, base=None, key=None, token=None, timeout=DEFAULT_TIMEOUT, soft=False):
    base = (base or os.environ.get("MINISIGHT_API_BASE") or DEFAULT_BASE).rstrip("/")
    url = base + "/" + path.lstrip("/")
    if params:
        params = {k: v for k, v in params.items() if v not in (None, "")}
        if params:
            url += "?" + urllib.parse.urlencode(params, doseq=True)
    req = urllib.request.Request(url, method="GET")
    req.add_header("Accept", "application/json")
    req.add_header("User-Agent", "minisight-skill/1.1")
    key = key or os.environ.get("MINISIGHT_API_KEY")
    token = token or os.environ.get("MINISIGHT_ACCESS_TOKEN")
    if key:
        req.add_header("X-API-Key", key)
    if token:
        req.add_header("Authorization", "Bearer " + token)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        try:
            detail = e.read().decode("utf-8", "replace")[:500]
        except Exception:
            detail = ""
        hint = {401: "密钥缺失或无效（检查 MINISIGHT_API_KEY）",
                403: "无权限访问该数据",
                404: "接口或资源不存在（细节见 references/api-*.md）",
                429: "免费额度已用完。明日自动恢复；完整数据与画布功能（连线推演/报告生成）请到 minisight.cn 注册使用"}.get(e.code, "")
        msg = f"HTTP {e.code} {url}" + (f"\n  {hint}" if hint else "") + (f"\n  {detail}" if detail else "")
        if soft:
            return {"_error": msg}
        fail(msg)
    except urllib.error.URLError as e:
        msg = f"网络错误：{e.reason}（检查 MINISIGHT_API_BASE 与网络）"
        if soft:
            return {"_error": msg}
        fail(msg)
    try:
        return json.loads(body)
    except json.JSONDecodeError:
        return {"_raw": body[:2000]}


def fail(msg):
    print(msg, file=sys.stderr)
    sys.exit(1)


def emit(data, limit=None, raw=False):
    if raw:
        print(json.dumps(data, ensure_ascii=False))
        return
    if limit is not None and isinstance(data, dict):
        for v in data.values():
            if isinstance(v, list) and len(v) > limit:
                data["_truncated"] = {"shown": limit, "total": len(v)}
                v[:] = v[:limit]
                break
    print(json.dumps(data, ensure_ascii=False, indent=2))


def trunc(s, n=200):
    return s if len(s) <= n else s[:n] + "…"


def _unwrap(resp):
    """剥掉 API 的 {code,message,data} 包装，返回业务数据。"""
    if isinstance(resp, dict) and isinstance(resp.get("data"), (dict, list)):
        return resp["data"]
    return resp


def build_weekly(base_kw, limit=None):
    """一键本周产业情报周报：聚合 新词窗口 + 替代技术 + 链主清单。子块失败互不影响。"""
    n_terms = limit or 8
    terms = _unwrap(http_get("research-worth/window", {"limit": n_terms}, soft=True, **base_kw))
    alt = _unwrap(http_get("components/tech-substitution", {"limit": limit or 8}, soft=True, **base_kw))
    leaders = _unwrap(http_get("components/chain-leaders/list", {"limit": limit or 10}, soft=True, **base_kw))

    out = {"cta": "深度研究（画布连线推演/框选提问/生成报告）请到 minisight.cn"}

    if "_error" not in terms:
        summary = terms.get("summary") or {}
        out["scan_summary"] = (f"近{summary.get('window_days', 7)}天扫描 "
                               f"{summary.get('report_count', '?')} 篇研报 · "
                               f"{summary.get('org_count', '?')} 家机构")
        out["week_of"] = terms.get("stat_date")
        words = []
        for key in ("words", "terms", "items"):
            if isinstance(terms.get(key), list):
                words = terms[key]
                break
        out["terms"] = [{"name": w.get("name"), "kind": w.get("kind"),
                         "org_cnt": w.get("org_cnt"), "new_org_cnt": w.get("new_org_cnt"),
                         "desc": trunc(w.get("description") or "", 90)} for w in words][:n_terms]
    else:
        out["terms_error"] = terms["_error"]

    if "_error" not in alt:
        routes = alt.get("routes") if isinstance(alt, dict) else alt
        out["alt_tech"] = [{"name": r.get("name"), "domain": r.get("domain"),
                            "maturity": r.get("maturity"),
                            "note": trunc(r.get("maturityNote") or r.get("description") or "", 90)}
                           for r in (routes or []) if isinstance(r, dict)][:limit or 8]
    else:
        out["alt_tech_error"] = alt["_error"]

    if "_error" not in leaders:
        rows = leaders.get("leaders") if isinstance(leaders, dict) else leaders
        out["chain_leaders"] = [{"companyName": r.get("companyName"), "chainName": r.get("chainName"),
                                 "leaderType": r.get("leaderType")}
                                for r in (rows or []) if isinstance(r, dict)][:limit or 10]
    else:
        out["chain_leaders_error"] = leaders["_error"]

    return out


def build_parser():
    # 全局参数通过 parents 同时挂到主解析器与每个子命令上，
    # 使 `ms.py search X --base ...` 与 `ms.py --base ... search X` 都合法
    glob = argparse.ArgumentParser(add_help=False)
    glob.add_argument("--base", help="API 根地址（默认读 MINISIGHT_API_BASE）")
    glob.add_argument("--key", help="API Key（默认读 MINISIGHT_API_KEY）")
    glob.add_argument("--token", help="JWT（默认读 MINISIGHT_ACCESS_TOKEN）")
    glob.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT)
    glob.add_argument("--raw", action="store_true", help="输出单行 JSON")
    p = argparse.ArgumentParser(prog="ms.py", description="MiniSight 产业研究 CLI", parents=[glob])
    sub = p.add_subparsers(dest="cmd", required=True)

    def mk(name, help_text):
        return sub.add_parser(name, help=help_text, parents=[glob])

    def common(sp, help_text):
        sp.description = help_text
        sp.add_argument("--limit", type=int, help="限制返回条数（列表类）")
        return sp

    common(mk("search", "全局搜索：企业/题材/设备/词条"), "全局搜索").add_argument("query")
    common(mk("industries", "产业列表（定链边界）"), "产业列表")
    mk("theme", "题材/主题详情").add_argument("theme_id")
    common(mk("devices", "设备列表（找锚定设备）"), "设备列表")
    mk("device", "设备详情与 BOM").add_argument("device_id")
    sp = common(mk("enterprise", "企业卡：上市地/市值/主营"), "企业详情")
    sp.add_argument("enterprise_id")
    sp.add_argument("--aliases", action="store_true", help="查企业别名")
    sp = common(mk("chain-leaders", "链主列表/链主事件动态"), "链主动态")
    sp.add_argument("--list", action="store_true", help="只看链主清单（先拿 leaderId）")
    sp.add_argument("--leader-id", help="按链主查事件（来自 --list 返回的 id）")
    sp = common(mk("alt-tech", "替代技术雷达"), "替代技术")
    sp.add_argument("--theme-id", help="按题材查替代技术（来自 theme 接口）")
    sp = common(mk("financial", "企业财务（三表/营收结构）"), "企业财务")
    sp.add_argument("company_id")
    sp = common(mk("earnings", "机构盈利预测"), "盈利预测")
    sp.add_argument("company_id")
    sp.add_argument("--details", action="store_true", help="拉明细")
    common(mk("terms", "值得研究词表窗口（找选题）"), "研究词表窗口")
    sp = common(mk("term", "词条详情/关联"), "研究词条")
    sp.add_argument("term_id")
    sp.add_argument("--assoc", action="store_true", help="拉关联关系")
    sp = common(mk("reports", "研报检索"), "研报检索")
    sp.add_argument("query")
    sp = common(mk("policies", "政策检索"), "政策检索")
    sp.add_argument("query")
    mk("compass", "宏观罗盘指标")
    common(mk("weekly", "一键本周产业情报周报（新词+替代技术+链主）"), "本周产业情报周报")
    sp = common(mk("openapi", "拉取实时接口清单（OpenAPI，仅本地调试环境可用）"), "接口清单")
    sp.add_argument("--grep", help="按关键词过滤路径")

    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    base_kw = {"base": args.base, "key": args.key, "token": args.token, "timeout": args.timeout}

    if args.cmd == "weekly":
        emit(build_weekly(base_kw, args.limit), raw=args.raw)
        return

    if args.cmd == "openapi":
        import re
        root = re.sub(r"/api/v[0-9]+$", "", (args.base or os.environ.get("MINISIGHT_API_BASE") or DEFAULT_BASE).rstrip("/"))
        url = root + "/openapi.json"
        try:
            with urllib.request.urlopen(url, timeout=args.timeout) as resp:
                body = resp.read().decode("utf-8", "replace")
        except Exception as e:
            fail(f"无法拉取 openapi.json：{e}")
        stripped = body.lstrip()[:200].lower()
        if stripped.startswith("<!doctype") or stripped.startswith("<html"):
            fail("当前环境（生产）不暴露接口清单。接口细节请参考技能包 references/api-*.md 文档。")
        try:
            spec = json.loads(body)
        except json.JSONDecodeError:
            fail("openapi.json 内容无法解析（可能被网关拦截），请参考 references/api-*.md 文档。")
        paths = spec.get("paths", {})
        if args.grep:
            paths = {k: v for k, v in paths.items() if args.grep.lower() in k.lower()}
        emit({"server": root, "path_count": len(paths), "paths": {k: sorted(v.keys()) for k, v in sorted(paths.items())}}, raw=args.raw)
        return

    if args.cmd == "search":
        emit(http_get("search", {"q": args.query, "limit": args.limit}, **base_kw), raw=args.raw)
    elif args.cmd == "industries":
        emit(http_get("industries", {"limit": args.limit}, **base_kw), limit=args.limit, raw=args.raw)
    elif args.cmd == "theme":
        emit(http_get(f"components/theme/{urllib.parse.quote(args.theme_id)}", None, **base_kw), raw=args.raw)
    elif args.cmd == "devices":
        emit(http_get("device", {"limit": args.limit}, **base_kw), limit=args.limit, raw=args.raw)
    elif args.cmd == "device":
        emit(http_get(f"device/{urllib.parse.quote(args.device_id)}", None, **base_kw), raw=args.raw)
    elif args.cmd == "enterprise":
        path = f"enterprise/{urllib.parse.quote(args.enterprise_id)}" + ("/aliases" if args.aliases else "")
        emit(http_get(path, None, **base_kw), raw=args.raw)
    elif args.cmd == "chain-leaders":
        if args.list:
            emit(http_get("components/chain-leaders/list", {"limit": args.limit}, **base_kw), limit=args.limit, raw=args.raw)
        else:
            emit(http_get("components/chain-leaders", {"leaderId": args.leader_id, "limit": args.limit}, **base_kw), limit=args.limit, raw=args.raw)
    elif args.cmd == "alt-tech":
        emit(http_get("components/tech-substitution", {"themeId": args.theme_id, "limit": args.limit}, **base_kw), limit=args.limit, raw=args.raw)
    elif args.cmd == "financial":
        emit(http_get(f"financial/company/{urllib.parse.quote(args.company_id)}", None, **base_kw), raw=args.raw)
    elif args.cmd == "earnings":
        if args.details:
            emit(http_get(f"components/earnings-forecast/{urllib.parse.quote(args.company_id)}/details", None, **base_kw), raw=args.raw)
        else:
            emit(http_get("components/earnings-forecast", {"limit": args.limit}, **base_kw), limit=args.limit, raw=args.raw)
    elif args.cmd == "terms":
        emit(http_get("research-worth/window", {"limit": args.limit}, **base_kw), limit=args.limit, raw=args.raw)
    elif args.cmd == "term":
        path = f"research-worth/term/{urllib.parse.quote(args.term_id)}" + ("/associations" if args.assoc else "")
        emit(http_get(path, None, **base_kw), raw=args.raw)
    elif args.cmd == "reports":
        emit(http_get("reports/search", {"q": args.query, "limit": args.limit}, **base_kw), limit=args.limit, raw=args.raw)
    elif args.cmd == "policies":
        emit(http_get("policies/search", {"q": args.query, "limit": args.limit}, **base_kw), limit=args.limit, raw=args.raw)
    elif args.cmd == "compass":
        emit(http_get("components/macro/compass", None, **base_kw), raw=args.raw)


if __name__ == "__main__":
    main()
