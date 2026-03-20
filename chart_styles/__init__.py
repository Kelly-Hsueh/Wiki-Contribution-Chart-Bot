from __future__ import annotations

from typing import Any, Literal

from chart_styles.sum_style import build_option as build_sum_option
from chart_styles.namespace_style import build_option as build_namespace_option
from chart_styles.account_style import build_option as build_account_option

ChartStyle = Literal["namespace", "sum", "account"]

_SUPPORTED_CHART_STYLES: set[str] = {"namespace", "sum", "account"}


def parse_chart_style(raw_value: str) -> ChartStyle:
    value = raw_value.strip().lower()
    if not value:
        return "namespace"
    if value not in _SUPPORTED_CHART_STYLES:
        raise RuntimeError(
            "环境变量 CHART_STYLE 仅支持 namespace、sum 或 account，"
            "例如 CHART_STYLE=namespace")
    return value  # type: ignore[return-value]


def build_option_for_style(
    chart_style: ChartStyle,
    display_name: str,
    contribs: list[dict[str, Any]],
    generated_time: str,
    chart_series_type: str,
    excluded_namespaces: set[int],
    namespace_mode: str,
    top_namespace_limit: int,
    namespace_map: dict[int, str] | None = None,
    is_auto_inferred_namespaces: bool = False,
    accounts_contribs: dict[str, list[dict[str, Any]]] | None = None,
    account_order: list[str] | None = None,
) -> dict[str, Any]:
    if chart_style == "account":
        if accounts_contribs is None or account_order is None:
            raise RuntimeError("account 模式需要提供 accounts_contribs 和 account_order 参数")
        return build_account_option(
            display_name=display_name,
            accounts_contribs=accounts_contribs,
            generated_time=generated_time,
            chart_series_type=chart_series_type,
            account_order=account_order,
            excluded_namespaces=excluded_namespaces,
            is_auto_inferred_namespaces=is_auto_inferred_namespaces,
            namespace_map=namespace_map,
        )

    if chart_style == "sum":
        return build_sum_option(
            display_name=display_name,
            contribs=contribs,
            generated_time=generated_time,
            chart_series_type=chart_series_type,
            excluded_namespaces=excluded_namespaces,
            namespace_mode=namespace_mode,
            top_namespace_limit=top_namespace_limit,
            namespace_map=namespace_map,
            is_auto_inferred_namespaces=is_auto_inferred_namespaces,
        )

    return build_namespace_option(
        display_name=display_name,
        contribs=contribs,
        generated_time=generated_time,
        chart_series_type=chart_series_type,
        excluded_namespaces=excluded_namespaces,
        namespace_mode=namespace_mode,
        top_namespace_limit=top_namespace_limit,
        namespace_map=namespace_map,
        is_auto_inferred_namespaces=is_auto_inferred_namespaces,
    )
