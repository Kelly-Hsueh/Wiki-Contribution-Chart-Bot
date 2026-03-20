from __future__ import annotations


def build_namespace_name(ns_id: int) -> str:
    return "（主）" if ns_id == 0 else f"{{{{ns:{ns_id}}}}}"


def build_excluded_namespaces_text(
    excluded_namespaces: set[int], is_auto_inferred: bool = False
) -> str:
    if not excluded_namespaces:
        return "未排除任何命名空间"

    if is_auto_inferred:
        # 自动推断时的特殊格式：显示 ns=2 和奇数命名空间
        return "已排除{{ns:2}}、各奇数〔{{ns:1}}〕命名空间"

    sorted_ids = sorted(excluded_namespaces)
    preview_count = 3
    preview_labels = [
        build_namespace_name(ns_id) for ns_id in sorted_ids[:preview_count]
    ]
    if len(sorted_ids) <= preview_count:
        return "已排除：" + "、".join(preview_labels)

    return ("已排除：" + "、".join(preview_labels) + f" 等{len(sorted_ids)}个命名空间")
