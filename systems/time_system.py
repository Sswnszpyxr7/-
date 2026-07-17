# -*- coding: utf-8 -*-
"""世界时间与行动推进。"""

PERIODS = ("清晨", "白昼", "黄昏", "夜晚")


def period_name(state):
    return PERIODS[state.time_index % len(PERIODS)]


def time_label(state):
    return f"第 {state.world_day} 日·{period_name(state)}"


def advance_time(state, steps=1, announce=True):
    """推进时间，并触发收藏/成就评估。"""
    if steps <= 0:
        return
    previous_day = state.world_day
    previous_period = period_name(state)
    total = state.time_index + steps
    state.world_day += total // len(PERIODS)
    state.time_index = total % len(PERIODS)
    state.actions_taken += steps
    if announce:
        from systems import ui

        if state.world_day != previous_day:
            ui.slow_print(f"☼ 新的一天开始了——{time_label(state)}。")
        elif period_name(state) != previous_period:
            ui.slow_print(f"☼ 时间来到了【{period_name(state)}】。")
    from systems import collection

    collection.evaluate_achievements(state, announce=announce)
