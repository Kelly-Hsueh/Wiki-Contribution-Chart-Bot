from __future__ import annotations

from typing import Any


def fetch_namespaces(
    session: Any,
    wiki_api: str,
    timeout: int,
) -> dict[int, str]:
    """从 MediaWiki API 获取命名空间名称映射。

    Args:
        session: requests.Session 对象
        wiki_api: MediaWiki API 端点
        timeout: 请求超时时间（秒）

    Returns:
        映射 {ns_id: namespace_name} 的字典
        其中 ns_id=0 对应主命名空间，会被标记为"（主）"

    Raises:
        RuntimeError: 如果 API 请求失败或响应格式异常
    """
    from mw_runtime import api_get_json

    params = {
        "action": "query",
        "format": "json",
        "meta": "siteinfo",
        "formatversion": 2,
        "siprop": "namespaces",
    }

    try:
        data = api_get_json(
            session=session,
            wiki_api=wiki_api,
            params=params,
            timeout=timeout,
            error_context="获取命名空间信息失败",
        )
    except RuntimeError as exc:
        raise RuntimeError(f"无法从 API 获取命名空间: {exc}") from exc

    namespaces_data = data.get("query", {}).get("namespaces", {})
    if not namespaces_data:
        raise RuntimeError("API 响应中未包含 namespaces 数据")

    namespace_map: dict[int, str] = {}

    for ns_key, ns_info in namespaces_data.items():
        try:
            ns_id = int(ns_key)
        except ValueError:
            continue

        if not isinstance(ns_info, dict):
            continue

        # formatversion=2 使用 "name" 字段（而非 formatversion=1 的 "*" 字段）
        ns_name = ns_info.get("name", "")

        # MediaWiki API 对主命名空间返回空字符串，我们将其转换为"（主）"
        if ns_id == 0 and not ns_name:
            namespace_map[ns_id] = "（主）"
        elif ns_name:
            namespace_map[ns_id] = ns_name

    return namespace_map
