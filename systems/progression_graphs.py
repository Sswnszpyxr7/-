# -*- coding: utf-8 -*-
"""剧情分支图与恋爱阶段图使用的存档状态模型。"""


STORY_NODE_WIDTH = 205
STORY_NODE_HEIGHT = 62


def _node(node_id, title, detail, x, y, status, width=STORY_NODE_WIDTH, height=STORY_NODE_HEIGHT):
    return {
        "id": node_id,
        "title": title,
        "detail": detail,
        "x": x,
        "y": y,
        "width": width,
        "height": height,
        "status": status,
    }


def _stage_status(done, unlocked):
    if done:
        return "complete"
    return "current" if unlocked else "locked"


def _choice_status(stage_done, selected, collected=False, favorable=True):
    if selected:
        return "route_good" if favorable else "route_bad"
    if collected:
        return "collected"
    return "alternate" if stage_done else "locked"


def _result_status(stage_done, succeeded):
    if not stage_done:
        return "locked"
    return "route_good" if succeeded else "route_bad"


def story_graph(state):
    """返回带固定布局坐标的剧情节点和连线。"""
    flags = state.flags
    endings = set(state.endings_seen)
    main_specs = [
        ("team7", "重生·分班日", "第七班重新集结", flags["team7_assigned"], True),
        ("bell", "铃铛测试", "团队合作的起点", flags["bell_test_completed"], flags["team7_assigned"]),
        ("tougen", "桃源觉醒", "玖辛奈与第一契约", flags["chapter1_end"], flags["bell_test_completed"]),
        ("wave", "波之国", "白与再不斩的命运", flags["wave_done"], flags["chapter1_end"]),
        ("chunin", "中忍考试", "咒印、宁次与我爱罗", flags["chunin_done"], flags["wave_done"]),
        ("crush", "木叶崩溃", "三代火影生死节点", flags["crush_done"], flags["chunin_done"]),
        ("tsunade", "寻找纲手", "鼬的情报与三忍抉择", flags["tsunade_done"], flags["crush_done"]),
        ("sasuke", "终结谷", "佐助离村篇四路线", flags["sasuke_arc_done"], flags["tsunade_done"]),
        ("training", "三年修行", "进入疾风传", flags["shippuden_started"], flags["main_complete"]),
        ("kazekage", "风影夺还", "我爱罗与千代", flags["kazekage_done"], flags["shippuden_started"]),
        ("akatsuki", "晓之阴影", "阿斯玛与自来也", flags["akatsuki_done"], flags["kazekage_done"]),
        ("sage", "妙木山修行", "仙人模式与静音契约", flags["sage_training_done"], flags["akatsuki_done"]),
        ("pain", "佩恩袭村", "村庄、雏田与长门", flags["pain_done"], flags["sage_training_done"]),
        ("war", "忍界大战", "带土、斑与九命同归", flags["war_done"], flags["pain_done"]),
    ]
    nodes = []
    edges = []
    y_by_id = {}
    for index, (node_id, title, detail, done, unlocked) in enumerate(main_specs):
        y = 45 + index * 124
        y_by_id[node_id] = y
        nodes.append(_node(node_id, title, detail, 40, y, _stage_status(done, unlocked)))
        if index:
            edges.append((main_specs[index - 1][0], node_id))

    def add_choices(source, choices, y_offset=0):
        y = y_by_id[source] + y_offset
        for index, choice in enumerate(choices):
            node_id, title, detail, status = choice
            nodes.append(_node(node_id, title, detail, 305 + index * 220, y, status, width=200))
            edges.append((source, node_id))

    wave_route = None
    if flags["wave_done"]:
        if flags["haku_alive"] and flags["zabuza_alive"]:
            wave_route = "wave_perfect"
        elif flags["haku_alive"]:
            wave_route = "wave_haku"
        else:
            wave_route = "wave_canon"
    add_choices(
        "wave",
        [
            (
                "wave_canon",
                "原定命运",
                "白与再不斩牺牲",
                _choice_status(flags["wave_done"], wave_route == "wave_canon", "wave_canon" in endings, False),
            ),
            (
                "wave_haku",
                "白的新生",
                "白存活，再不斩牺牲",
                _choice_status(flags["wave_done"], wave_route == "wave_haku", "wave_haku" in endings),
            ),
            (
                "wave_perfect",
                "双生归途",
                "白与再不斩共同存活",
                _choice_status(flags["wave_done"], wave_route == "wave_perfect", "wave_perfect" in endings),
            ),
            (
                "rin_line",
                "琳命线·支线",
                "照片 → 海雾残光 → 契约",
                _stage_status(flags["rin_contacted"], flags["wave_done"]),
            ),
        ],
    )

    add_choices(
        "chunin",
        [
            (
                "curse_avoided",
                "咒印彻底格挡",
                "封印术改变佐助命运",
                _choice_status(flags["chunin_done"], flags["curse_avoided"], favorable=True),
            ),
            (
                "curse_remains",
                "咒印侵蚀保留",
                "终结谷难度与结局受影响",
                _choice_status(flags["chunin_done"], flags["chunin_done"] and not flags["curse_avoided"], favorable=False),
            ),
            (
                "neji_freed",
                "宁次挣脱宿命",
                "决赛中的命运论战",
                _result_status(flags["chunin_done"], flags["neji_freed"]),
            ),
        ],
    )

    add_choices(
        "crush",
        [
            (
                "hiruzen_saved",
                "三代生还",
                "提前预警与命运改写",
                _result_status(flags["crush_done"], flags["hiruzen_saved"]),
            ),
            (
                "gaara_redeemed",
                "我爱罗转意",
                "言语共鸣战成功",
                _result_status(flags["crush_done"], flags["gaara_redeemed"]),
            ),
        ],
    )

    add_choices(
        "tsunade",
        [
            (
                "itachi_knows",
                "鼬收到真相",
                "旅馆相遇时传递情报",
                _result_status(flags["tsunade_done"], flags["itachi_knows"]),
            ),
            (
                "tsunade_contract",
                "纲手契约",
                "羁绊达到要求后邀请桃源",
                _stage_status(state.contracts["tsunade"]["unlocked"], flags["tsunade_done"]),
            ),
        ],
    )

    sasuke_ending = flags["sasuke_ending"]
    sasuke_choices = [
        (1, "sasuke_canon", "离村", "原剧情路线", False),
        (2, "sasuke_promise", "约定", "带着约定离村", True),
        (3, "sasuke_guarded", "留村监护", "在木叶接受监护", True),
        (4, "sasuke_alliance", "改命同盟", "与鸣人共同改变未来", True),
    ]
    add_choices(
        "sasuke",
        [
            (
                ending_id,
                title,
                detail,
                _choice_status(
                    flags["sasuke_arc_done"],
                    sasuke_ending == value,
                    ending_id in endings,
                    favorable,
                ),
            )
            for value, ending_id, title, detail, favorable in sasuke_choices
        ],
    )

    add_choices(
        "kazekage",
        [
            (
                "gaara_saved",
                "我爱罗获救",
                "风影成功复苏",
                _result_status(flags["kazekage_done"], flags["gaara_saved"]),
            ),
            (
                "chiyo_alive",
                "千代婆婆生还",
                "沙海天平命运节点",
                _result_status(flags["kazekage_done"], flags["chiyo_alive"]),
            ),
            (
                "sakura_contract",
                "小樱契约",
                "第四条命线",
                _stage_status(flags["sakura_contracted"], flags["kazekage_done"]),
            ),
        ],
    )

    add_choices(
        "akatsuki",
        [
            (
                "asuma_saved",
                "阿斯玛生还",
                "十班驰援成功",
                _result_status(flags["akatsuki_done"], flags["asuma_saved"]),
            ),
            (
                "jiraiya_saved",
                "自来也生还",
                "佩恩情报达到三级",
                _result_status(flags["akatsuki_done"], flags["jiraiya_saved"]),
            ),
            (
                "hinata_contract",
                "雏田契约",
                "月下之誓",
                _stage_status(flags["hinata_contracted"], flags["akatsuki_done"]),
            ),
        ],
    )

    add_choices(
        "pain",
        [
            (
                "village_evacuated",
                "村庄提前疏散",
                "降低佩恩袭村伤亡",
                _result_status(flags["pain_done"], flags["village_evacuated"]),
            ),
            (
                "hinata_guarded",
                "雏田未受重伤",
                "守护节点改写",
                _result_status(flags["pain_done"], flags["hinata_guarded"]),
            ),
            (
                "nagato_redeemed",
                "长门转意",
                "塔中问答成功",
                _result_status(flags["pain_done"], flags["nagato_redeemed"]),
            ),
        ],
    )

    add_choices(
        "war",
        [
            (
                "kurama_friend",
                "九喇嘛和解",
                "心之瀑布",
                _result_status(flags["war_done"], flags["kurama_friend"]),
            ),
            (
                "obito_redeemed",
                "带土回归",
                "琳唤回迷途之人",
                _result_status(flags["war_done"], flags["obito_redeemed"]),
            ),
            (
                "moon_stopped",
                "无限月读被阻止",
                "终局命运节点",
                _result_status(flags["war_done"], flags["infinite_tsukuyomi_stopped"]),
            ),
        ],
    )
    add_choices(
        "war",
        [
            (
                "war_standard",
                "普通结局",
                "未尽的遗憾",
                _choice_status(
                    flags["war_done"],
                    flags["war_done"] and not flags["true_end"],
                    "war_standard" in endings,
                    False,
                ),
            ),
            (
                "war_true",
                "九命同归·真结局",
                "六大改命与契约条件达成",
                _choice_status(flags["war_done"], flags["true_end"], "war_true" in endings),
            ),
        ],
        y_offset=72,
    )

    complete_main = sum(1 for _, _, _, done, _ in main_specs if done)
    return {
        "nodes": nodes,
        "edges": edges,
        "width": 1210,
        "height": y_by_id["war"] + 190,
        "summary": f"主线 {complete_main}/{len(main_specs)} · 已收集结局 {len(endings)}/9",
    }


