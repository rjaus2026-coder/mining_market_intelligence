#!/usr/bin/env python3

from __future__ import annotations

from typing import Any


def _strip_comments(line: str) -> str:
    in_single = False
    in_double = False
    escaped = False
    out = []
    for ch in line:
        if ch == "\\" and not escaped:
            escaped = True
            out.append(ch)
            continue
        if ch == "'" and not in_double and not escaped:
            in_single = not in_single
        elif ch == '"' and not in_single and not escaped:
            in_double = not in_double
        elif ch == "#" and not in_single and not in_double:
            break
        out.append(ch)
        escaped = False
    return "".join(out).rstrip()


def _parse_scalar(value: str) -> Any:
    value = value.strip()
    if value == "":
        return ""
    if value in ("true", "True"):
        return True
    if value in ("false", "False"):
        return False
    if value in ("null", "Null", "none", "None", "~"):
        return None
    if value.startswith('"') and value.endswith('"'):
        return value[1:-1]
    if value.startswith("'") and value.endswith("'"):
        return value[1:-1]
    if value.lstrip("-").isdigit():
        return int(value)
    return value


def _preprocess(text: str) -> list[tuple[int, str]]:
    lines = []
    for raw in text.splitlines():
        stripped = _strip_comments(raw)
        if not stripped.strip():
            continue
        indent = len(stripped) - len(stripped.lstrip(" "))
        lines.append((indent, stripped.strip()))
    return lines


def _parse_mapping_entry(content: str) -> tuple[str, str | None]:
    if ":" not in content:
        raise ValueError(f"Expected mapping entry, got: {content}")
    key, value = content.split(":", 1)
    value = value.strip()
    return key.strip(), value if value != "" else None


def _parse_list_item(lines: list[tuple[int, str]], index: int, indent: int) -> tuple[Any, int]:
    item_indent, content = lines[index]
    if item_indent != indent or not content.startswith("- "):
        raise ValueError("Invalid list item")

    payload = content[2:].strip()
    index += 1

    if payload == "":
        nested, index = _parse_block(lines, index, indent + 2)
        return nested, index

    if ":" in payload:
        key, value = _parse_mapping_entry(payload)
        item: dict[str, Any] = {}
        item[key] = _parse_scalar(value) if value is not None else None
        while index < len(lines):
            next_indent, next_content = lines[index]
            if next_indent < indent + 2:
                break
            if next_indent == indent and next_content.startswith("- "):
                break
            if next_indent > indent + 2:
                raise ValueError(f"Unexpected indentation: {next_content}")
            sub_key, sub_value = _parse_mapping_entry(next_content)
            index += 1
            if sub_value is None:
                nested, index = _parse_block(lines, index, next_indent + 2)
                item[sub_key] = nested
            else:
                item[sub_key] = _parse_scalar(sub_value)
        return item, index

    return _parse_scalar(payload), index


def _parse_block(lines: list[tuple[int, str]], index: int, indent: int) -> tuple[Any, int]:
    if index >= len(lines):
        return {}, index

    current_indent, current_content = lines[index]
    if current_indent < indent:
        return {}, index

    if current_indent == indent and current_content.startswith("- "):
        items = []
        while index < len(lines):
            next_indent, next_content = lines[index]
            if next_indent != indent or not next_content.startswith("- "):
                break
            item, index = _parse_list_item(lines, index, indent)
            items.append(item)
        return items, index

    mapping: dict[str, Any] = {}
    while index < len(lines):
        next_indent, next_content = lines[index]
        if next_indent < indent:
            break
        if next_indent > indent:
            raise ValueError(f"Unexpected indentation: {next_content}")
        if next_content.startswith("- "):
            break
        key, value = _parse_mapping_entry(next_content)
        index += 1
        if value is None:
            nested, index = _parse_block(lines, index, indent + 2)
            mapping[key] = nested
        else:
            mapping[key] = _parse_scalar(value)
    return mapping, index


def safe_load(text: str) -> Any:
    lines = _preprocess(text)
    if not lines:
        return {}
    data, index = _parse_block(lines, 0, lines[0][0])
    if index != len(lines):
        raise ValueError("Could not parse entire YAML document")
    return data
