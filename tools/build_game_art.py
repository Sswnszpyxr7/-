# -*- coding: utf-8 -*-
"""构建图标生图清单，并把生成图集处理为游戏可用资源。"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageOps

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from systems import icon_assets  # noqa: E402


DEFAULT_PROMPTS = ROOT / "output" / "imagegen" / "icon-prompts.jsonl"
DEFAULT_SOURCE = ROOT / "output" / "imagegen" / "icon-sources"
DEFAULT_QA = ROOT / "output" / "imagegen" / "icon-checks"

ICON_SIZES = {
    "elements": 64,
    "status": 32,
    "intents": 48,
    "reactions": 48,
    "actions": 48,
    "equipment": 64,
    "items": 64,
    "affixes": 48,
    "contracts": 128,
    "achievements": 128,
    "endings": 128,
    "skills": 64,
}

CONCEPTS = {
    "elements": {
        "fire": "a curling orange-red flame around a coal ember",
        "wind": "a sharp turquoise crescent gust with three streaming arcs",
        "lightning": "a branching electric bolt around a bright violet core",
        "water": "a blue whirlpool and suspended water droplet",
        "earth": "layered ochre stone plates rising like a barrier",
        "wood": "a living branch and fresh leaves twisting upward",
        "yin": "a dark crescent moon with a violet illusion ripple",
        "yang": "a radiant ivory sun spiral with warm gold rays",
        "seal": "concentric crimson sealing rings and crossed energy chains",
        "medical": "a mint-green healing palm over a pulse of light",
        "taijutsu": "a bandaged fist striking through a circular shockwave",
        "genjutsu": "a hypnotic indigo eye surrounded by warped rings",
        "tailed_beast": "a fierce red-orange chakra beast silhouette with nine flowing tails",
    },
    "intents": {
        "fatal": "a crimson meteor impact and fractured warning halo",
        "control": "violet binding cords locking a faceted target crystal",
        "support": "a jade shield with an upward golden chakra stream",
        "attack": "a bright steel slash and forward red impact arrow shape without text",
    },
    "status": {
        "burn": "a charred silhouette engulfed by orange flame",
        "paralyze": "a stunned silhouette crossed by electric arcs",
        "poison": "a violet venom drop above curling toxic vapor",
        "confuse": "a tilted mask surrounded by spiraling stars",
        "bleed": "three sharp crimson claw marks and falling droplets",
        "spirit_shake": "a cracked translucent spirit mask with purple vibration rings",
        "defense_up": "a blue steel shield reinforced by an upward chevron",
        "evade_up": "a white afterimage slipping past a curved attack trail",
        "clone_guard": "two pale shadow silhouettes guarding the central figure",
        "sealed": "red chakra chains closing around a dark core",
        "cloak": "a red fox-shaped chakra mantle around a human silhouette",
        "attack_up": "a glowing fist and rising scarlet energy flare",
        "nine_shield": "nine golden threads woven into a luminous protective circle",
        "fear": "a black staring mask with a cold blue aura",
        "chakra_disorder": "a tangled cyan chakra coil broken by magenta static",
        "wet": "three clear blue droplets and rippling rings",
    },
    "reactions": {
        "douse": "blue water crashing over an orange flame and releasing white vapor",
        "electrocharged": "a water droplet pierced by branching yellow lightning",
        "steam_burst": "red flame and blue water colliding in a white steam burst",
        "fan_flame": "turquoise wind crescents feeding a sweeping orange fire wave",
        "mud_trap": "a boot sinking into spiraling brown mud and blue water",
    },
    "actions": {
        "battle_start": "two dark steel kunai crossing in front of a compact orange-gold chakra burst",
        "attack": "a wrapped fist crossing a bright elemental chakra slash",
        "guard": "a reinforced forearm guard deflecting a sharp impact spark",
        "item": "a compact ninja supply pouch with one glowing medicine vial",
        "contract": "two luminous life threads joining at a small summoning seal",
        "retreat": "a swift ninja silhouette leaping away through a smoke burst",
        "position": "three tactical ground markers connected by a curved movement arrow",
        "ally_order": "three allied silhouettes arranged around a tactical command marker",
        "ally_ultimate": "two allied chakra streams converging into one brilliant finishing strike",
        "travel": "a ninja sandal stepping across a compact map compass",
        "rest": "a warm camp lantern beside a folded bedroll and calm chakra glow",
        "train": "a battered wooden training post struck by a wrapped fist",
        "explore": "a hooded scout silhouette entering a moonlit forest path",
        "gather": "a medicinal leaf, mineral shard, and small gathering knife",
        "observe": "a focused ninja eye above widening sensory rings",
        "visit": "a warm lantern beside an open doorway with a welcoming glow",
        "heart_talk": "two warm glowing speech wisps connected by one soft golden life-thread knot",
        "gift": "a small crimson gift pouch tied with a gold life-thread bow",
        "contract_tree": "an ancient tree with nine luminous gold and crimson life threads",
        "fate_corridor": "a dark arched doorway opening into a violet-blue spiral path with golden destiny threads",
        "training_court": "a battered wooden practice post struck by a wrapped fist and amber chakra impact",
        "ninjutsu_research": "an open technique scroll with a cyan chakra spiral and analytical sealing rings",
        "tougen_build": "a wooden cottage roof being assembled by a bronze hammer in a warm home aura",
        "quests": "a rolled mission scroll pinned by a small blank wooden tag",
        "status": "a human silhouette beside three clean rising status bars without text",
        "loadout": "a kunai, technique scroll, and armor plate arranged as a tactical kit",
        "faction": "three distinct village banners surrounding a handshake emblem without symbols",
        "workshop": "a blacksmith hammer striking a glowing kunai on a compact anvil",
        "wanted": "a shadowed rogue portrait on torn parchment with a red threat mark and no writing",
        "collection": "an open archive book holding several glowing collectible emblems",
        "new_cycle": "a golden spiral path looping around a rising sun",
        "save": "a sealed memory scroll tied with a glowing green cord",
        "load": "an opening memory scroll releasing a blue scene silhouette",
    },
    "equipment": {
        "kunai_kit": "a compact black leather pouch opened to reveal polished kunai",
        "chakra_blade": "a short ninja blade edged with bright cyan chakra",
        "spiral_gauntlet": "a reinforced orange bracer surrounding a blue wind spiral",
        "hunter_blade": "a rugged dark tracking sword with a notched silver edge",
        "genin_vest": "a practical olive ninja protective vest",
        "medic_coat": "a clean white-and-teal field medic coat with utility pockets",
        "nine_thread_cloak": "a dark cloak woven with nine thin luminous gold threads",
        "serpent_guard": "layered charcoal armor made from iridescent snake scales",
        "seal_charm": "a rolled crimson-edged sealing charm with abstract spiral marks",
        "wind_talisman": "a jade pendant holding a miniature crescent wind vortex",
        "bond_token": "three linked metal leaves forming a warm team medallion",
        "war_emblem": "a weathered bronze allied-forces medal with crossed banner shapes",
        "tempered_kunai": "three mirror-polished forged kunai bound in dark red cord",
        "chakra_mail": "interlocking dark steel chainmail rings threaded with cyan chakra",
        "medic_charm": "a white ceramic healing charm with a mint pulse crystal",
        "will_of_fire_charm": "a bronze leaf-shaped charm surrounding a warm amber flame",
        "suna_guard_mail": "layered sand-gold armor plates flowing around a guarded heart",
        "alliance_chakra_blade": "a balanced silver combat blade edged in five interwoven chakra colors",
        "explosive_kunai": "two black kunai wrapped with compact orange explosive tags without writing",
        "poison_senbon": "an open lacquered case of silver senbon with violet medicinal droplets",
        "puppet_blade": "a segmented red-bronze mechanical blade with visible chakra joints",
        "sage_staff": "a knotted ancient wooden staff capped by a jade natural-energy ring",
        "paper_fan": "a white folded-paper war fan with blue chakra-edged feathers",
        "forest_cloak": "a moss-green travel cloak clasped with a small wooden leaf",
        "sandweave_armor": "tan woven armor reinforced by floating iron-sand scales",
        "sage_robe": "an ochre and deep-red training robe with a natural-energy spiral clasp",
        "paper_mantle": "a mantle of overlapping white paper feathers with pale blue edges",
        "war_plate": "heavy dark allied battle armor joined by five colored fastening cords",
        "tracking_lens": "a compact brass monocular lens glowing with concentric sensory rings",
        "toxin_charm": "a sealed violet antidote gourd protected by green medicinal leaves",
        "frog_charm": "a carved jade frog charm holding a tiny natural-energy pearl",
        "rain_amulet": "a blue paper-flower pendant with one suspended rain droplet",
        "fate_compass": "a gold-and-obsidian compass woven from nine luminous life threads",
    },
    "items": {
        "ration_pill": "three dark brown soldier ration pills in a small paper packet",
        "healing_pill": "a glossy red medicinal pill beside a tiny ceramic vial",
        "chakra_pill": "a luminous blue chakra pill inside a glass capsule",
        "medicinal_herb": "a fresh bundle of healing leaves tied with white thread",
        "antidote_pill": "two pale green antidote pills beside a tiny sealed medicine pouch",
        "revival_elixir": "a crimson-gold restorative elixir glowing inside a small crystal vial",
        "strong_ration": "three dense black-red enhanced ration pills in reinforced paper wrapping",
        "focus_pill": "a translucent indigo pill surrounded by a calm circular chakra ripple",
        "material_wood": "a neat bundle of seasoned dark cedar slats and carved wooden pegs",
        "material_iron_sand": "a small open pouch of glittering black iron sand held by magnetic arcs",
        "material_chakra_shard": "a faceted cyan chakra crystal shard with light trapped inside",
        "material_venom_sac": "a sealed purple venom sac with two small fang marks",
        "material_beast_bone": "clean ivory beast-bone segments suitable for crafting joints",
        "material_explosive_clay": "a compact lump of pale explosive clay with an orange warning glow and no markings",
        "material_fine_cloth": "a folded bolt of durable midnight-blue ninja cloth with visible weave",
        "material_seal_ink": "a stoppered black-red ink bottle beside a clean brush with no writing",
        "material_nature_crystal": "a moss-green natural-energy crystal sprouting tiny leaves",
        "material_paper_fiber": "a bundle of luminous white paper fibers and folded strips",
        "ryo_coin": "a small stack of worn bronze ninja-era coins with square holes and no writing",
    },
    "affixes": {
        "swift": "a silver claw streaking through three blue speed lines",
        "armored": "a heavy iron helmet and layered shield plates",
        "berserk": "a cracked red oni mask surrounded by violent flame",
        "chakra": "a bright cyan chakra sphere overflowing with energy ribbons",
        "regenerative": "a green heart-shaped leaf closing a glowing wound",
        "venomous": "two purple serpent fangs dripping venom",
        "gear_power": "a razor-bright silver weapon edge cutting through a red spark",
        "gear_guard": "a layered blue shield anchored by a heavy stone base",
        "gear_light": "a pale feather crossing three turquoise speed arcs",
        "gear_breaker": "a steel wedge splitting a cracked enemy guard plate",
        "gear_medic": "a green healing pulse blooming from a white bandage knot",
        "gear_bond": "two gold chakra cords tied into one unbreakable knot",
        "gear_reaction": "five elemental sparks converging into a bright central ring",
        "gear_seal": "crimson sealing rings closing around a dark technique core",
    },
    "contracts": {
        "kushina": "a red spiral seal guarded by two radiant chakra chains",
        "rin": "a blue healing bell cradled by gentle water light",
        "tsunade": "a violet diamond seal above a pale healing slug silhouette",
        "sakura": "a cherry blossom struck by a powerful gloved fist",
        "shizune": "a precise silver senbon crossing a mint antidote vial",
        "hinata": "a pale lavender all-seeing eye framed by gentle-fist chakra",
        "konan": "a blue paper rose opening into angelic paper wings",
        "mei": "a crimson lava fan meeting a turquoise mist wave",
        "gaia": "golden roots embracing a small green world-heart",
    },
    "achievements": {
        "first_action": "a sunrise behind a newly opened ninja scroll",
        "event_hunter": "an attentive ear beside a village lantern and tiny footprints",
        "world_walker": "worn sandals crossing a stylized map compass",
        "full_loadout": "six distinct ninja technique cards arranged like a complete hand",
        "two_companions": "three linked silhouettes running forward together",
        "first_contract": "one golden life-thread tying two small lights",
        "nine_contracts": "nine golden life-threads woven into a complete circular crest",
        "skill_scholar": "an open technique scroll surrounded by elemental sparks",
        "first_ending": "a road splitting into two luminous paths",
        "ending_collector": "five sealed memory cards orbiting a crystal archive",
        "true_end": "nine brilliant threads converging into a sunrise over a flowering tree",
    },
    "endings": {
        "wave_canon": "a broken sword fading into cold sea mist on a bridge",
        "wave_haku": "a single white ice flower opening beside a quiet bridge",
        "wave_perfect": "two traveler silhouettes leaving a thawing bridge at dawn",
        "sasuke_canon": "a lone dark figure walking beyond a moonlit valley gate",
        "sasuke_promise": "two hands separated by distance but joined by a thin blue thread",
        "sasuke_guarded": "a guarded village gate beneath an uneasy blue moon",
        "sasuke_alliance": "two rival crests joined over a cracked valley statue",
        "war_standard": "a torn allied banner standing in rain over a silent battlefield",
        "war_true": "nine golden life-lines sheltering the whole village beneath sunrise",
    },
}

WANTED_PROMPTS = {
    "forest_alpha": (
        "a gigantic scarred gray forest wolf alpha snarling from tangled cedar roots, "
        "feral amber eyes, torn ear, fast predator posture"
    ),
    "rogue_hunter": (
        "a dangerous border-crossing rogue ninja hunter in layered charcoal armor, lower face masked, "
        "weathered tracking blade and poisoned kunai"
    ),
    "serpent_king": (
        "a colossal dark emerald king serpent coiled among ancient trees, pale fangs, old scars, "
        "regenerative scale patterns and venom mist"
    ),
    "red_cloud_agent": (
        "an elite covert agent in a black high-collared cloak patterned with abstract dark-red cloud shapes, "
        "face partly hidden, several elemental chakra lights around the hands"
    ),
    "zetsu_commander": (
        "a pale plant-like humanoid war remnant commander, asymmetrical flytrap collar, twisted roots, "
        "multiple fused faces suggested in the torso, unsettling battlefield presence"
    ),
}


def _entries(category, mapping):
    return [(category, asset_id, label) for asset_id, label in mapping.items()]


LEGACY_EQUIPMENT_IDS = {
    "kunai_kit", "chakra_blade", "spiral_gauntlet", "hunter_blade", "genin_vest",
    "medic_coat", "nine_thread_cloak", "serpent_guard", "seal_charm", "wind_talisman",
    "bond_token", "war_emblem",
}
LEGACY_ITEM_IDS = {"ration_pill", "healing_pill", "chakra_pill", "medicinal_herb"}
LEGACY_AFFIX_IDS = {"swift", "armored", "berserk", "chakra", "regenerative", "venomous"}


def _selected(mapping, ids):
    return {asset_id: mapping[asset_id] for asset_id in mapping if asset_id in ids}


def _sheet_specs():
    specs = [
        (
            "sheet-core.png",
            5,
            _entries("elements", icon_assets.ELEMENT_NAMES)
            + _entries("intents", icon_assets.INTENT_NAMES),
        ),
        (
            "sheet-conditions.png",
            5,
            _entries("status", icon_assets.STATUS_NAMES)
            + _entries("reactions", icon_assets.REACTION_NAMES),
        ),
        ("sheet-actions.png", 5, _entries("actions", icon_assets.ACTION_NAMES)),
        (
            "sheet-inventory.png",
            5,
            _entries("equipment", _selected(icon_assets.EQUIPMENT_NAMES, LEGACY_EQUIPMENT_IDS))
            + _entries("items", _selected(icon_assets.ITEM_NAMES, LEGACY_ITEM_IDS))
            + _entries("affixes", _selected(icon_assets.AFFIX_NAMES, LEGACY_AFFIX_IDS)),
        ),
        (
            "sheet-legacy.png",
            5,
            _entries("contracts", icon_assets.CONTRACT_NAMES)
            + _entries("achievements", icon_assets.ACHIEVEMENT_NAMES),
        ),
        ("sheet-endings.png", 3, _entries("endings", icon_assets.ENDING_NAMES)),
    ]
    skill_entries = _entries("skills", icon_assets.SKILL_NAMES)
    for index in range(0, len(skill_entries), 16):
        specs.append((f"sheet-skills-{index // 16 + 1}.png", 4, skill_entries[index:index + 16]))
    economy_entries = (
        _entries("equipment", {
            key: value for key, value in icon_assets.EQUIPMENT_NAMES.items()
            if key not in LEGACY_EQUIPMENT_IDS
        })
        + _entries("items", {
            key: value for key, value in icon_assets.ITEM_NAMES.items()
            if key not in LEGACY_ITEM_IDS
        })
        + _entries("affixes", {
            key: value for key, value in icon_assets.AFFIX_NAMES.items()
            if key not in LEGACY_AFFIX_IDS
        })
    )
    for index in range(0, len(economy_entries), 25):
        specs.append((f"sheet-economy-{index // 25 + 1}.png", 5, economy_entries[index:index + 25]))
    return specs


def _concept(category, asset_id, label):
    if category == "skills":
        with (ROOT / "data" / "skills.json").open(encoding="utf-8") as handle:
            skill = json.load(handle)[asset_id]
        element = icon_assets.ELEMENT_NAMES.get(skill.get("element"), skill.get("element", ""))
        effect = skill.get("effect") or "clean decisive impact"
        return f"{label}, {element} nature, visual effect concept: {effect}"
    return CONCEPTS[category][asset_id]


def _sheet_prompt(filename, columns, entries):
    rows = columns
    cells = []
    for index, (category, asset_id, label) in enumerate(entries):
        row, column = divmod(index, columns)
        cells.append(
            f"row {row + 1} column {column + 1}: {label} ({asset_id}) — "
            f"{_concept(category, asset_id, label)}"
        )
    capacity = columns * rows
    for index in range(len(entries), capacity):
        row, column = divmod(index, columns)
        cells.append(f"row {row + 1} column {column + 1}: an empty dark tile with no symbol")
    return "\n".join(
        [
            "Create a production-ready icon atlas for a dark Japanese ninja-fantasy RPG.",
            f"The canvas is a strict {columns} by {rows} grid in exact row-major order.",
            "Every cell is an equal square dark obsidian rounded tile separated by thin black gutters.",
            "Each populated tile contains one centered emblem with a strong silhouette, refined cel-painted detail, "
            "subtle gold rim, restrained elemental glow, and consistent three-quarter relief.",
            "Keep every emblem fully inside its own cell with generous padding; nothing may cross a cell boundary.",
            "Cell assignments:",
            *cells,
            "No text, letters, numbers, kanji, labels, logos, UI captions, signatures, or watermarks anywhere.",
            "Do not merge cells. Do not change the order. Keep the visual system consistent across the complete atlas.",
            f"Internal production filename reference only: {filename}.",
        ]
    )


def _wanted_prompt(target_id, label):
    return "\n".join(
        [
            "Create a vertical collectible wanted-poster illustration for a dark Japanese ninja-fantasy RPG.",
            f"Target concept: {label} — {WANTED_PROMPTS[target_id]}.",
            "Aged parchment mounted on a weathered mission board, hand-painted anime wanted portrait, "
            "ink splashes, torn fibers, red threat-stamp shapes with no glyphs, and a blank nameplate area.",
            "Strong centered target silhouette, head and torso or full creature visible, dramatic but readable at thumbnail size.",
            "Muted sepia paper with one target-specific accent color, polished game collectible quality.",
            "No readable text, no letters, no numbers, no logos, no signatures, no watermark, no extra characters.",
        ]
    )


def _spec_has_missing_icons(spec):
    _filename, _columns, entries = spec
    return any(not icon_assets.icon_path(category, asset_id).is_file()
               for category, asset_id, _label in entries)


def write_prompts(path, missing_only=False):
    path.parent.mkdir(parents=True, exist_ok=True)
    jobs = []
    specs = [spec for spec in _sheet_specs() if not missing_only or _spec_has_missing_icons(spec)]
    for filename, columns, entries in specs:
        jobs.append(
            {
                "out": filename,
                "prompt": _sheet_prompt(filename, columns, entries),
                "use_case": "stylized-concept",
                "style": "cohesive premium 2D anime RPG interface art, crisp iconography",
                "composition": "strict equal-cell icon atlas with exact row-major ordering",
                "constraints": "no text, no logo, no watermark, no cross-cell elements",
                "size": "1024x1024",
                "quality": "medium",
                "model": "gpt-image-2",
            }
        )
    for target_id, label in (() if missing_only else icon_assets.WANTED_NAMES.items()):
        jobs.append(
            {
                "out": f"wanted-{target_id}.png",
                "prompt": _wanted_prompt(target_id, label),
                "use_case": "stylized-concept",
                "style": "polished anime RPG collectible poster, painterly ink and parchment texture",
                "composition": "vertical centered target portrait with complete parchment edges",
                "constraints": "no readable text, no logo, no watermark",
                "size": "1024x1536",
                "quality": "medium",
                "model": "gpt-image-2",
            }
        )
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for job in jobs:
            handle.write(json.dumps(job, ensure_ascii=False, separators=(",", ":")) + "\n")
    print(f"wrote {len(jobs)} generation jobs to {path}")


def _crop_sheet(source, columns, entries):
    image = Image.open(source).convert("RGB")
    rows = columns
    crops = []
    for index, entry in enumerate(entries):
        row, column = divmod(index, columns)
        left = round(column * image.width / columns)
        right = round((column + 1) * image.width / columns)
        top = round(row * image.height / rows)
        bottom = round((row + 1) * image.height / rows)
        cell = image.crop((left, top, right, bottom))
        inset = max(1, round(min(cell.size) * 0.018))
        cell = cell.crop((inset, inset, cell.width - inset, cell.height - inset))
        crops.append((entry, cell))
    return crops


def _save_icons(source_dir, only_missing=False):
    saved = []
    for filename, columns, entries in _sheet_specs():
        source = source_dir / filename
        if not source.is_file():
            if only_missing and not _spec_has_missing_icons((filename, columns, entries)):
                continue
            raise FileNotFoundError(source)
        for (category, asset_id, _label), image in _crop_sheet(source, columns, entries):
            size = ICON_SIZES[category]
            output = icon_assets.icon_path(category, asset_id)
            if only_missing and output.is_file():
                continue
            output.parent.mkdir(parents=True, exist_ok=True)
            ImageOps.fit(image, (size, size), method=Image.Resampling.LANCZOS).save(output, "PNG")
            saved.append(output)
    return saved


def _save_posters(source_dir):
    outputs = []
    (icon_assets.WANTED_ROOT / "thumbs").mkdir(parents=True, exist_ok=True)
    for target_id in icon_assets.WANTED_NAMES:
        source = source_dir / f"wanted-{target_id}.png"
        if not source.is_file():
            raise FileNotFoundError(source)
        image = Image.open(source).convert("RGB")
        poster = ImageOps.fit(image, (256, 320), method=Image.Resampling.LANCZOS, centering=(0.5, 0.45))
        output = icon_assets.wanted_path(target_id)
        output.parent.mkdir(parents=True, exist_ok=True)
        poster.save(output, "PNG")
        poster.resize((64, 80), Image.Resampling.LANCZOS).save(
            icon_assets.wanted_path(target_id, thumbnail=True),
            "PNG",
        )
        outputs.append(output)
    return outputs


def _hex_rgb(value):
    value = value.lstrip("#")
    return tuple(int(value[index:index + 2], 16) for index in (0, 2, 4))


def _portrait_panel(portrait_id, size, accent):
    source = icon_assets.ASSET_ROOT / "portraits" / f"{portrait_id}.png"
    portrait = Image.open(source).convert("RGB")
    portrait = ImageOps.fit(portrait, (size, size), method=Image.Resampling.LANCZOS, centering=(0.5, 0.38))
    color = Image.new("RGB", portrait.size, accent)
    portrait = Image.blend(portrait, Image.blend(portrait, color, 0.18), 0.5)
    mask = Image.new("L", portrait.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.polygon(((42, 0), (size, 0), (size - 36, size), (0, size)), fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(1.2))
    return portrait, mask


def _compose_boss_cutins():
    output_dir = icon_assets.BOSS_CUTIN_ROOT
    output_dir.mkdir(parents=True, exist_ok=True)
    outputs = []
    for enemy_id, (_name, portrait_id, illustration_id, accent_hex, secondary_id) in icon_assets.BOSS_META.items():
        background_path = icon_assets.ASSET_ROOT / "illustrations" / f"{illustration_id}.png"
        background = Image.open(background_path).convert("RGB")
        background = ImageOps.fit(background, (832, 208), method=Image.Resampling.LANCZOS)
        background = ImageEnhance.Color(background).enhance(0.72)
        background = ImageEnhance.Brightness(background).enhance(0.58)
        accent = _hex_rgb(accent_hex)
        tint = Image.new("RGB", background.size, accent)
        background = Image.blend(background, tint, 0.12)
        canvas = background.convert("RGBA")

        overlay = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        draw.rectangle((0, 0, 832, 22), fill=(7, 9, 14, 190))
        draw.rectangle((0, 184, 832, 208), fill=(7, 9, 14, 210))
        draw.polygon(((350, 0), (832, 0), (832, 208), (275, 208)), fill=(*accent, 38))
        for index in range(8):
            y = 26 + index * 22
            draw.line((255 + index * 11, y, 820, y - 34), fill=(*accent, 70), width=2)
        canvas = Image.alpha_composite(canvas, overlay)

        if secondary_id:
            panel, mask = _portrait_panel(secondary_id, 250, accent)
            layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
            layer.paste(panel.convert("RGBA"), (370, -18), mask)
            layer = ImageEnhance.Brightness(layer).enhance(0.62)
            canvas = Image.alpha_composite(canvas, layer)

        panel, mask = _portrait_panel(portrait_id, 310, accent)
        glow = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
        glow_draw = ImageDraw.Draw(glow)
        glow_draw.ellipse((500, -100, 900, 300), fill=(*accent, 80))
        glow = glow.filter(ImageFilter.GaussianBlur(28))
        canvas = Image.alpha_composite(canvas, glow)
        layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
        layer.paste(panel.convert("RGBA"), (535, -45), mask)
        canvas = Image.alpha_composite(canvas, layer)

        frame = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
        frame_draw = ImageDraw.Draw(frame)
        frame_draw.line((250, 205, 820, 32), fill=(*accent, 230), width=3)
        frame_draw.line((280, 208, 820, 46), fill=(240, 240, 235, 120), width=1)
        canvas = Image.alpha_composite(canvas, frame)

        output = icon_assets.boss_cutin_path(enemy_id)
        canvas.convert("RGB").save(output, "PNG")
        outputs.append(output)
    return outputs


def _contact_sheet(paths, output, thumb_size=(96, 96), columns=8):
    paths = list(paths)
    if not paths:
        return
    label_height = 24
    rows = math.ceil(len(paths) / columns)
    sheet = Image.new(
        "RGB",
        (columns * thumb_size[0], rows * (thumb_size[1] + label_height)),
        (18, 21, 28),
    )
    draw = ImageDraw.Draw(sheet)
    for index, path in enumerate(paths):
        row, column = divmod(index, columns)
        x, y = column * thumb_size[0], row * (thumb_size[1] + label_height)
        image = Image.open(path).convert("RGB")
        image = ImageOps.contain(image, thumb_size, method=Image.Resampling.LANCZOS)
        px = x + (thumb_size[0] - image.width) // 2
        py = y + (thumb_size[1] - image.height) // 2
        sheet.paste(image, (px, py))
        draw.text((x + 3, y + thumb_size[1] + 4), path.stem[:18], fill=(220, 224, 232))
    output.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(output, "PNG")


def _write_qa(saved_icons, posters, cutins, qa_dir):
    qa_dir.mkdir(parents=True, exist_ok=True)
    by_category = {}
    for path in saved_icons:
        by_category.setdefault(path.parent.name, []).append(path)
    for category, paths in by_category.items():
        _contact_sheet(sorted(paths), qa_dir / f"{category}.png")
    _contact_sheet(posters, qa_dir / "wanted-posters.png", thumb_size=(128, 160), columns=5)
    _contact_sheet(cutins, qa_dir / "boss-cutins.png", thumb_size=(208, 52), columns=4)


def validate():
    errors = []
    counts = {}
    for category, asset_id, path in icon_assets.expected_icons():
        counts[category] = counts.get(category, 0) + 1
        if not path.is_file():
            errors.append(f"missing icon: {category}/{asset_id}")
            continue
        with Image.open(path) as image:
            expected = ICON_SIZES[category]
            if image.size != (expected, expected):
                errors.append(f"wrong size: {path} = {image.size}, expected {(expected, expected)}")
            image.verify()
    for target_id in icon_assets.WANTED_NAMES:
        for thumbnail, expected in ((False, (256, 320)), (True, (64, 80))):
            path = icon_assets.wanted_path(target_id, thumbnail=thumbnail)
            if not path.is_file():
                errors.append(f"missing wanted poster: {path}")
                continue
            with Image.open(path) as image:
                if image.size != expected:
                    errors.append(f"wrong size: {path} = {image.size}, expected {expected}")
                image.verify()
    for enemy_id in icon_assets.BOSS_META:
        path = icon_assets.boss_cutin_path(enemy_id)
        if not path.is_file():
            errors.append(f"missing boss cut-in: {path}")
            continue
        with Image.open(path) as image:
            if image.size != (832, 208):
                errors.append(f"wrong size: {path} = {image.size}, expected {(832, 208)}")
            image.verify()
    report = {"counts": counts, "wanted": len(icon_assets.WANTED_NAMES), "boss_cutins": len(icon_assets.BOSS_META)}
    if errors:
        report["errors"] = errors
        raise RuntimeError(json.dumps(report, ensure_ascii=False, indent=2))
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return report


def process(source_dir, qa_dir):
    icons = _save_icons(source_dir)
    posters = _save_posters(source_dir)
    cutins = _compose_boss_cutins()
    _write_qa(icons, posters, cutins, qa_dir)
    validate()


def process_missing(source_dir, qa_dir):
    icons = _save_icons(source_dir, only_missing=True)
    _write_qa(icons, [], [], qa_dir)
    validate()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-prompts", type=Path)
    parser.add_argument("--write-missing-prompts", type=Path)
    parser.add_argument("--process", type=Path)
    parser.add_argument("--process-missing", type=Path)
    parser.add_argument("--compose-boss", action="store_true")
    parser.add_argument("--qa-dir", type=Path, default=DEFAULT_QA)
    parser.add_argument("--validate", action="store_true")
    args = parser.parse_args()
    if not any((args.write_prompts, args.write_missing_prompts, args.process,
                args.process_missing, args.compose_boss, args.validate)):
        args.write_prompts = DEFAULT_PROMPTS
    if args.write_prompts:
        write_prompts(args.write_prompts)
    if args.write_missing_prompts:
        write_prompts(args.write_missing_prompts, missing_only=True)
    if args.process_missing:
        process_missing(args.process_missing, args.qa_dir)
    elif args.process:
        process(args.process, args.qa_dir)
    elif args.compose_boss:
        cutins = _compose_boss_cutins()
        _contact_sheet(cutins, args.qa_dir / "boss-cutins.png", thumb_size=(208, 52), columns=4)
        print(f"wrote {len(cutins)} Boss cut-ins")
    elif args.validate:
        validate()


if __name__ == "__main__":
    main()
