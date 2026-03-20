from __future__ import annotations

from collections import Counter
from datetime import datetime
from typing import Any

from chart_styles.utils import build_excluded_namespaces_text


def _group_by_month_and_account(
    accounts_contribs: dict[str, list[dict[str, Any]]],
) -> tuple[list[tuple[int, int]], dict[str, list[int]], list[str]]:
    """按月份和账户分组统计编辑数。

    Args:
        accounts_contribs: 键为用户名，值为该用户的贡献列表的字典

    Returns:
        (sorted_months, account_month_counts, account_order)
        - sorted_months: 排序后的 (year, month) 元组列表
        - account_month_counts: 键为用户名，值为[按月计数]列表的字典
        - account_order: 按 WIKI_USER 中的顺序排列的用户名列表
    """
    monthly_account_counter: Counter[tuple[int, int, str]] = Counter()
    month_counter: Counter[tuple[int, int]] = Counter()
    account_totals: Counter[str] = Counter()

    for account, contribs in accounts_contribs.items():
        for item in contribs:
            timestamp = item.get("timestamp")
            if not isinstance(timestamp, str):
                continue

            try:
                dt = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ")
            except ValueError:
                continue

            key = (dt.year, dt.month, account)
            monthly_account_counter[key] += 1
            month_counter[(dt.year, dt.month)] += 1
            account_totals[account] += 1

    if not month_counter:
        return [], {}, []

    sorted_months = sorted(month_counter.keys())
    start_year, start_month = sorted_months[0]
    end_year, end_month = sorted_months[-1]

    full_months: list[tuple[int, int]] = []
    year, month = start_year, start_month
    while (year, month) <= (end_year, end_month):
        full_months.append((year, month))
        month += 1
        if month > 12:
            month = 1
            year += 1

    # 保持 WIKI_USER 中的用户顺序（account_order 会在调用时传入）
    account_month_counts: dict[str, list[int]] = {
        account: [
            monthly_account_counter.get((year, month, account), 0)
            for year, month in full_months
        ]
        for account in accounts_contribs
    }

    return full_months, account_month_counts, list(accounts_contribs.keys())


def _build_series_style() -> dict[str, Any]:
    return {
        "showSymbol": False,
        "lineStyle": {
            "width": 1.8,
        },
        "areaStyle": {
            "opacity": 0.16,
        },
        "barMaxWidth": 28,
    }


def build_option(
    display_name: str,
    accounts_contribs: dict[str, list[dict[str, Any]]],
    generated_time: str,
    chart_series_type: str,
    account_order: list[str],
    excluded_namespaces: set[int] | None = None,
    is_auto_inferred_namespaces: bool = False,
    namespace_map: dict[int, str] | None = None,
) -> dict[str, Any]:
    """构建按账户堆叠的图表选项。

    Args:
        display_name: 图表显示名称
        accounts_contribs: 键为用户名，值为该用户的贡献列表的字典
        generated_time: 生成时间字符串
        chart_series_type: 图表类型 (bar 或 line)
        account_order: 账户在图表中的显示顺序
        excluded_namespaces: 被排除的命名空间集合（用于显示信息）
        is_auto_inferred_namespaces: 是否为自动推断的排除命名空间
        namespace_map: 命名空间映射（用于显示名称）
    """
    if excluded_namespaces is None:
        excluded_namespaces = set()

    full_months, account_month_counts, _ = _group_by_month_and_account(
        accounts_contribs)

    x_labels = [f"{year}年{month}月" for year, month in full_months]

    # 按指定顺序构建图表系列
    legend_data: list[str] = []
    series: list[dict[str, Any]] = []

    for account in account_order:
        if account not in account_month_counts:
            continue

        legend_data.append(account)
        series.append({
            "name": account,
            "type": chart_series_type,
            "stack": "Total",
            "emphasis": {
                "focus": "series"
            },
            "data": account_month_counts.get(account, [0] * len(x_labels)),
            **_build_series_style(),
        })

    excluded_ns_text = build_excluded_namespaces_text(
        excluded_namespaces, namespace_map, is_auto_inferred_namespaces
    )
    subtext = (
        "按月按账户统计\n"
        f"{excluded_ns_text}\n"
        f"（截至 {generated_time}）"
    )

    return {
        "__WARNING__":
        "!!! DON'T MODIFY THIS PAGE MANUALLY, YOUR CHANGES WILL BE OVERWRITTEN !!!",
        "title": {
            "text": f"{display_name}的编辑历史",
            "subtext": subtext,
            "top": 8,
            "left": "center",
            "itemGap": 10,
            "subtextStyle": {
                "lineHeight": 18
            }
        },
        "grid": {
            "top": 150,
            "left": "10%",
            "right": "10%",
            "bottom": 95,
            "containLabel": True
        },
        "tooltip": {
            "trigger": "axis",
            "axisPointer": {
                "type": "cross",
                "animation": False
            }
        },
        "toolbox": {
            "show": True,
            "feature": {
                "dataZoom": {
                    "yAxisIndex": "none"
                },
                "magicType": {
                    "type": ["line", "bar"],
                    "option": {
                        "line": {
                            "xAxis": {
                                "boundaryGap": False
                            },
                            "series": [{
                                "showSymbol": False,
                                "areaStyle": {
                                    "opacity": 0.16,
                                }
                            }]
                        },
                        "bar": {
                            "xAxis": {
                                "boundaryGap": True
                            },
                            "series": [{
                                "barMaxWidth": 28,
                            }]
                        }
                    }
                },
                "restore": {},
                "saveAsImage": {
                    "excludeComponents": ["toolbox", "dataZoom"]
                }
            }
        },
        "axisPointer": {
            "link": {
                "xAxisIndex": "all"
            }
        },
        "dataZoom": [{
            "type": "inside",
            "xAxisIndex": [0],
            "startValue": 0,
            "end": 100
        }, {
            "show": True,
            "xAxisIndex": [0],
            "type": "slider",
            "bottom": 10,
            "start": 0,
            "end": 100
        }],
        "legend": {
            "type": "scroll",
            "top": 100,
            "left": "center",
            "right": "10%",
            "data": legend_data
        },
        "xAxis": {
            "type": "category",
            "boundaryGap": chart_series_type == "bar",
            "data": x_labels
        },
        "yAxis": {
            "type": "value"
        },
        "series": series,
        "animation": False
    }
