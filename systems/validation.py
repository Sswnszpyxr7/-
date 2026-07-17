# -*- coding: utf-8 -*-
"""游戏数据完整性校验。"""


class DataValidationError(ValueError):
    """游戏数据存在无法安全运行的引用错误。"""


def _validate_extended_systems(state, errors):
    from systems import contract, crafting, equipment, factions, party

    for recipe_id, recipe in crafting.RECIPES.items():
        if recipe.get("equipment") and recipe["equipment"] not in equipment.CATALOG:
            errors.append(f"配方 {recipe_id} 引用了不存在的忍具 {recipe['equipment']}")
        if recipe.get("equipment") and recipe.get("item"):
            errors.append(f"配方 {recipe_id} 同时定义了忍具与道具产物")
        unknown_materials = set(recipe.get("materials", {})) - crafting.MATERIALS
        if unknown_materials:
            errors.append(f"配方 {recipe_id} 使用未知素材 {sorted(unknown_materials)}")
    if set(state.faction_reputation) != set(factions.FACTIONS):
        errors.append("阵营声望状态与阵营目录不一致")
    if any(teammate_id not in party.TEAMMATES for teammate_id in state.selected_party):
        errors.append("当前队伍包含不存在的队友")
    story_ids = [quest["id"] for chain in factions.FACTION_CHAINS.values() for quest in chain]
    if len(story_ids) != len(set(story_ids)):
        errors.append("阵营故事任务存在重复 id")
    for faction_id, rewards in factions.RANK_REWARDS.items():
        if faction_id not in factions.FACTIONS:
            errors.append(f"声望奖励引用不存在的阵营 {faction_id}")
        for reward in rewards.values():
            if reward.get("gear") and reward["gear"] not in equipment.CATALOG:
                errors.append(f"声望奖励引用不存在的忍具 {reward['gear']}")
    if set(party.TEAMMATE_ROUTES) != set(party.TEAMMATES):
        errors.append("队友成长路线与队友目录不一致")
    if set(contract.TRIAL_THEMES) != set(state.contracts):
        errors.append("契约试炼主题与契约目录不一致")


def validate_game_state(state):
    """验证 JSON 数据中的关键交叉引用，返回警告列表。"""
    errors = []
    warnings = []

    skills = state.skills_db
    actors = [("player", state.player)]
    actors.extend((f"enemy:{enemy_id}", enemy) for enemy_id, enemy in state.enemies_db.items())
    for owner, actor in actors:
        for skill_id in actor.get("skills", []):
            if skill_id not in skills:
                errors.append(f"{owner} 引用了不存在的技能 {skill_id}")

    for map_id, location in state.maps.items():
        if location.get("id", map_id) != map_id:
            errors.append(f"地图键与 id 不一致: {map_id}")
        for destination in location.get("exits", location.get("connections", [])):
            if destination not in state.maps:
                errors.append(f"地图 {map_id} 指向不存在的地点 {destination}")

    for contract_id, contract in state.contracts.items():
        if contract.get("id") != contract_id:
            errors.append(f"契约键与 id 不一致: {contract_id}")

    for quest_id, quest in state.quests.items():
        if quest.get("id") != quest_id:
            errors.append(f"任务键与 id 不一致: {quest_id}")

    for skill_id, skill in skills.items():
        if skill.get("id", skill_id) != skill_id:
            warnings.append(f"技能键与 id 不一致: {skill_id}")

    from systems import world_events

    _validate_extended_systems(state, errors)

    event_ids = set()
    event_counts = {map_id: 0 for map_id in state.maps}
    for event in world_events.EVENTS:
        if event["id"] in event_ids:
            errors.append(f"重复的随机事件 id: {event['id']}")
        event_ids.add(event["id"])
        if event["location"] not in state.maps:
            errors.append(f"随机事件 {event['id']} 引用不存在的地点 {event['location']}")
        else:
            event_counts[event["location"]] += 1
    chain_ids = [chain_id for chain_id, _, _, _ in world_events.CHAIN_DEFS]
    if len(chain_ids) != len(set(chain_ids)):
        errors.append("地点连续事件存在重复 chain id")
    for chain_id, location, _, stages in world_events.CHAIN_DEFS:
        if location not in state.maps:
            errors.append(f"地点连续事件 {chain_id} 引用不存在的地图 {location}")
        if len(stages) != 3:
            errors.append(f"地点连续事件 {chain_id} 必须包含三个阶段")
    for map_id, count in event_counts.items():
        if count < 2:
            warnings.append(f"地点 {map_id} 的随机事件少于 2 个")

    if errors:
        raise DataValidationError("\n".join(errors))
    return warnings
