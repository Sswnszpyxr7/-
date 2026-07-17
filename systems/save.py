# -*- coding: utf-8 -*-
"""存档读档系统：原子写入、备份、版本与旧档兼容。"""
import copy
import json
import os
import shutil
from datetime import datetime, timezone

from systems import ui

SAVE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "saves")
SLOTS = 3
SAVE_SCHEMA_VERSION = 7
PROFILE_SCHEMA_VERSION = 1


class SaveError(RuntimeError):
    """存档无法安全读写。"""


def set_save_dir(path):
    """为测试或独立运行设置存档目录。"""
    global SAVE_DIR
    SAVE_DIR = os.path.abspath(os.fspath(path))


def _validate_slot(slot):
    if not isinstance(slot, int) or not 1 <= slot <= SLOTS:
        raise ValueError(f"存档槽位必须为 1-{SLOTS}")


def _slot_path(slot):
    _validate_slot(slot)
    return os.path.join(SAVE_DIR, f"save_{slot:02d}.json")


def _backup_path(path):
    return f"{path}.bak"


def _profile_path():
    return os.path.join(SAVE_DIR, "collection_profile.json")


def load_profile(state):
    """合并跨存档共享的图鉴、成就与结局收集。"""
    path = _profile_path()
    if not os.path.exists(path):
        return False
    try:
        with open(path, "r", encoding="utf-8") as file:
            data = json.load(file)
        state.discovered_enemies = list(
            dict.fromkeys([*state.discovered_enemies, *data.get("discovered_enemies", [])])
        )
        state.discovered_characters = list(
            dict.fromkeys([*state.discovered_characters, *data.get("discovered_characters", [])])
        )
        state.discovered_skills = list(
            dict.fromkeys([*state.discovered_skills, *data.get("discovered_skills", [])])
        )
        state.achievements = list(dict.fromkeys([*state.achievements, *data.get("achievements", [])]))
        state.endings_seen = list(dict.fromkeys([*state.endings_seen, *data.get("endings_seen", [])]))
        return True
    except (OSError, json.JSONDecodeError, TypeError):
        return False


def _save_profile(state):
    path = _profile_path()
    temp_path = f"{path}.tmp"
    existing = {
        "discovered_characters": [],
        "discovered_enemies": [],
        "discovered_skills": [],
        "achievements": [],
        "endings_seen": [],
    }
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as file:
                existing.update(json.load(file))
        except (OSError, json.JSONDecodeError, TypeError):
            pass
    payload = {
        "schema_version": PROFILE_SCHEMA_VERSION,
        "discovered_characters": list(
            dict.fromkeys([*existing.get("discovered_characters", []), *state.discovered_characters])
        ),
        "discovered_enemies": list(
            dict.fromkeys([*existing.get("discovered_enemies", []), *state.discovered_enemies])
        ),
        "discovered_skills": list(
            dict.fromkeys([*existing.get("discovered_skills", []), *state.discovered_skills])
        ),
        "achievements": list(dict.fromkeys([*existing.get("achievements", []), *state.achievements])),
        "endings_seen": list(dict.fromkeys([*existing.get("endings_seen", []), *state.endings_seen])),
    }
    with open(temp_path, "w", encoding="utf-8", newline="\n") as file:
        json.dump(payload, file, ensure_ascii=False, indent=2)
        file.flush()
        os.fsync(file.fileno())
    os.replace(temp_path, path)


def _payload(state):
    from systems import collection

    collection.refresh(state)
    data = copy.deepcopy(state.to_dict())
    data["_meta"] = {
        "schema_version": SAVE_SCHEMA_VERSION,
        "saved_at": datetime.now(timezone.utc).isoformat(),
    }
    return data


def save_game(state, slot=1, silent=False):
    """先写临时文件，成功后原子替换正式存档。"""
    path = _slot_path(slot)
    temp_path = f"{path}.tmp"
    backup_path = _backup_path(path)
    try:
        os.makedirs(SAVE_DIR, exist_ok=True)
        with open(temp_path, "w", encoding="utf-8", newline="\n") as file:
            json.dump(_payload(state), file, ensure_ascii=False, indent=2)
            file.flush()
            os.fsync(file.fileno())
        if os.path.exists(path):
            shutil.copy2(path, backup_path)
        os.replace(temp_path, path)
        try:
            _save_profile(state)
        except OSError:
            # 主存档已成功落盘；收藏档失败不应伪装成主存档失败。
            pass
    except (OSError, TypeError, ValueError) as exc:
        try:
            if os.path.exists(temp_path):
                os.remove(temp_path)
        except OSError:
            pass
        raise SaveError(f"无法写入存档 {slot}: {exc}") from exc
    if not silent:
        ui.slow_print(f"※ 已保存到存档 {slot}。")


def _read_payload(path):
    with open(path, "r", encoding="utf-8") as file:
        data = json.load(file)
    if not isinstance(data, dict):
        raise SaveError("存档根节点不是对象")
    version = data.get("_meta", {}).get("schema_version", 1)
    if version > SAVE_SCHEMA_VERSION:
        raise SaveError(f"存档版本 {version} 高于当前支持版本 {SAVE_SCHEMA_VERSION}")
    return data


def load_game(state, slot=1):
    path = _slot_path(slot)
    if not os.path.exists(path):
        ui.slow_print("该存档不存在。")
        return False

    source = path
    try:
        data = _read_payload(path)
    except (OSError, json.JSONDecodeError, SaveError, TypeError) as primary_error:
        backup = _backup_path(path)
        if not os.path.exists(backup):
            ui.slow_print(f"存档损坏或无法读取: {primary_error}")
            return False
        try:
            data = _read_payload(backup)
            source = backup
        except (OSError, json.JSONDecodeError, SaveError, TypeError) as backup_error:
            ui.slow_print(f"存档与备份都无法读取: {backup_error}")
            return False

    try:
        state.from_dict(data)
    except (KeyError, TypeError, ValueError) as exc:
        ui.slow_print(f"存档内容不完整: {exc}")
        return False
    load_profile(state)
    if source != path:
        ui.slow_print(f"※ 主存档损坏，已从备份恢复存档 {slot}。")
    else:
        ui.slow_print(f"※ 已读取存档 {slot}。")
    return True


def _describe(path):
    try:
        data = _read_payload(path)
        player = data["player"]
        return f"Lv.{player['level']} 鸣人 | 第{data['chapter']}章 | 命运点 {data['fate_points']}"
    except (OSError, json.JSONDecodeError, SaveError, KeyError, TypeError):
        backup = _backup_path(path)
        if os.path.exists(backup):
            return "(主存档损坏，有可用备份)"
        return "(损坏的存档)"


def list_slots():
    """返回 ``[(slot, 描述或 None)]``。"""
    result = []
    for slot in range(1, SLOTS + 1):
        path = _slot_path(slot)
        result.append((slot, _describe(path) if os.path.exists(path) else None))
    return result


def save_menu(state):
    slots = list_slots()
    options = [f"存档 {slot}: {description or '空'}" for slot, description in slots]
    index = ui.choose("选择存档位置:", options, allow_cancel=True)
    if index >= 0:
        try:
            save_game(state, slots[index][0])
        except SaveError as exc:
            ui.slow_print(str(exc))


def load_menu(state):
    slots = list_slots()
    options = [f"存档 {slot}: {description or '空'}" for slot, description in slots]
    index = ui.choose("选择要读取的存档:", options, allow_cancel=True)
    if index >= 0 and slots[index][1]:
        return load_game(state, slots[index][0])
    if index >= 0:
        ui.slow_print("该存档为空。")
    return False
