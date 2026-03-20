from __future__ import annotations


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