ROMANCE_LINES = {
    "sakura": {
        "name": "小樱",
        "events": (("加班的医疗班", "木叶医院"), ("两碗拉面", "一乐拉面")),
        "confess": ("医院天台的晚霞", "木叶医院"),
    },
    "hinata": {
        "name": "雏田",
        "events": (("月下的组手", "第七训练场"), ("火影岩上的两个人", "火影岩")),
        "confess": ("三根木桩的约定", "第七训练场"),
    },
    "tsunade": {
        "name": "纲手",
        "events": (("深夜的办公室", "火影办公室"), ("不赌牌的夜晚", "一乐拉面")),
        "confess": ("火影帽下的答案", "火影办公室"),
    },
    "konan": {
        "name": "小南",
        "events": (("雨之国的来客", "木叶大门"), ("纸伞下", "木叶大门")),
        "confess": ("第一万零一朵纸花", "木叶大门"),
    },
    "rin": {
        "name": "琳",
        "events": (("星空湖的夜钓", "桃源"), ("一起做药丸", "桃源")),
        "confess": ("药草田的花开了", "桃源"),
    },
}


def _romance_stage_status(done, available, lover, who):
    if done:
        return "love" if lover == who else "complete"
    if lover and lover != who:
        return "family"
    return "current" if available else "locked"


