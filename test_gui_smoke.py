# -*- coding: utf-8 -*-
"""GUI 冒烟测试:不弹人工交互,自动点按钮走完 开场→探索菜单→系统菜单→退出。

存档目录被重定向到临时目录,不会碰真实存档。
运行: python test_gui_smoke.py
"""
import os
import shutil
import sys
import tempfile
import time

os.environ["NL_FAST"] = "1"  # 关闭逐字打印,加速测试
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import gui as gui_mod          # noqa: E402
from systems import save as save_mod  # noqa: E402
from systems import ui as ui_mod  # noqa: E402

REAL_STDOUT = sys.stdout


def pick(labels, key):
    for i, label in enumerate(labels):
        if key in ui_mod.choice_label(label):
            return i
    return None


def main():
    tmp = tempfile.mkdtemp(prefix="nl_saves_")
    save_mod.set_save_dir(tmp)  # 隔离存档

    app = gui_mod.NineLivesGUI()
    deadline = time.time() + 90
    interactions = 0
    ok = False

    try:
        while time.time() < deadline:
            app.root.update()
            time.sleep(0.004)
            if app.ended:
                ok = True
                break
            if app.waiting == "pause":
                interactions += 1
                app._continue()
            elif app.waiting == "choose":
                interactions += 1
                labels = app._options
                prompt = app._prompt or ""
                if "要做什么" in prompt:
                    idx = pick(labels, "道具/菜单")
                elif pick(labels, "退出游戏") is not None:
                    idx = pick(labels, "退出游戏")
                elif "确定退出" in prompt:
                    idx = pick(labels, "退出")
                else:
                    idx = 0
                app._answer(idx if idx is not None else 0)

        text = app.text.get("1.0", "end")
        assert ok, f"超时:游戏未在 90 秒内结束 (交互 {interactions} 次)"
        assert "分班的日子" in text, "开场剧情未出现在剧情窗中"
        assert "当前位置" in text, "地点描述未出现在剧情窗中"
        assert "▸" in text, "选项回显未出现在剧情窗中"
        autosave = os.path.join(tmp, "save_03.json")
        assert os.path.exists(autosave), "退出时未写入自动存档"
        # 边栏在最后刷新过,不抛异常即视为渲染正常
        app._refresh_status()
        assert app.visual_canvas.winfo_exists(), "场景横幅画布未创建"
        assert app.sidebar_canvas.winfo_exists(), "可滚动状态栏未创建"
        assert app.collection_button.winfo_viewable(), "收藏馆按钮在默认窗口尺寸下不可见"
        assert app._portrait_photo is not None, "角色头像未成功加载"
        assert app._banner_photo is not None, "地点插图未成功加载"
        app._options = [
            ui_mod.Choice(
                f"滚动选项 {index + 1}",
                ("actions", "quests"),
                "用于验证大量结构化选项不会挤出剧情区域",
            )
            for index in range(18)
        ]
        app._allow_cancel = False
        story_height_before_choices = app.text.winfo_height()
        app._show_choices()
        app.root.update_idletasks()
        app._resize_choice_area()
        assert app.choice_scroll.winfo_manager(), "大量行动选项未启用内部滚动条"
        assert app.choice_canvas.winfo_height() <= 230, "行动区高度超过设计上限"
        first_button = app.btn_frame.winfo_children()[0]
        assert first_button.cget("image"), "结构化行动图标未显示"
        assert abs(app.text.winfo_height() - story_height_before_choices) <= 2, \
            "选项出现导致剧情视口高度突变"
        app._clear_buttons()
        app.root.update_idletasks()
        assert abs(app.text.winfo_height() - story_height_before_choices) <= 2, \
            "选项消失导致剧情视口高度突变"
        app._flush_text(["\n卡卡西：现在测试头像切换。\n"])
        assert app._current_portrait == "kakashi", "剧情文本未触发角色头像切换"
        app._flush_text(["\n波之国·大桥决战。\n"])
        assert app._current_illustration == "wave_bridge", "关键剧情未触发横幅切换"
        app._handle_visual_event(
            "battle_start",
            {
                "enemy_id": "pain_deva",
                "enemy_name": "佩恩·天道",
                "boss": True,
                "enemy_hp": 800,
                "enemy_max_hp": 1000,
                "elements": ["yin"],
                "affixes": [],
            },
        )
        app._handle_visual_event(
            "battle_update",
            {
                "intent": "fatal",
                "intent_name": "地爆天星",
                "enemy_hp": 640,
                "enemy_max_hp": 1000,
                "enemy_status": ["sealed"],
                "player_status": ["wet"],
                "break_value": 30,
                "break_max": 100,
            },
        )
        app.root.update()
        assert app._current_illustration == "boss:pain_deva", "Boss 战未切换战斗切入图"
        assert app._banner_photo is not None, "Boss 战斗切入图未成功加载"
        assert app._battle_visual["intent"] == "fatal", "战斗意图视觉事件未进入 GUI"
        assert app._battle_visual["enemy_hp"] == 640, "Boss 生命值未进入固定 HUD"
        app._options = ["开始战斗", ui_mod.Choice("查看任务", ("actions", "quests"))]
        app._allow_cancel = False
        app._show_choices()
        app.root.update_idletasks()
        option_buttons = app.btn_frame.winfo_children()
        assert all(button.cget("image") for button in option_buttons), "无资源选项未保留统一图标槽"
        app._handle_visual_event("battle_end", {"result": "win"})
        assert app._battle_visual is None, "战斗结束后 HUD 未清理"

        # P0-1: 游戏内模态浮层替代系统 messagebox
        app.root.after(30, lambda: app._close_game_modal("ok"))
        app._modal_info("行动详情", "这是一条用于验证浮层的说明文字。", badge="详情")
        app.root.update()
        assert not app._modal_active, "信息浮层关闭后仍处于激活状态"
        assert app._modal_backdrop is None, "信息浮层遮罩未销毁"

        app.root.after(30, lambda: app._close_game_modal("yes"))
        confirmed = app._modal_confirm(
            "退出游戏",
            "确定要离开忍界旅程吗？\n当前进度将自动保存。",
            badge="退出",
            yes_label="退出并保存",
            no_label="继续游戏",
            danger=True,
        )
        app.root.update()
        assert confirmed is True, "确认浮层未正确返回 yes"
        assert not app._modal_active, "确认浮层关闭后仍处于激活状态"

        app.root.after(30, lambda: app._close_game_modal("no"))
        cancelled = app._modal_confirm("测试取消", "点取消应返回 False")
        app.root.update()
        assert cancelled is False, "确认浮层取消路径失败"

        # P0-2: 暂停态大号继续按钮
        story_height_before_continue = app.text.winfo_height()
        app.waiting = "pause"
        app._show_continue_prompt("(按回车继续)")
        app.root.update_idletasks()
        app._resize_choice_area()
        assert app.continue_button is not None, "暂停态未创建继续主按钮"
        assert app.continue_button.winfo_exists(), "继续主按钮控件不存在"
        assert "继续" in app.continue_button.cget("text"), "继续主按钮文案不正确"
        assert app.continue_button.cget("bg") == gui_mod.PRIMARY_BTN, "继续按钮未使用主色"
        assert "剧情暂停" in app.hint_var.get(), "暂停态提示文案未更新"
        assert "阅读完毕" in app._normalize_pause_message("(按回车继续)"), "通用暂停文案未本地化"
        assert abs(app.text.winfo_height() - story_height_before_continue) <= 2, \
            "继续按钮出现导致剧情视口高度突变"
        app._continue()
        assert app.waiting is None, "点击继续后 waiting 未清空"
        assert app.continue_button is None, "继续后主按钮引用未清理"

        # P0-3: 设置面板与偏好持久化
        assert app.settings_button is not None, "设置按钮未创建"
        assert app.settings_button.winfo_viewable(), "设置按钮在默认窗口尺寸下不可见"
        app._open_settings()
        app.root.update()
        assert app._settings_open, "设置面板未能打开"
        # 关闭设置面板
        if callable(app._settings_close):
            app._settings_close()
        app.root.update()
        assert not app._settings_open, "设置面板关闭后仍处于打开状态"

        app._apply_ui_prefs(
            {"font_scale": "large", "fast_text": True, "scroll_speed": "fast"},
            persist=True,
        )
        assert app.prefs["font_scale"] == "large", "字号档位未应用"
        assert app.prefs["scroll_speed"] == "fast", "滚动速度未应用"
        assert gui_mod.LOG_FONT[1] == gui_mod.FONT_SCALE_PRESETS["large"]["log"], \
            "模块级剧情字号未更新"
        assert app.text.cget("font")[1] == gui_mod.FONT_SCALE_PRESETS["large"]["log"] or \
            int(str(app.text.cget("font")).split()[1]) == gui_mod.FONT_SCALE_PRESETS["large"]["log"], \
            "剧情文本控件字号未更新"
        prefs_path = os.path.join(tmp, "ui_prefs.json")
        assert os.path.exists(prefs_path), "界面偏好未写入存档目录"
        reloaded = gui_mod.load_ui_prefs()
        assert reloaded["font_scale"] == "large", "重启读取字号失败"
        assert reloaded["scroll_speed"] == "fast", "重启读取滚动速度失败"
        # 恢复默认，避免污染后续断言依赖
        app._apply_ui_prefs(dict(gui_mod.DEFAULT_UI_PREFS), persist=True)

        # P0-4: 侧栏结构化展示
        app.state.player["attack"] = 42
        app.state.player["defense"] = 33
        app.state.player["speed"] = 28
        app.state.player["spirit"] = 37
        app.state.inventory["兵粮丸"] = 3
        app.state.inventory["起爆符"] = 1
        app.state.team7_trust = 12
        app.state.kakashi_suspicion = 4
        app.state.belonging = 8
        app.state.relations["sasuke"]["trust"] = 9
        app.state.relations["sasuke"]["revenge"] = 2
        app.state.relations["sasuke"]["curse"] = 1
        app.state.relations["sakura"]["confidence"] = 6
        app.state.relations["sakura"]["trust"] = 7
        for contract in app.state.contracts.values():
            if not contract.get("unlocked"):
                contract["unlocked"] = True
                contract["contract_level"] = max(1, int(contract.get("contract_level") or 1))
                break
        app._refresh_status()
        app.root.update_idletasks()
        assert app.stat_vars["attack"].get() == "42", "四维攻击未结构化显示"
        assert app.stat_vars["spirit"].get() == "37", "四维精神未结构化显示"
        assert app.side_lists["items"]["signature"] is not None, "道具列表未刷新"
        assert any(name == "兵粮丸" for name, _ in app.side_lists["items"]["signature"]), \
            "道具未进入结构化列表"
        assert app.side_lists["loadout"]["signature"] is not None, "忍术列表未刷新"
        assert len(app.side_lists["loadout"]["signature"]) >= 1, "忍术列表为空"
        assert app.side_lists["gear"]["signature"] is not None, "忍具列表未刷新"
        assert len(app.side_lists["gear"]["signature"]) == 3, "忍具槽位应为 3 行"
        assert app.metric_rows["sasuke"]["trust"].get() == "9", "佐助信任指标未更新"
        assert app.metric_rows["sakura"]["confidence"].get() == "6", "小樱自信指标未更新"
        assert app.side_lists["contracts"]["signature"] is not None, "契约列表未刷新"
        # 二次刷新签名不变（不闪烁重建）
        first_sig = app.side_lists["items"]["signature"]
        app._refresh_status()
        assert app.side_lists["items"]["signature"] is first_sig, "列表签名缓存失效导致无谓重建"

        # 插图居中：场景画布应能重绘且保留横幅
        app._redraw_visual()
        app.root.update_idletasks()
        assert app._banner_photo is not None, "场景插图丢失"
        assert app.visual_canvas.find_all(), "场景画布未绘制内容"

        # 技能列表滚轮：内容溢出时应可滚动（不依赖滚动条是否 pack）
        app._prompt = "使用哪个技能？"
        app._options = [
            ui_mod.Choice(
                f"测试技能{index + 1} (威力 {10 + index} 查克拉 {5 + index})",
                ("skills", "basic_taijutsu"),
                detail="用于验证技能卡滚轮",
            )
            for index in range(12)
        ]
        app._allow_cancel = False
        app.waiting = "choose"
        app._show_choices()
        app.root.update_idletasks()
        app._resize_choice_area()
        assert app._choice_content_overflows(), "大量技能卡未超出行动区高度"
        top_before = app.choice_canvas.yview()[0]
        class _Wheel:
            delta = -120
            num = 0
        app._scroll_choices(_Wheel())
        app.root.update_idletasks()
        top_after = app.choice_canvas.yview()[0]
        assert top_after > top_before, "技能列表滚轮未滚动视口"
        app._clear_buttons()
        app.waiting = None
        app._prompt = ""

        app._open_collection()
        app.root.update()
        collection_windows = [w for w in app.root.winfo_children() if w.winfo_class() == "Toplevel"]
        assert collection_windows, "收藏馆独立页未能打开"
        for window in collection_windows:
            assert "剧情分支图" in window.collection_tabs, "收藏馆缺少剧情分支图"
            assert "恋爱线阶段图" in window.collection_tabs, "收藏馆缺少恋爱线阶段图"
            assert "技能图标" in window.collection_tabs, "收藏馆缺少技能图标页"
            assert "契约徽章" in window.collection_tabs, "收藏馆缺少契约徽章页"
            assert "成就徽章" in window.collection_tabs, "收藏馆缺少成就徽章页"
            assert "结局徽章" in window.collection_tabs, "收藏馆缺少结局徽章页"
            assert window.story_graph_canvas.find_all(), "剧情分支图没有绘制内容"
            assert window.romance_graph_canvas.find_all(), "恋爱线阶段图没有绘制内容"
            window.destroy()
        print(f"SMOKE TEST PASS (交互 {interactions} 次,自动存档已写入)",
              file=REAL_STDOUT)
    finally:
        sys.stdout = REAL_STDOUT
        try:
            if getattr(app, "_settings_open", False) and callable(getattr(app, "_settings_close", None)):
                app._settings_close()
            if app._modal_active:
                app._close_game_modal("ok")
            app.root.destroy()
        except Exception:
            pass
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    main()
