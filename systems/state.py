# -*- coding: utf-8 -*-
"""游戏全局状态：玩家、契约、任务、命运、关系、标记。"""
import copy
import json
import os

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")

REL_NAMES = {
    "sasuke": {
        "trust": "信任鸣人", "revenge": "复仇执念", "curse": "咒印侵蚀",
        "team_bond": "第七班羁绊", "isolation": "孤立感",
    },
    "sakura": {
        "confidence": "自信", "medical": "医疗兴趣", "trust": "对鸣人信任",
        "sasuke_obsession": "对佐助执念", "responsibility": "第七班责任感",
    },
}

CHAR_NAMES = {"sasuke": "佐助", "sakura": "小樱"}


def _load_json(name):
    with open(os.path.join(DATA_DIR, name), "r", encoding="utf-8") as f:
        return json.load(f)


class GameState:
    """整个游戏的可存档状态。"""

    def __init__(self):
        chars = _load_json("characters.json")
        self.skills_db = _load_json("skills.json")
        self.maps = _load_json("maps.json")
        self.enemies_db = chars["enemies"]

        self.player = copy.deepcopy(chars["naruto"])
        self.contracts = _load_json("contracts.json")
        self.quests = _load_json("quests.json")

        self.location = "naruto_home"
        self.fate_points = 0
        self.backlash = 0            # 命运反噬等级 0-6
        self.exposure = 0            # 暴露度
        self.kakashi_suspicion = 0   # 卡卡西怀疑值
        self.team7_trust = 0         # 第七班信任度
        self.village_trust = 0       # 木叶信任(村民与高层的态度,佩恩篇关键)
        self.belonging = 10          # 归属感
        self.kyubi_flux = 0          # 九尾波动
        self.inventory = {"军粮丸": 2, "回复丹": 1}
        self.ryo = 500
        self.chapter = 1
        self.world_day = 1
        self.time_index = 0
        self.actions_taken = 0
        # 可重复的非战斗收益按游戏日记账，避免切换菜单/反复进出场景刷资源。
        # {activity_key: {"day": int, "count": int}}
        self.daily_activity = {}
        self.tougen_training_sessions = 0
        self.equipped_skills = list(self.player.get("skills", []))[:6]
        self.skill_upgrades = {}
        self.owned_equipment = ["kunai_kit", "genin_vest"]
        self.equipped_gear = {"weapon": "kunai_kit", "armor": "genin_vest", "accessory": ""}
        self.equipment_quality = {"kunai_kit": "common", "genin_vest": "common"}
        self.equipment_enhancements = {}
        self.equipment_affixes = {}
        self.wanted_records = {}
        self.new_game_plus = 0
        self.challenge_modifiers = []
        self.selected_party = []
        # 队友拥有独立成长；未出战角色会在首次可用时补建默认记录。
        self.teammate_progress = {}
        # 联合技实战熟练度：{combo_id: {uses, level, exp}}。
        self.combo_mastery = {}
        # 动态委托与阵营声望。
        self.faction_reputation = {"konoha": 0, "suna": 0, "alliance": 0}
        self.dynamic_quests = {}
        self.dynamic_quest_serial = 0
        self.last_dynamic_refresh_day = 0
        self.faction_story = {}
        self.faction_rank_rewards = []
        self.random_event_history = {}
        self.random_event_last_seen = {}
        self.world_event_chains = {}
        self.contract_trials = []
        self.discovered_characters = []
        self.discovered_enemies = []
        self.discovered_skills = []
        self.achievements = []
        self.endings_seen = []
        # 重要角色关系数值 (设计文档 §21.2 / §21.3)
        self.relations = {
            "sasuke": {"trust": 10, "revenge": 70, "curse": 0,
                       "team_bond": 5, "isolation": 80},
            "sakura": {"confidence": 30, "medical": 10, "trust": 10,
                       "sasuke_obsession": 80, "responsibility": 20},
        }
        self.tougen_buildings = []   # 已建成的桃源建筑 id
        self.research_done = []      # 已完成的忍术研究 id
        self.runtime_flags = {}      # 不写入存档的单次剧情临时状态
        # 恋爱线:心动值 (疾风传开启;定情后 flags["lover"] 记录恋人)
        self.romance = {"sakura": 0, "hinata": 0, "tsunade": 0, "konan": 0, "rin": 0}
        self.flags = {
            "intro_done": False,
            "team7_assigned": False,
            "talked_sasuke": False,
            "talked_sakura": False,
            "bell_test_completed": False,
            "tougen_unlocked": False,
            "kushina_contacted": False,
            "cat_found": False,
            "rasengan_learned": False,
            "chapter1_end": False,
            # ── 波之国篇 ──
            "wave_done": False,
            "haku_bond": 0,
            "haku_alive": False,
            "zabuza_alive": False,
            # ── 琳剧情线 ──
            "rin_photo_seen": False,
            "rin_light_found": False,
            "rin_contacted": False,
            "rin_kakashi_hint": False,
            # ── 中忍考试篇 ──
            "chunin_done": False,
            "warned_hokage": False,
            "curse_avoided": False,
            "oro_marked_naruto": False,
            "gaara_bond": 0,
            "jiraiya_trust": 0,
            "neji_freed": False,
            # ── 木叶崩溃篇 ──
            "crush_done": False,
            "hiruzen_saved": False,
            "gaara_redeemed": False,
            # ── 寻找纲手篇 ──
            "tsunade_done": False,
            "tsunade_returned": False,
            "tsunade_bond": 0,
            "itachi_knows": False,
            "sasuke_hospitalized": False,
            "rasengan_official": False,
            "tsunade_tougen_invited": False,
            # ── 佐助离村篇 ──
            "sasuke_arc_done": False,
            "sasuke_ending": 0,       # 1原剧情离村 2约定离村 3留村监护 4改命同盟
            "spar_done": False,
            "main_complete": False,
            # ── 杂项 ──
            "kyubi_calm_done": False,
            "herb_quest_active": False,
            "sakura_hospital_c3": False,
            "sakura_hospital_c5": False,
            "sasuke_talk_c3": False,
            "sasuke_talk_c4": False,
            "sasuke_talk_c5": False,
            # ── 疾风传·三年后 ──
            "shippuden_started": False,     # 完成三年修行,进入疾风传
            # 风影夺还篇
            "kazekage_done": False,
            "gaara_saved": False,           # 我爱罗未死于拔尾兽
            "chiyo_alive": False,           # 千代婆婆存活(改命)
            "sakura_contracted": False,     # 第四契约:小樱
            # 晓之阴影篇
            "akatsuki_done": False,
            "asuma_saved": False,           # 阿斯玛存活(改命)
            "hinata_contracted": False,     # 第六契约:雏田
            "shizune_contracted": False,
            "sage_training_done": False,    # 妙木山仙术修行
            "jiraiya_saved": False,         # 自来也存活(改命核心)
            "pain_intel": 0,                # 佩恩情报层级 0-3
            # 佩恩袭村篇
            "pain_done": False,
            "village_evacuated": False,     # 提前疏散
            "hinata_guarded": False,        # 雏田未重伤
            "nagato_redeemed": False,       # 长门转意
            "konan_contracted": False,
            # 忍界大战篇
            "war_done": False,
            "summit_done": False,           # 五影会谈
            "mei_contracted": False,
            "kurama_friend": False,         # 与九喇嘛和解
            "obito_redeemed": False,        # 带土被琳唤回
            "infinite_tsukuyomi_stopped": False,
            "true_end": False,              # 九命同归·大团圆
            # ── 恋爱线 (疾风传开启) ──
            "rom_sakura_1": False, "rom_sakura_2": False,
            "rom_hinata_1": False, "rom_hinata_2": False,
            "rom_tsunade_1": False, "rom_tsunade_2": False,
            "rom_konan_1": False, "rom_konan_2": False,
            "rom_rin_1": False, "rom_rin_2": False,
            "lover": "",                    # 定情对象 id ("" = 未定情)
        }

    # ── 属性与成长 ──────────────────────────────

    def exp_to_next(self):
        return self.player["level"] * 100

    def gain_exp(self, amount):
        """获得经验，返回升级次数。"""
        from systems import ui
        p = self.player
        p["exp"] += amount
        ui.slow_print(f"※ 获得经验 {amount} 点。")
        ups = 0
        while p["exp"] >= self.exp_to_next():
            p["exp"] -= self.exp_to_next()
            p["level"] += 1
            ups += 1
            p["max_hp"] += 15
            p["max_chakra"] += 12
            p["attack"] += 3
            p["defense"] += 2
            p["speed"] += 2
            p["spirit"] += 2
            p["hp"] = p["max_hp"]
            p["chakra"] = p["max_chakra"]
            ui.slow_print(f"★ 等级提升！鸣人达到 Lv.{p['level']}，全属性成长，状态全恢复！")
        return ups

    def gain_fate(self, amount, reason=""):
        from systems import ui
        self.fate_points += amount
        tail = f"({reason})" if reason else ""
        ui.slow_print(f"◆ 命运点 +{amount} {tail} [当前: {self.fate_points}]")

    def spend_fate(self, amount, reason=""):
        """消耗命运点，不足返回 False。"""
        from systems import ui
        if self.fate_points < amount:
            return False
        self.fate_points -= amount
        tail = f"({reason})" if reason else ""
        ui.slow_print(f"◇ 命运点 -{amount} {tail} [剩余: {self.fate_points}]")
        return True

    def add_backlash(self, amount, reason=""):
        from systems import ui
        self.backlash = max(0, min(6, self.backlash + amount))
        tail = f"({reason})" if reason else ""
        sign = "+" if amount >= 0 else ""
        ui.slow_print(f"▼ 命运反噬 {sign}{amount} {tail} [当前等级: {self.backlash}]")

    def add_suspicion(self, amount):
        from systems import ui
        self.kakashi_suspicion = max(0, self.kakashi_suspicion + amount)
        sign = "+" if amount >= 0 else ""
        ui.slow_print(f"▲ 卡卡西怀疑值 {sign}{amount} [当前: {self.kakashi_suspicion}]")

    def add_trust(self, amount):
        from systems import ui
        self.team7_trust += amount
        ui.slow_print(f"♥ 第七班信任度 +{amount} [当前: {self.team7_trust}]")

    def add_village_trust(self, amount):
        from systems import ui
        self.village_trust = max(0, self.village_trust + amount)
        sign = "+" if amount >= 0 else ""
        ui.slow_print(f"♣ 木叶信任 {sign}{amount} [当前: {self.village_trust}]")

    def add_flux(self, amount):
        from systems import ui
        self.kyubi_flux = max(0, self.kyubi_flux + amount)
        sign = "+" if amount >= 0 else ""
        ui.slow_print(f"☄ 九尾波动 {sign}{amount} [当前: {self.kyubi_flux}]")

    def add_rel(self, who, key, amount):
        """调整关系数值并打印，如 add_rel('sasuke', 'revenge', -5)。"""
        from systems import ui
        rel = self.relations[who]
        rel[key] = max(0, min(100, rel[key] + amount))
        name = f"{CHAR_NAMES.get(who, who)}·{REL_NAMES[who][key]}"
        sign = "+" if amount >= 0 else ""
        ui.slow_print(f"♦ {name} {sign}{amount} [当前: {rel[key]}]")

    def add_romance(self, who, amount):
        """恋爱心动值。"""
        from systems import ui
        names = {"sakura": "小樱", "hinata": "雏田", "tsunade": "纲手",
                 "konan": "小南", "rin": "琳"}
        self.romance[who] = max(0, min(100, self.romance.get(who, 0) + amount))
        sign = "+" if amount >= 0 else ""
        ui.slow_print(f"❀ {names.get(who, who)}·心动 {sign}{amount} [当前: {self.romance[who]}]")

    def add_item(self, name, count=1, cap=9):
        from systems import ui
        cur = self.inventory.get(name, 0)
        got = max(0, min(cap, cur + count) - cur)
        if got > 0:
            self.inventory[name] = cur + got
            ui.slow_print(f"※ 获得【{name}】×{got}。")
        return got

    def gain_ryo(self, amount, reason=""):
        from systems import ui
        amount = max(0, int(amount))
        self.ryo += amount
        tail = f"（{reason}）" if reason else ""
        ui.slow_print(f"※ 获得 {amount} 两{tail} [当前: {self.ryo} 两]")
        return amount

    def spend_ryo(self, amount, reason=""):
        from systems import ui
        amount = max(0, int(amount))
        if self.ryo < amount:
            return False
        self.ryo -= amount
        tail = f"（{reason}）" if reason else ""
        ui.slow_print(f"※ 支付 {amount} 两{tail} [剩余: {self.ryo} 两]")
        return True

    def daily_uses(self, key):
        """返回某项活动在当前游戏日已经获得收益的次数。"""
        record = self.daily_activity.get(key, {})
        if not isinstance(record, dict) or record.get("day") != self.world_day:
            return 0
        return max(0, int(record.get("count", 0)))

    def consume_daily_use(self, key, limit=1):
        """占用一次当日收益额度；额度耗尽时返回 False。"""
        used = self.daily_uses(key)
        if used >= max(0, int(limit)):
            return False
        self.daily_activity[key] = {"day": self.world_day, "count": used + 1}
        return True

    def has_building(self, bid):
        return bid in self.tougen_buildings

    def has_research(self, rid):
        return rid in self.research_done

    def learn_skill(self, skill_id):
        if skill_id not in self.player["skills"]:
            self.player["skills"].append(skill_id)
            if len(self.equipped_skills) < 6:
                self.equipped_skills.append(skill_id)

    # ── 序列化 ──────────────────────────────

    def to_dict(self):
        return {
            "player": self.player,
            "contracts": self.contracts,
            "quests": self.quests,
            "location": self.location,
            "fate_points": self.fate_points,
            "backlash": self.backlash,
            "exposure": self.exposure,
            "kakashi_suspicion": self.kakashi_suspicion,
            "team7_trust": self.team7_trust,
            "village_trust": self.village_trust,
            "belonging": self.belonging,
            "kyubi_flux": self.kyubi_flux,
            "inventory": self.inventory,
            "ryo": self.ryo,
            "chapter": self.chapter,
            "world_day": self.world_day,
            "time_index": self.time_index,
            "actions_taken": self.actions_taken,
            "daily_activity": self.daily_activity,
            "tougen_training_sessions": self.tougen_training_sessions,
            "equipped_skills": self.equipped_skills,
            "skill_upgrades": self.skill_upgrades,
            "owned_equipment": self.owned_equipment,
            "equipped_gear": self.equipped_gear,
            "equipment_quality": self.equipment_quality,
            "equipment_enhancements": self.equipment_enhancements,
            "equipment_affixes": self.equipment_affixes,
            "wanted_records": self.wanted_records,
            "new_game_plus": self.new_game_plus,
            "challenge_modifiers": self.challenge_modifiers,
            "selected_party": self.selected_party,
            "teammate_progress": self.teammate_progress,
            "combo_mastery": self.combo_mastery,
            "faction_reputation": self.faction_reputation,
            "dynamic_quests": self.dynamic_quests,
            "dynamic_quest_serial": self.dynamic_quest_serial,
            "last_dynamic_refresh_day": self.last_dynamic_refresh_day,
            "faction_story": self.faction_story,
            "faction_rank_rewards": self.faction_rank_rewards,
            "random_event_history": self.random_event_history,
            "random_event_last_seen": self.random_event_last_seen,
            "world_event_chains": self.world_event_chains,
            "contract_trials": self.contract_trials,
            "discovered_characters": self.discovered_characters,
            "discovered_enemies": self.discovered_enemies,
            "discovered_skills": self.discovered_skills,
            "achievements": self.achievements,
            "endings_seen": self.endings_seen,
            "relations": self.relations,
            "tougen_buildings": self.tougen_buildings,
            "research_done": self.research_done,
            "romance": self.romance,
            "flags": self.flags,
        }

    def from_dict(self, data):
        if not isinstance(data, dict):
            raise TypeError("存档必须是 JSON 对象")

        # 始终以当前版本默认数据为基础，只合并存档中已知字段。
        saved_player = data.get("player", {})
        if not isinstance(saved_player, dict):
            raise TypeError("玩家数据格式错误")
        self.player.update(saved_player)
        for cid, saved_contract in data.get("contracts", {}).items():
            if cid in self.contracts and isinstance(saved_contract, dict):
                self.contracts[cid].update(saved_contract)
        for qid, saved_quest in data.get("quests", {}).items():
            if qid in self.quests and isinstance(saved_quest, dict):
                self.quests[qid].update(saved_quest)

        self.location = data.get("location", self.location)
        if self.location not in self.maps:
            self.location = "naruto_home"
        self.fate_points = data.get("fate_points", self.fate_points)
        self.backlash = data.get("backlash", self.backlash)
        self.exposure = data.get("exposure", self.exposure)
        self.kakashi_suspicion = data.get("kakashi_suspicion", self.kakashi_suspicion)
        self.team7_trust = data.get("team7_trust", self.team7_trust)
        self.village_trust = data.get("village_trust", 0)
        self.belonging = data.get("belonging", self.belonging)
        self.kyubi_flux = data.get("kyubi_flux", 0)
        saved_inventory = data.get("inventory", {})
        if isinstance(saved_inventory, dict):
            self.inventory.update(saved_inventory)
        self.ryo = max(0, int(data.get("ryo", self.ryo)))
        self.chapter = data.get("chapter", self.chapter)
        self.world_day = max(1, int(data.get("world_day", self.world_day)))
        self.time_index = int(data.get("time_index", self.time_index)) % 4
        self.actions_taken = max(0, int(data.get("actions_taken", self.actions_taken)))
        saved_daily = data.get("daily_activity", {})
        if isinstance(saved_daily, dict):
            self.daily_activity = {
                str(key): {
                    "day": max(1, int(value.get("day", self.world_day))),
                    "count": max(0, int(value.get("count", 0))),
                }
                for key, value in saved_daily.items()
                if isinstance(value, dict)
            }
        self.tougen_training_sessions = max(0, int(data.get("tougen_training_sessions", 0)))
        saved_equipped = data.get("equipped_skills")
        if saved_equipped is None:
            self.equipped_skills = list(self.player.get("skills", []))[:6]
        else:
            self.equipped_skills = list(saved_equipped)
        saved_upgrades = data.get("skill_upgrades", {})
        if isinstance(saved_upgrades, dict):
            self.skill_upgrades = dict(saved_upgrades)
        self.owned_equipment = list(data.get("owned_equipment", self.owned_equipment))
        saved_gear = data.get("equipped_gear", {})
        if isinstance(saved_gear, dict):
            self.equipped_gear.update(saved_gear)
        saved_quality = data.get("equipment_quality", {})
        if isinstance(saved_quality, dict):
            self.equipment_quality.update(saved_quality)
        saved_enhancements = data.get("equipment_enhancements", {})
        if isinstance(saved_enhancements, dict):
            self.equipment_enhancements = dict(saved_enhancements)
        saved_affixes = data.get("equipment_affixes", {})
        if isinstance(saved_affixes, dict):
            self.equipment_affixes = dict(saved_affixes)
        saved_wanted = data.get("wanted_records", {})
        if isinstance(saved_wanted, dict):
            self.wanted_records = {key: max(0, int(value)) for key, value in saved_wanted.items()}
        self.new_game_plus = max(0, int(data.get("new_game_plus", self.new_game_plus)))
        self.challenge_modifiers = list(dict.fromkeys(data.get("challenge_modifiers", [])))
        self.selected_party = list(data.get("selected_party", self.selected_party))
        saved_teammates = data.get("teammate_progress", {})
        if isinstance(saved_teammates, dict):
            self.teammate_progress = copy.deepcopy(saved_teammates)
        saved_mastery = data.get("combo_mastery", {})
        if isinstance(saved_mastery, dict):
            self.combo_mastery = copy.deepcopy(saved_mastery)
        saved_reputation = data.get("faction_reputation", {})
        if isinstance(saved_reputation, dict):
            for faction_id in self.faction_reputation:
                self.faction_reputation[faction_id] = max(
                    0, int(saved_reputation.get(faction_id, self.faction_reputation[faction_id]))
                )
        saved_dynamic = data.get("dynamic_quests", {})
        if isinstance(saved_dynamic, dict):
            self.dynamic_quests = copy.deepcopy(saved_dynamic)
        self.dynamic_quest_serial = max(0, int(data.get("dynamic_quest_serial", 0)))
        self.last_dynamic_refresh_day = max(0, int(data.get("last_dynamic_refresh_day", 0)))
        saved_faction_story = data.get("faction_story", {})
        if isinstance(saved_faction_story, dict):
            self.faction_story = copy.deepcopy(saved_faction_story)
        self.faction_rank_rewards = list(dict.fromkeys(data.get("faction_rank_rewards", [])))
        saved_history = data.get("random_event_history", {})
        if isinstance(saved_history, dict):
            self.random_event_history = saved_history
        saved_last_seen = data.get("random_event_last_seen", {})
        if isinstance(saved_last_seen, dict):
            self.random_event_last_seen = saved_last_seen
        saved_chains = data.get("world_event_chains", {})
        if isinstance(saved_chains, dict):
            self.world_event_chains = {
                key: max(0, int(value)) for key, value in saved_chains.items()
            }
        self.contract_trials = list(dict.fromkeys(data.get("contract_trials", [])))
        self.discovered_characters = list(dict.fromkeys(data.get("discovered_characters", [])))
        self.discovered_enemies = list(dict.fromkeys(data.get("discovered_enemies", [])))
        self.discovered_skills = list(dict.fromkeys(data.get("discovered_skills", [])))
        self.achievements = list(dict.fromkeys(data.get("achievements", [])))
        self.endings_seen = list(dict.fromkeys(data.get("endings_seen", [])))
        for who, rel in data.get("relations", {}).items():
            if who in self.relations and isinstance(rel, dict):
                self.relations[who].update({key: value for key, value in rel.items()
                                            if key in self.relations[who]})
        self.tougen_buildings = list(data.get("tougen_buildings", []))
        self.research_done = list(data.get("research_done", []))
        saved_romance = data.get("romance", {})
        if isinstance(saved_romance, dict):
            self.romance.update({key: value for key, value in saved_romance.items()
                                 if key in self.romance})
        # 「螺旋丸·性质变化」研究修改的是技能库数值,读档时重放
        if "rasengan_perfect" in self.research_done:
            self.skills_db["rasengan"]["power"] = 120
        saved_flags = data.get("flags", {})
        if isinstance(saved_flags, dict):
            self.flags.update({key: value for key, value in saved_flags.items()
                               if key in self.flags})
        from systems import equipment, factions, loadout, party, skill_mastery

        equipment.normalize_equipment(self)
        loadout.normalize_loadout(self)
        skill_mastery.normalize_upgrades(self)
        party.normalize_party(self)
        party.normalize_progress(self)
        factions.normalize_state(self)