def romance_graph(state):
    """返回五条恋爱线的阶段状态。"""
    flags = state.flags
    lover = flags.get("lover", "")
    rows = []
    for who, spec in ROMANCE_LINES.items():
        contracted = bool(state.contracts[who]["unlocked"])
        ready = flags["shippuden_started"] and contracted
        first_done = flags[f"rom_{who}_1"]
        second_done = flags[f"rom_{who}_2"]
        special_ready = ready
        if who == "hinata":
            special_ready = ready and flags["hinata_contracted"]
        elif who == "konan":
            special_ready = ready and flags["pain_done"]
        heart = state.romance.get(who, 0)
        confess_ready = second_done and flags["war_done"] and heart >= 50 and not lover
        stages = [
            {
                "title": "恋爱线解锁",
                "detail": f"契约 {'已缔结' if contracted else '未缔结'} · "
                f"疾风传 {'已开启' if flags['shippuden_started'] else '未开启'}",
                "status": _romance_stage_status(ready, contracted or flags["shippuden_started"], lover, who),
            },
            {
                "title": spec["events"][0][0],
                "detail": f"地点：{spec['events'][0][1]} · 心动 +25",
                "status": _romance_stage_status(first_done, special_ready, lover, who),
            },
            {
                "title": spec["events"][1][0],
                "detail": f"地点：{spec['events'][1][1]} · 心动 +30",
                "status": _romance_stage_status(second_done, first_done, lover, who),
            },
            {
                "title": spec["confess"][0],
                "detail": f"地点：{spec['confess'][1]} · 大战结束 · 心动 ≥50",
                "status": _romance_stage_status(lover == who, confess_ready, lover, who),
            },
        ]
        if second_done and not flags["war_done"] and not lover:
            stages[-1]["status"] = "waiting"
            stages[-1]["detail"] += "（等待大战结束）"
        elif second_done and heart < 50 and not lover:
            stages[-1]["status"] = "waiting"
            stages[-1]["detail"] += f"（当前 {heart}）"
        rows.append(
            {
                "id": who,
                "name": spec["name"],
                "heart": heart,
                "is_lover": lover == who,
                "stages": stages,
            }
        )
    lover_name = ROMANCE_LINES.get(lover, {}).get("name", "尚未定情")
    return {
        "rows": rows,
        "width": 1120,
        "height": 775,
        "summary": f"当前恋人：{lover_name} · 定情为单恋人制",
    }
