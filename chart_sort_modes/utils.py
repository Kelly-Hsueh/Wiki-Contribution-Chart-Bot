from __future__ import annotations

from datetime import datetime
from typing import Any

from chart_sort_modes import (
    DEFAULT_ACCOUNT_REG_MARKER_OUT_OF_RANGE,
    REGISTRATION_MARKER_COLOR,
    REGISTRATION_MARKER_SYMBOL,
)


def build_namespace_name(ns_id: int, namespace_map: dict[int, str] | None = None) -> str:
    """根据命名空间 ID 获取显示名称。

    Args:
        ns_id: 命名空间 ID
        namespace_map: 命名空间映射（从 API 获取）。如果为 None，则使用占位符格式。

    Returns:
        命名空间的显示名称
    """
    if namespace_map and ns_id in namespace_map:
        return namespace_map[ns_id]

    # 降级处理：当没有 namespace_map 时使用占位符
    return "（主）" if ns_id == 0 else f"ns:{ns_id}"


def build_excluded_namespaces_text(
    excluded_namespaces: set[int],
    namespace_map: dict[int, str] | None = None,
    is_auto_inferred: bool = False,
) -> str:
    """构建排除命名空间的文本说明。

    Args:
        excluded_namespaces: 排除的命名空间 ID 集合
        namespace_map: 命名空间映射（从 API 获取）。
        is_auto_inferred: 是否为自动推断的排除命名空间

    Returns:
        排除命名空间的文本说明
    """
    if not excluded_namespaces:
        return "未排除任何命名空间"

    if is_auto_inferred:
        # 自动推断时的特殊格式：显示 ns=2 和奇数命名空间
        ns_2_name = build_namespace_name(2, namespace_map)
        ns_1_name = build_namespace_name(1, namespace_map)
        return f"已排除{ns_2_name}、各奇数〔{ns_1_name}〕命名空间"

    sorted_ids = sorted(excluded_namespaces)
    preview_count = 3
    preview_labels = [
        build_namespace_name(ns_id, namespace_map)
        for ns_id in sorted_ids[:preview_count]
    ]
    if len(sorted_ids) <= preview_count:
        return "已排除：" + "、".join(preview_labels)

    excluded_text = "、".join(preview_labels)
    return f"已排除：{excluded_text} 等{len(sorted_ids)}个命名空间"


def build_registration_scatter_series(
    x_labels: list[str],
    full_months: list[tuple[int, int]],
    account_registrations: dict[str, str] | None = None,
    account_order: list[str] | None = None,
    out_of_range_strategy: str = DEFAULT_ACCOUNT_REG_MARKER_OUT_OF_RANGE,
) -> dict[str, Any] | None:
    """构建通用注册时间散点系列。"""
    if not account_registrations or not x_labels or not full_months:
        return None

    start_year, start_month = full_months[0]
    ordered_accounts = account_order or list(account_registrations.keys())
    registration_scatter_data: list[dict[str, Any]] = []

    for account_name in ordered_accounts:
        registration_iso = account_registrations.get(account_name)
        if not registration_iso:
            continue

        try:
            reg_dt = datetime.strptime(registration_iso, "%Y-%m-%dT%H:%M:%SZ")
            reg_year, reg_month, reg_day = reg_dt.year, reg_dt.month, reg_dt.day
        except ValueError:
            continue

        if (reg_year, reg_month) < (start_year, start_month):
            if out_of_range_strategy == "hide":
                continue
            if out_of_range_strategy != "clamp_to_first":
                continue
            month_idx = 0
            display_date = (
                f"{reg_year}年{reg_month:02d}月{reg_day:02d}日（早于统计区间）"
            )
        else:
            try:
                month_idx = full_months.index((reg_year, reg_month))
            except ValueError:
                continue
            display_date = f"{reg_month:02d}月{reg_day:02d}日"

        registration_scatter_data.append({
            "name": f"{account_name} 注册时间",
            "value": [x_labels[month_idx], 0],
            "tooltip": {
                "formatter": f"{account_name}<br/>注册于{display_date}",
                "position": "top",
            },
        })

    if not registration_scatter_data:
        return None

    return {
        "name": "注册时间",
        "type": "scatter",
        "symbol": REGISTRATION_MARKER_SYMBOL,
        "symbolSize": 12,
        "symbolOffset": [0, "60%"],
        "data": registration_scatter_data,
        "color": REGISTRATION_MARKER_COLOR,
        "itemStyle": {
            "color": REGISTRATION_MARKER_COLOR,
        },
        "tooltip": {
            "trigger": "item",
            "position": "top",
        },
    }
