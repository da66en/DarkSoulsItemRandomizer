# TODO: is lightning spear, great lightening spear and sunlight spear being shuffled in?
# TODO: generate cheat sheet doesn't do seek guidance hints or show sync-num

import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox as tkMB
import random
import hashlib
import sys
import os
import datetime
import shutil
import webbrowser
import requests
from distutils.version import LooseVersion

import randomizer_options as rngopts
import randomize_item_table
import starting_gifts_setup as gift_s
import bnd_rebuilder
import dcx_handler
from fmg_handler import FMGHandler

import logging

from settings_string_io import SettingsStringIO, SettingsVariable, IncompatibleVersionError, InvalidValueError

log = logging.getLogger(__name__)

import ini_parser 
INI_FILE = "randomizer.ini"

MAX_SEED_LENGTH = 64

# Save folders live under <Documents>\NBGI\.
PTDE_SAVE_FOLDER_NAME = "DarkSouls"
DS1R_SAVE_FOLDER_NAME = "DARK SOULS REMASTERED"

def get_documents_dirs():
    """Every plausible Documents folder: the shell's (follows OneDrive/redirection) plus the defaults."""
    dirs = []
    try:
        import ctypes
        from ctypes import wintypes
        buf = ctypes.create_unicode_buffer(wintypes.MAX_PATH)
        CSIDL_PERSONAL = 5
        if ctypes.windll.shell32.SHGetFolderPathW(None, CSIDL_PERSONAL, None, 0, buf) == 0:
            dirs.append(buf.value)
    except Exception:
        pass
    home = os.path.expanduser("~")
    dirs.append(os.path.join(home, "Documents"))
    dirs.append(os.path.join(home, "OneDrive", "Documents"))
    unique_dirs = {}
    for d in dirs:
        unique_dirs.setdefault(os.path.normcase(os.path.normpath(d)), os.path.normpath(d))
    return list(unique_dirs.values())

VERSION_NUM = "1.0.5"
# only add versions compatible RNG-wise, IE when fixing GUI stuff
COMPATIBLE_VERSIONS = [VERSION_NUM]

#PTDE_GAMEPARAM_PATH_LIST = ["./GameParam.parambnd", "./param/GameParam/GameParam.parambnd", "C:\Program Files (x86)\Steam\steamapps\common\Dark Souls Prepare to Die Edition\DATA\param\GameParam\GameParam.parambnd", "C:\Programs\Steam\steamapps\common\Dark Souls Prepare to Die Edition\DATA\param\GameParam\GameParam.parambnd"]
#DS1R_GAMEPARAM_PATH_LIST = ["./GameParam.parambnd.dcx", "./param/GameParam/GameParam.parambnd.dcx", "D:\SteamLibrary\steamapps\common\DARK SOULS REMASTERED\param\GameParam\GameParam.parambnd.dcx", "D:\Program Files (x86)\Steam\steamapps\common\DARK SOULS REMASTERED\param\GameParam\GameParam.parambnd.dcx", "C:\programs\Steam\steamapps\common\DARK SOULS REMASTERED\param\GameParam\GameParam.parambnd.dcx"]

#PTDE_ENGMENU_PATH_LIST = ["./msg/ENGLISH/menu.msgbnd", "C:\Program Files (x86)\Steam\steamapps\common\Dark Souls Prepare to Die Edition\DATA\msg\ENGLISH\menu.msgbnd", "C:\Programs\Steam\steamapps\common\Dark Souls Prepare to Die Edition\DATA\msg\ENGLISH\menu.msgbnd"]
#DS1R_ENGMENU_PATH_LIST = ["./msg/ENGLISH/menu.msgbnd.dcx", "D:\SteamLibrary\steamapps\common\DARK SOULS REMASTERED\msg\ENGLISH\menu.msgbnd.dcx", "D:\Program Files (x86)\Steam\steamapps\common\DARK SOULS REMASTERED\msg\ENGLISH\menu.msgbnd.dcx", "C:\Programs\Steam\steamapps\common\DARK SOULS REMASTERED\msg\ENGLISH\menu.msgbnd.dcx"]

PTDE_GAMEPARAM_PATH_LIST = ["./GameParam.parambnd", "./param/GameParam/GameParam.parambnd", "C:\\Program Files (x86)\\Steam\\steamapps\\common\\Dark Souls Prepare to Die Edition\\DATA\\param\\GameParam\\GameParam.parambnd", "C:\\Programs\\Steam\\steamapps\\common\\Dark Souls Prepare to Die Edition\\DATA\\param\\GameParam\\GameParam.parambnd"]
DS1R_GAMEPARAM_PATH_LIST = ["./GameParam.parambnd.dcx", "./param/GameParam/GameParam.parambnd.dcx", "D:\\SteamLibrary\\steamapps\\common\\DARK SOULS REMASTERED\\param\\GameParam\\GameParam.parambnd.dcx", "D:\\Program Files (x86)\\Steam\\steamapps\\common\\DARK SOULS REMASTERED\\param\\GameParam\\GameParam.parambnd.dcx", "C:\\programs\\Steam\\steamapps\\common\\DARK SOULS REMASTERED\\param\\GameParam\\GameParam.parambnd.dcx"]

PTDE_ENGMENU_PATH_LIST = ["./msg/ENGLISH/menu.msgbnd", "C:\\Program Files (x86)\\Steam\\steamapps\\common\\Dark Souls Prepare to Die Edition\\DATA\\msg\\ENGLISH\\menu.msgbnd", "C:\\Programs\\Steam\\steamapps\\common\\Dark Souls Prepare to Die Edition\\DATA\\msg\\ENGLISH\\menu.msgbnd"]
DS1R_ENGMENU_PATH_LIST = ["./msg/ENGLISH/menu.msgbnd.dcx", "D:\\SteamLibrary\\steamapps\\common\\DARK SOULS REMASTERED\\msg\\ENGLISH\\menu.msgbnd.dcx", "D:\\Program Files (x86)\\Steam\\steamapps\\common\\DARK SOULS REMASTERED\\msg\\ENGLISH\\menu.msgbnd.dcx", "C:\\Programs\\Steam\\steamapps\\common\\DARK SOULS REMASTERED\\msg\\ENGLISH\\menu.msgbnd.dcx"]

DESC_DICT = {
    "diff": {rngopts.RandOptDifficulty.EASY: "* Perfectly fair. Items have an equal chance to be placed anywhere.\n", 
        rngopts.RandOptDifficulty.MEDIUM: "* Slightly biased. Desirable items are not placed in plain view.\n", 
        rngopts.RandOptDifficulty.HARD: "* Heavily biased. Desirable items are hidden, and are rarely in early areas.\n"},
    "key_diff": {rngopts.RandOptKeyDifficulty.LEAVE_ALONE: ("* Key items are placed in their usual locations.\n" + 
            "  For a player who wants random items without needing to hunt for keys.\n" + 
            "  Some key locations may contain additional items in some seeds.\n"),
        rngopts.RandOptKeyDifficulty.RANDOMIZE: ("* Key items are shuffled into the item pool and placed in random locations.\n" + 
            "  For a player who wishes to explore all of Lordran. Average run is ~10hrs.\n" + 
            "  Players will typically need to pick up many items in search of keys.\n"),
        rngopts.RandOptKeyDifficulty.RACE_MODE: (
            "* Key items are shuffled but can be placed only in certain locations.\n" + 
            "  Good for races / short runs. Average run is ~4hrs. See README for list of \n" + 
            "  locations to check. Read this list ahead of time to know where to check.\n"),
        rngopts.RandOptKeyDifficulty.SPEEDRUN_MODE: (
            "* Key items are shuffled but can be placed only in certain locations.\n" +
            "  May require skips and glitches to complete. SOFTLOCKING IS POSSIBLE.\n" +
            "  See README for list of locations to check. Read this list ahead of time.\n")},
    "souls_diff": {rngopts.RandOptSoulItemsDifficulty.SHUFFLE: "* Soul items are shuffled into the item pool like other items.\n",
        rngopts.RandOptSoulItemsDifficulty.CONSUMABLE: "* Lesser soul items are replaced with a random consumable before shuffling.\n",
        rngopts.RandOptSoulItemsDifficulty.TRANSPOSE:  "* Boss souls can be transposed to one of their boss items.\n"},
    "boss_soul_transpose_chance": {10: "* Boss souls have a 10% chance to be transposed.\n",
        25: "* Boss souls have a 25% chance to be transposed.\n",
        50: "* Boss souls have a 50% chance to be transposed.\n",
        75: "* Boss souls have a 75% chance to be transposed.\n"},
    "start_items": {rngopts.RandOptStartItemsDifficulty.SHIELD_AND_1H: ("* Player starts with random class-usable (L) shield & (R) weapon.\n" + 
            "  The weapon is usable one-handed with base stats.\n"),
        rngopts.RandOptStartItemsDifficulty.SHIELD_AND_2H: ("* Player starts with random class-usable (L) shield & (R) weapon.\n" + 
            "  The weapon may need to be two-handed to be usable with base stats.\n"),
        rngopts.RandOptStartItemsDifficulty.COMBINED_POOL_AND_2H: ("* Player starts with random class-usable (L) shield OR weapon & (R) weapon.\n" + 
            "  The weapon(s) may need to be two-handed to be usable with base stats.\n")},
    "fashion": {True: "* Armor sets ARE NOT kept together during shuffling.\n   Players will typically need to mix-and-match armor pieces.\n",
        False: "* Armor sets ARE kept together during shuffling.\n   Players will be able to find full sets of armor at once.\n"},
    "npc_armor": {True: "* NPCs wear randomly chosen armor instead of their normal sets.\n   If Fashion Souls is on, NPCs will also mix-and-match their armor.\n",
        False: "* NPCs will wear their normal sets of armor.\n   NPCs have their familiar look, weight class and defense stats.\n"},
    "use_lv": {rngopts.RandOptLordvesselLocation.RANDOMIZED: "* The Lordvessel IS included in the randomized keys.\n   Difficulty ranges from much easier (in Firelink) to harder (in TotG).\n",
        rngopts.RandOptLordvesselLocation.GWYNEVERE: "* The Lordvessel IS NOT included in the randomized keys.\n   Difficulty is standard. Lordvessel is given by Gwynevere in Anor Londo.\n",
        rngopts.RandOptLordvesselLocation.FIRELINK: "* The Lordvessel is at Firelink Shrine.\n   Difficulty is easy.\n"},
    "use_lord_souls": {True: "* The 4 Lord Souls ARE included in the randomized keys.\n   Difficulty ranges from much easier to much harder.\n", 
        False: "* The 4 Lord Souls ARE NOT included in the randomized keys.\n   Difficulty is standard. Lord Souls are dropped by their normal bosses.\n"},
    "ascend_weapons": {True: "* Normal weapons can be ascended with a random ember.\n",
        False: "* Normal weapons drop as expected.\n"},
    "ascend_weapons_chance": {5: "* Eager Smiths ascends normal weapons 5% of the time.\n",
        15: "* Eager Smiths ascends normal weapons 15% of the time.\n",
        25: "* Eager Smiths ascends normal weapons 25% of the time.\n"},
    "set_up_hints": {True: "* The dev messages visibile with Seek Guidance will have \n   hints automatically added in.\n", 
        False: "* There are no hints that are added to the seed via Seek Guidance.\n\n"},
    "keys_not_in_dlc": {True: "* Key items will NOT be in DLC (Painted World, Artorias of the Abyss).\n",
        False: "* Key items can be in DLC (Painted World, Artorias of the Abyss).\n"},
    "no_black_knight_weapons": {True: "* Black Knight weapons replaced by Titanite Chunks and Slabs.\n",
        False: "* Black Knight weapons are available for use.\n"},
    "npc_weapons": {True: "* NPCs wield randomly chosen weapons, shields, catalysts, and talismans instead of their normal equipment.\n",
        False: "* NPCs have their familiar loadouts.\n"},
    "starting_gifts": {True: "* Character starting gifts are randomized.\n   Ring gifts become other rings; non-ring gifts become non-ring gifts.\n",
        False: "* Character starting gifts are unchanged.\n"},
    "starting_stats": {True: "* Starting class stats are randomized from 8 to 15, except Deprived.\n   Each class keeps its vanilla stat total.\n",
        False: "* Starting class stats are unchanged.\n"}
}
DESC_ORDER = ["diff", "key_diff", "souls_diff", "boss_soul_transpose_chance", "use_lv", "start_items", "starting_gifts", "starting_stats", "fashion", "npc_armor", "npc_weapons", "use_lord_souls", "ascend_weapons", "ascend_weapons_chance", "set_up_hints", "keys_not_in_dlc", "no_black_knight_weapons"]

LIGHT_THEME = {
    "window_bg": "SystemButtonFace",
    "panel_bg": "SystemButtonFace",
    "text_bg": "SystemButtonFace",
    "entry_bg": "white",
    "entry_fg": "black",
    "fg": "black",
    "button_bg": "SystemButtonFace",
    "button_fg": "black",
    "combo_button_bg": "#d0d0d0",
    "combo_border": "#8a8a8a",
    "active_bg": "SystemButtonFace",
    "select_bg": "SystemHighlight",
    "select_fg": "SystemHighlightText",
    "disabled_fg": "gray50",
    "placeholder_fg": "grey",
    "deemph_fg": "grey",
    "emph_fg": "red2",
    "error_fg": "red",
    "success_fg": "green",
    "invalid_bg": "light salmon",
    "help_bg": "pale goldenrod",
}

DARK_THEME = {
    "window_bg": "#1b1b1f",
    "panel_bg": "#1b1b1f",
    "text_bg": "#232329",
    "entry_bg": "#111216",
    "entry_fg": "#e8e6df",
    "fg": "#e8e6df",
    "button_bg": "#303038",
    "button_fg": "#f1eee7",
    "combo_button_bg": "#3b3b45",
    "combo_border": "#5a5a66",
    "active_bg": "#3b3b45",
    "select_bg": "#5f6f94",
    "select_fg": "#ffffff",
    "disabled_fg": "#8a8790",
    "placeholder_fg": "#9b98a0",
    "deemph_fg": "#9b98a0",
    "emph_fg": "#ff8b7c",
    "error_fg": "#ff6b6b",
    "success_fg": "#79c47a",
    "invalid_bg": "#6b3732",
    "help_bg": "#77652e",
}


def resource_path(rel_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, rel_path)


class Placeholder_State(object):
    __slots__ = 'normal_color', 'normal_font', 'placeholder_text', 'placeholder_color', 'placeholder_font', 'with_placeholder'


class DescriptionState:
    NORMAL = "normal"
    DEEMPH = "deemph"
    EMPH = "emph"
    
    def __init__(self, desc_specifiers, text_area):
        self.text_area = text_area
        self.desc_specifiers = desc_specifiers
        
    def write_state_to_area(self):
        self.text_area.config(state="normal")
        self.text_area.delete(1.0, "end")
        
        for desc_part in DESC_ORDER:
            (desc_part_value, desc_part_format) = self.desc_specifiers[desc_part]
            text_part = DESC_DICT[desc_part][desc_part_value]
            self.text_area.insert("end", text_part, desc_part_format)
        theme = getattr(self.text_area, "theme_colors", LIGHT_THEME)
        self.text_area.tag_config(DescriptionState.NORMAL, foreground=theme["fg"])
        self.text_area.tag_config(DescriptionState.DEEMPH, foreground=theme["deemph_fg"])
        self.text_area.tag_config(DescriptionState.EMPH, foreground=theme["emph_fg"])
        self.text_area.config(state="disabled")

class MainGUI:
    def __init__(self):
        init_options = ini_parser.get_values_from_ini(INI_FILE, section="DEFAULT")     #load ini file 
        self.seed_rng = random.Random()
        self.has_hovered_desc = False
        self.root = tk.Tk()
        self.style = ttk.Style()
        self.dark_mode = tk.BooleanVar()
        self.dark_mode.set(init_options.getboolean("dark_mode", fallback=False))
        self.root.title("Dark Souls Item Randomizer v" + VERSION_NUM)
        self.root.resizable(False, False)
        img = tk.PhotoImage(file=resource_path('favicon.gif'))
        self.root.call('wm', 'iconphoto', self.root._w, img)
    
        tk.Label(self.root, text="Seed:").grid(row=0, column=0, sticky='E', padx=2)
        self.seed_string = tk.StringVar()
        self.seed_string.set("")
        self.seed_string.trace('w', lambda name, index, mode: self.seed_changed())
        self.seed_entry = tk.Entry(self.root, font="TkFixedFont", textvariable=self.seed_string, width=70)
        self.entry_state = self.add_placeholder_to(self.seed_entry, 'Type a seed (or leave blank for a random seed)')
        self.seed_entry.grid(row=0, column=1, columnspan=2, ipady=2, ipadx=1, padx=2, sticky='EW')
        self.reroll_seed = tk.BooleanVar()
        self.reroll_seed.set(init_options.getboolean("reroll_seed_each_run", fallback=False))
        self.top_button_frame = tk.Frame(self.root)
        self.top_button_frame.grid(row=0, column=3, padx=2, sticky='EW')
        self.top_button_frame.columnconfigure(1, weight=1)
        self.reroll_seed_check = tk.Checkbutton(self.top_button_frame, text="Reroll seed each run",
         variable=self.reroll_seed, onvalue=True, offvalue=False, padx=2)
        self.reroll_seed_check.grid(row=0, column=0, sticky='W')
        self.dark_mode_check = tk.Checkbutton(self.top_button_frame, text="Dark mode",
         variable=self.dark_mode, onvalue=True, offvalue=False, padx=2, command=self.apply_theme)
        self.dark_mode_check.grid(row=0, column=2, padx=2, sticky='E')
        self.sellout_button = tk.Button(self.top_button_frame, text="?", bg="pale goldenrod",
         padx=2, pady=2, command=self.lift_sellout_area)
        self.sellout_button.grid(row=0, column=3, padx=2, sticky='E')
        
        tk.Label(self.root, text="Dark Souls Game Version:").grid(row=1, column=0, columnspan=2, sticky='W', padx=2, ipady=1)
        self.game_version = tk.StringVar()
        self.game_version.trace('w', lambda name, index, mode: self.update())
        self.game_version_menu = ttk.Combobox(self.root, textvariable=self.game_version, state="readonly", 
            values=[rngopts.RandOptGameVersion.PTDE, rngopts.RandOptGameVersion.REMASTERED],
            style="GameVersion.TCombobox")
        self.style.map('Highlight.GameVersion.TCombobox', fieldbackground=[('readonly', self.current_theme()["invalid_bg"])])
        self.style.map('Error.GameVersion.TCombobox', foreground=[('readonly', self.current_theme()["error_fg"])])
        # Clear the highlighting of the combobox after user interaction,
        #  since it auto-highlights for some reason.
        self.game_version_menu.bind("<<ComboboxSelected>>", lambda event: self.combobox_selected(event, self.update_game_version))
        self.game_version_menu.config(width=30)
        self.game_version_menu.grid(row=1, column=2, sticky='EW', padx=2)
        
        self.msg_area = tk.Text(self.root, width=76, height=27,
                                state="disabled", background=self.root.cget('background'), wrap="word")
        self.msg_area.grid(row=2, column=0, columnspan=3, rowspan=14, padx=2, pady=2, sticky='NS')
        self.msg_quit_button = tk.Button(self.root, text="Quit", command=self.quit_button)
        self.msg_quit_button.grid(row=9, column=1, columnspan=2, rowspan=2)
        self.msg_continue_button = tk.Button(self.root, text="Continue", command=self.continue_button)
        self.msg_continue_button.grid(row=7, column=1, columnspan=2, rowspan=2)
        self.back_button = tk.Button(self.root, text="Back", command=self.back_button)
        self.back_button.grid(row=7, column=1, columnspan=2, rowspan=2)
        self.desc_area = tk.Text(self.root, width=76, height=27, state="disabled", background=self.root.cget('background'), wrap="word")
        self.desc_area.grid(row=2, column=0, columnspan=3, rowspan=14, padx=2, pady=2)
        
        # Settings panel: two independently stacked columns, so neither stretches
        # to match the grid rows of the description text box.
        self.options_frame = tk.Frame(self.root)
        self.options_frame.grid(row=2, column=3, rowspan=10, sticky='NW', padx=2)
        self.options_left = tk.Frame(self.options_frame)
        self.options_left.grid(row=0, column=0, sticky='NW')
        self.options_right = tk.Frame(self.options_frame)
        self.options_right.grid(row=0, column=1, sticky='NW', padx=(12, 0))

        self.diff_frame = tk.LabelFrame(self.options_left, text="Difficulty:", bd=0)
        self.diff_frame.grid(row=0, column=0, sticky='W', pady=2)
        #--
        self.diff = tk.IntVar()
        self.diff_as_string = tk.StringVar()
        self.diff.set(ini_parser.get_option_value(init_options, "difficulty"))
        self.diff_as_string.set(rngopts.RandOptDifficulty.as_string(self.diff.get()))
        self.diff.trace('w', lambda name, index, mode: self.update())
        self.gui_diff = ttk.Combobox(self.diff_frame, 
                                            values=rngopts.RandOptDifficulty.as_strings(),
                                            textvariable=self.diff_as_string,
                                            width=13,
                                            state="readonly")
        self.gui_diff.bind("<<ComboboxSelected>>", lambda event: self.combobox_selected(event,
            lambda: self.diff.set(rngopts.RandOptDifficulty.from_string(self.diff_as_string.get()))))
        self.gui_diff.grid(row=0, column=0, sticky='W')
        self.setup_hover_events(self.gui_diff, {"diff": None}, no_emph = True)
       
        
        self.key_diff_frame = tk.LabelFrame(self.options_left, text="Key Placement:", bd=0)
        self.key_diff_frame.grid(row=1, column=0, sticky='W', pady=2)
        #--
        self.key_diff = tk.IntVar()
        self.key_diff_as_string = tk.StringVar()
        self.key_diff.set(ini_parser.get_option_value(init_options, "key_placement"))
        self.key_diff_as_string.set(rngopts.RandOptKeyDifficulty.as_string(self.key_diff.get()))
        self.key_diff.trace('w', lambda name, index, mode: self.update())
        self.gui_key_diff = ttk.Combobox(self.key_diff_frame, 
                                            values=rngopts.RandOptKeyDifficulty.as_strings(),
                                            textvariable=self.key_diff_as_string,
                                            width=13,
                                            state="readonly")
        self.gui_key_diff.bind("<<ComboboxSelected>>", lambda event: self.combobox_selected(event,
            lambda: self.key_diff.set(rngopts.RandOptKeyDifficulty.from_string(self.key_diff_as_string.get()))))
        self.gui_key_diff.grid(row=0, column=0, sticky='W')
        self.setup_hover_events(self.gui_key_diff, {"key_diff": None}, no_emph = True)

        self.soul_frame = tk.LabelFrame(self.options_left, text="Soul Items:", bd=0)
        self.soul_frame.grid(row=2, column=0, sticky='W', pady=2)
        #--
        self.soul_diff = tk.IntVar()
        self.soul_diff_as_string = tk.StringVar()
        self.soul_diff.set(ini_parser.get_option_value(init_options, "soul_items_diff"))
        self.soul_diff_as_string.set(rngopts.RandOptSoulItemsDifficulty.as_string(self.soul_diff.get()))
        self.soul_diff.trace('w', lambda name, index, mode: self.update())
        self.gui_soul_diff = ttk.Combobox(self.soul_frame, 
                                            values=rngopts.RandOptSoulItemsDifficulty.as_strings(),
                                            textvariable=self.soul_diff_as_string,
                                            width=13,
                                            state="readonly")
        self.gui_soul_diff.bind("<<ComboboxSelected>>", lambda event: self.combobox_selected(event,
            lambda: self.soul_diff.set(rngopts.RandOptSoulItemsDifficulty.from_string(self.soul_diff_as_string.get()))))
        self.gui_soul_diff.grid(row=0, column=0, sticky='W')
        self.setup_hover_events(self.gui_soul_diff, {"souls_diff": None}, no_emph = True)
        self.boss_soul_transpose_chance = tk.IntVar()
        self.boss_soul_transpose_chance_as_string = tk.StringVar()
        self.boss_soul_transpose_chance.set(rngopts.RandOptBossSoulTransposeChance.verify(init_options.getint("boss_soul_transpose_chance", fallback=rngopts.RandOptBossSoulTransposeChance.CHANCE_75)))
        self.boss_soul_transpose_chance_as_string.set(rngopts.RandOptBossSoulTransposeChance.as_string(self.boss_soul_transpose_chance.get()))
        self.boss_soul_transpose_chance.trace('w', lambda name, index, mode: self.update())
        self.gui_boss_soul_transpose_chance = ttk.Combobox(self.soul_frame,
                                            values=rngopts.RandOptBossSoulTransposeChance.as_strings(),
                                            textvariable=self.boss_soul_transpose_chance_as_string,
                                            width=13,
                                            state="readonly")
        self.gui_boss_soul_transpose_chance.bind("<<ComboboxSelected>>", lambda event: self.combobox_selected(event,
            lambda: self.boss_soul_transpose_chance.set(rngopts.RandOptBossSoulTransposeChance.from_string(self.boss_soul_transpose_chance_as_string.get()))))
        self.gui_boss_soul_transpose_chance.grid(row=1, column=0, sticky='W')
        self.setup_hover_events(self.gui_boss_soul_transpose_chance, {"boss_soul_transpose_chance": None}, no_emph = True)

        self.use_lordvessel_frame = tk.LabelFrame(self.options_left, text="Lordvessel:", bd=0)
        self.use_lordvessel_frame.grid(row=3, column=0, sticky='W', pady=2)
        #--
        self.use_lordvessel = tk.StringVar()
        self.use_lordvessel.set(rngopts.RandOptLordvesselLocation.verify(ini_parser.get_option_value(init_options, "use_lordvessel")))
        self.use_lordvessel.trace('w', lambda name, index, mode: self.update())
        self.gui_lordvessel = ttk.Combobox(self.use_lordvessel_frame, 
                                            textvariable=self.use_lordvessel,
                                            values=rngopts.RandOptLordvesselLocation.as_strings(),
                                            width=13,
                                            state="readonly")
        self.gui_lordvessel.grid(row=0, column=0, sticky='W')
        self.gui_lordvessel.bind("<<ComboboxSelected>>", self.combobox_selected)
        self.setup_hover_events(self.gui_lordvessel, {"use_lv": None}, no_emph = True)

        self.start_items_frame = tk.LabelFrame(self.options_right, text="Starting Items:", bd=0)  #wxy
        self.start_items_frame.grid(row=0, column=0, sticky='W', pady=2)
        #--
        self.start_items_diff = tk.IntVar()
        self.start_items_diff_as_string = tk.StringVar()
        self.start_items_diff.set(ini_parser.get_option_value(init_options, "start_items_diff"))
        self.start_items_diff_as_string.set(rngopts.RandOptStartItemsDifficulty.as_string(self.start_items_diff.get()))
        self.start_items_diff.trace('w', lambda name, index, mode: self.update())
        self.gui_start_items_diff = ttk.Combobox(self.start_items_frame, 
                                            values=rngopts.RandOptStartItemsDifficulty.as_strings(),
                                            textvariable=self.start_items_diff_as_string,
                                            width=25,
                                            state="readonly")
        self.gui_start_items_diff.bind("<<ComboboxSelected>>", lambda event: self.combobox_selected(event,
            lambda: self.start_items_diff.set(rngopts.RandOptStartItemsDifficulty.from_string(self.start_items_diff_as_string.get()))))
        self.gui_start_items_diff.grid(row=0, column=0, sticky='W')
        self.setup_hover_events(self.gui_start_items_diff, {"start_items": None}, no_emph = True)
        
        self.misc_flags_frame = tk.LabelFrame(self.options_right, text="Other Settings:", bd=0)  #wxy
        self.misc_flags_frame.grid(row=1, column=0, sticky='W', pady=2)
        #--
        self.randomize_starting_gifts = tk.BooleanVar()
        self.randomize_starting_gifts.set(init_options.getboolean("randomize_starting_gifts", fallback=False))
        self.randomize_starting_gifts.trace('w', lambda name, index, mode: self.update())
        self.starting_gifts_check = tk.Checkbutton(self.misc_flags_frame, text="Randomize Starting Gifts",
         variable=self.randomize_starting_gifts, onvalue=True, offvalue=False)
        self.starting_gifts_check.grid(row=0, column=0, columnspan=2, sticky='W')
        self.setup_hover_events(self.starting_gifts_check, {"starting_gifts": None}, no_emph=True)

        self.randomize_starting_stats = tk.BooleanVar()
        self.randomize_starting_stats.set(init_options.getboolean("randomize_starting_stats", fallback=False))
        self.randomize_starting_stats.trace('w', lambda name, index, mode: self.update())
        self.starting_stats_check = tk.Checkbutton(self.misc_flags_frame, text="Randomize Starting Stats",
         variable=self.randomize_starting_stats, onvalue=True, offvalue=False,
         command=self.randomize_starting_stats_toggled)
        self.starting_stats_check.grid(row=1, column=0, columnspan=2, sticky='W')
        self.setup_hover_events(self.starting_stats_check, {"starting_stats": None}, no_emph=True)
        self.starting_stats_check.configure(command=self.randomize_starting_stats_check_clicked)

        self.fashion_bool = tk.BooleanVar()
        self.fashion_bool.set(ini_parser.get_option_value(init_options, "fashion_souls"))
        self.fashion_bool.trace('w', lambda name, index, mode: self.update())
        self.fashion_check = tk.Checkbutton(self.misc_flags_frame, text="Fashion Souls", 
         variable=self.fashion_bool, onvalue=True, offvalue=False, padx=2)
        self.fashion_check.grid(row=2, column=0, sticky='W')
        self.setup_hover_events(self.fashion_check, {"fashion": None}, no_emph=True)
        
        self.npc_armor_bool = tk.BooleanVar()
        self.npc_armor_bool.set(ini_parser.get_option_value(init_options, "randomize_npc_armor"))
        self.npc_armor_bool.trace('w', lambda name, index, mode: self.update())
        self.npc_armor_check = tk.Checkbutton(self.misc_flags_frame, text="Laundromat Mixup", 
         variable=self.npc_armor_bool, onvalue=True, offvalue=False, padx=2)
        self.npc_armor_check.grid(row=3, column=0, sticky='W')
        self.setup_hover_events(self.npc_armor_check, {"npc_armor": None}, no_emph=True)
       
        self.use_lord_souls = tk.BooleanVar()
        self.use_lord_souls.set(ini_parser.get_option_value(init_options, "use_lord_souls"))
        self.use_lord_souls.trace('w', lambda name, index, mode: self.update())
        self.lord_soul_check = tk.Checkbutton(self.misc_flags_frame, text="Senile Primordial Serpents", 
         variable=self.use_lord_souls, onvalue=True, offvalue=False, padx=2)
        self.lord_soul_check.grid(row=5, column=0, sticky='W')
        self.setup_hover_events(self.lord_soul_check, {"use_lord_souls": None}, no_emph = True)

        self.ascend_weapons_bool = tk.BooleanVar()
        self.ascend_weapons_bool.set(ini_parser.get_option_value(init_options, "ascend_weapons"))
        self.ascend_weapons_bool.trace('w', lambda name, index, mode: self.update())
        self.ascend_weapons_check = tk.Checkbutton(self.misc_flags_frame, text="Eager Smiths", 
         variable=self.ascend_weapons_bool, onvalue=True, offvalue=False, padx=2)
        self.ascend_weapons_check.grid(row=6, column=0, sticky='W')
        self.setup_hover_events(self.ascend_weapons_check, {"ascend_weapons": None}, no_emph = True)
        self.ascend_weapons_chance = tk.IntVar()
        self.ascend_weapons_chance_as_string = tk.StringVar()
        self.ascend_weapons_chance.set(rngopts.RandOptAscendWeaponsChance.verify(init_options.getint("ascend_weapons_chance", fallback=rngopts.RandOptAscendWeaponsChance.CHANCE_25)))
        self.ascend_weapons_chance_as_string.set(rngopts.RandOptAscendWeaponsChance.as_string(self.ascend_weapons_chance.get()))
        self.ascend_weapons_chance.trace('w', lambda name, index, mode: self.update())
        self.gui_ascend_weapons_chance = ttk.Combobox(self.misc_flags_frame,
                                            values=rngopts.RandOptAscendWeaponsChance.as_strings(),
                                            textvariable=self.ascend_weapons_chance_as_string,
                                            width=5,
                                            state="readonly")
        self.gui_ascend_weapons_chance.bind("<<ComboboxSelected>>", lambda event: self.combobox_selected(event,
            lambda: self.ascend_weapons_chance.set(rngopts.RandOptAscendWeaponsChance.from_string(self.ascend_weapons_chance_as_string.get()))))
        self.gui_ascend_weapons_chance.grid(row=6, column=1, sticky='W')
        self.setup_hover_events(self.gui_ascend_weapons_chance, {"ascend_weapons_chance": None}, no_emph = True)

        self.set_up_hints = tk.BooleanVar()
        self.set_up_hints.set(ini_parser.get_option_value(init_options, "set_up_hints"))
        self.set_up_hints.trace('w', lambda name, index, mode: self.update())
        self.hint_check = tk.Checkbutton(self.misc_flags_frame, text="Seek Guidance Hints", 
         variable=self.set_up_hints, onvalue=True, offvalue=False, padx=2)
        self.hint_check.grid(row=7, column=0, sticky='W')
        self.setup_hover_events(self.hint_check, {"set_up_hints": None}, no_emph = True)

        self.keys_not_in_dlc = tk.BooleanVar()
        self.keys_not_in_dlc.set(ini_parser.get_option_value(init_options, "keys_not_in_dlc"))
        self.keys_not_in_dlc.trace('w', lambda name, index, mode: self.update())
        self.keys_not_in_dlc_check = tk.Checkbutton(self.misc_flags_frame, text="No DLC", 
         variable=self.keys_not_in_dlc, onvalue=True, offvalue=False)   #, padx=2
        self.keys_not_in_dlc_check.grid(row=8, column=0, sticky='W')
        self.setup_hover_events(self.keys_not_in_dlc_check, {"keys_not_in_dlc": None}, no_emph = True)

        self.no_black_knight_weapons = tk.BooleanVar()
        self.no_black_knight_weapons.set(ini_parser.get_option_value(init_options, "no_black_knight_weapons"))
        self.no_black_knight_weapons.trace('w', lambda name, index, mode: self.update())
        self.no_black_knight_weapons_gui = tk.Checkbutton(self.misc_flags_frame, text="No Black Knight Weapons", 
         variable=self.no_black_knight_weapons, onvalue=True, offvalue=False)   #, padx=2
        self.no_black_knight_weapons_gui.grid(row=9, column=0, sticky='W')
        self.setup_hover_events(self.no_black_knight_weapons_gui, {"no_black_knight_weapons": None}, no_emph = True)

        self.npc_weapons_bool = tk.BooleanVar()
        self.npc_weapons_bool.set(init_options.getboolean("randomize_npc_weapons", fallback=False))
        self.npc_weapons_bool.trace('w', lambda name, index, mode: self.update())
        self.npc_weapons_check = tk.Checkbutton(self.misc_flags_frame, text="NPC Weapon Mixup",
         variable=self.npc_weapons_bool, onvalue=True, offvalue=False)
        self.npc_weapons_check.grid(row=4, column=0, sticky='W')
        self.setup_hover_events(self.npc_weapons_check, {"npc_weapons": None}, no_emph=True)

        self.actions_frame = tk.Frame(self.root)
        self.actions_frame.grid(row=12, column=3, rowspan=4, sticky='SEW', padx=2, pady=2)
        for col in range(3):
            self.actions_frame.columnconfigure(col, weight=1, uniform="actions")

        self.export_button = tk.Button(self.actions_frame, text="Scramble Items &\nExport to GameParam",
         padx=10, pady=10, command=self.export_to_gameparam)
        self.export_button.grid(row=0, column=0, columnspan=3, padx=2, sticky='EW')

        self.cheat_button = tk.Button(self.actions_frame, text="Write Seed Cheatsheet", command=self.export_seed_info)
        self.cheat_button.grid(row=1, column=0, columnspan=3, sticky='EW', padx=2, pady=(4, 0))

        self.normalize_button = tk.Button(self.actions_frame, text="Revert to vanilla",
         padx=2, pady=2, command=self.normalize_game)
        self.normalize_button.grid(row=2, column=0, padx=2, pady=(4, 0), sticky='EW')
        self.delete_saves_button = tk.Button(self.actions_frame, text="Delete Saves",
         padx=2, pady=2, command=self.delete_save_files)
        self.delete_saves_button.grid(row=2, column=1, padx=2, pady=(4, 0), sticky='EW')
        self.save_options_button = tk.Button(self.actions_frame, text="Save Defaults",
         padx=2, pady=2, command=self.save_current_options)
        self.save_options_button.grid(row=2, column=2, padx=2, pady=(4, 0), sticky='EW')

        # Settings sync popup menu
        self.popup_menu = tk.Menu(self.root, tearoff=0)
        self.popup_menu.add_command(label="Copy settings sync", command=self.settings_string_copy)
        self.popup_menu.add_command(label="Paste settings sync", command=self.settings_string_paste)
        self.root.bind("<Button-3>", self.popup_menu_show)

        self.settings_string_io = SettingsStringIO(VERSION_NUM, COMPATIBLE_VERSIONS, [
            SettingsVariable(name='seed', variable=self.seed_string, on_update=lambda: self.seed_entry.disable_placeholder()),
            # SettingsVariable(name='gv', variable=self.game_version, options=(rngopts.RandOptGameVersion.PTDE, rngopts.RandOptGameVersion.REMASTERED)),
            SettingsVariable(name='diff', variable=self.diff, options=DESC_DICT['diff'].keys()),
            SettingsVariable(name='kd', variable=self.key_diff, options=DESC_DICT['key_diff'].keys()),
            SettingsVariable(name='sd', variable=self.soul_diff, options=DESC_DICT['souls_diff'].keys()),
            SettingsVariable(name='bstc', variable=self.boss_soul_transpose_chance, options=DESC_DICT['boss_soul_transpose_chance'].keys()),
            SettingsVariable(name='id', variable=self.start_items_diff, options=DESC_DICT['start_items'].keys()),
            SettingsVariable(name='fs', variable=self.fashion_bool, options=DESC_DICT['fashion'].keys()),
            SettingsVariable(name='npc', variable=self.npc_armor_bool, options=DESC_DICT['npc_armor'].keys()),
            SettingsVariable(name='lv', variable=self.use_lordvessel, options=DESC_DICT['use_lv'].keys()),
            SettingsVariable(name='ls', variable=self.use_lord_souls, options=DESC_DICT['use_lord_souls'].keys()),
            SettingsVariable(name='nodlc', variable=self.keys_not_in_dlc, options=DESC_DICT['keys_not_in_dlc'].keys()),
            SettingsVariable(name='aw', variable=self.ascend_weapons_bool, options=DESC_DICT['ascend_weapons'].keys()),
            SettingsVariable(name='awc', variable=self.ascend_weapons_chance, options=DESC_DICT['ascend_weapons_chance'].keys()),
            SettingsVariable(name='hints', variable=self.set_up_hints, options=DESC_DICT['set_up_hints'].keys()),
            SettingsVariable(name='nobkw', variable=self.no_black_knight_weapons, options=DESC_DICT['no_black_knight_weapons'].keys()),
            SettingsVariable(name='npcw', variable=self.npc_weapons_bool, options=DESC_DICT['npc_weapons'].keys()),
            SettingsVariable(name='gifts', variable=self.randomize_starting_gifts, options=DESC_DICT['starting_gifts'].keys()),
            SettingsVariable(name='stats', variable=self.randomize_starting_stats, options=DESC_DICT['starting_stats'].keys()),
        ], call_after_update=self.update_desc)

        self.apply_theme()
        self.update_desc()
        self.detect_game_version()
        self.check_for_new_version()
        self.update()
        
    def update_game_version(self):
        self.game_version_menu.selection_clear()
        if self.game_version.get() in [rngopts.RandOptGameVersion.PTDE, rngopts.RandOptGameVersion.REMASTERED]:
            self.game_version_menu.configure(style="GameVersion.TCombobox")

    def combobox_selected(self, event, callback=None):
        if callback is not None:
            callback()
        event.widget.selection_clear()
        self.root.focus_set()

    def randomize_starting_stats_toggled(self):
        if (self.randomize_starting_stats.get() and
         self.game_version.get() == rngopts.RandOptGameVersion.REMASTERED):
            tkMB.showwarning(
                "Randomize Starting Stats",
                "Reverting back to the vanilla game and going online without first deleting "
                "characters with modified stats from the randomizer can cause you to get banned "
                "from the game.\n\nMake sure to delete any characters with randomized stats before "
                "reverting to vanilla and going online."
                "\n\nYou probably should also disable any cloud saving."
            )

    def randomize_starting_stats_check_clicked(self):
        self.randomize_starting_stats_toggled()
        self.update_desc_for_hover({"starting_stats": None}, no_emph=True)

    def current_theme(self):
        return DARK_THEME if self.dark_mode.get() else LIGHT_THEME

    def apply_theme(self):
        theme = self.current_theme()
        self.root.configure(bg=theme["window_bg"])
        self.root.option_add("*TCombobox*Listbox.background", theme["entry_bg"])
        self.root.option_add("*TCombobox*Listbox.foreground", theme["entry_fg"])
        self.root.option_add("*TCombobox*Listbox.selectBackground", theme["select_bg"])
        self.root.option_add("*TCombobox*Listbox.selectForeground", theme["select_fg"])
        self.configure_ttk_styles(theme)
        self.apply_theme_to_widget(self.root, theme)
        if hasattr(self, "popup_menu"):
            self.apply_theme_to_widget(self.popup_menu, theme)
        if hasattr(self, "sellout_button"):
            self.sellout_button.configure(bg=theme["help_bg"], fg=theme["button_fg"],
                activebackground=theme["active_bg"], activeforeground=theme["button_fg"])
        self.configure_message_tags()
        self.configure_seed_entry_colors()
        if hasattr(self, "desc_area"):
            self.update_desc(respect_current_hover=False)

    def configure_ttk_styles(self, theme):
        try:
            self.style.theme_use("clam")
        except tk.TclError:
            pass

        combo_settings = {
            "fieldbackground": theme["entry_bg"],
            "background": theme["combo_button_bg"],
            "foreground": theme["entry_fg"],
            "selectbackground": theme["select_bg"],
            "selectforeground": theme["select_fg"],
            "arrowcolor": theme["fg"],
            "bordercolor": theme["combo_border"],
            "lightcolor": theme["combo_border"],
            "darkcolor": theme["combo_border"],
        }
        for style_name in ("TCombobox", "GameVersion.TCombobox"):
            self.style.configure(style_name, **combo_settings)
            self.style.map(style_name,
                fieldbackground=[("readonly", theme["entry_bg"]), ("disabled", theme["panel_bg"])],
                foreground=[("readonly", theme["entry_fg"]), ("disabled", theme["disabled_fg"])],
                background=[("readonly", theme["combo_button_bg"]), ("disabled", theme["button_bg"])])

        self.style.configure("Highlight.GameVersion.TCombobox", **combo_settings)
        self.style.map("Highlight.GameVersion.TCombobox",
            fieldbackground=[("readonly", theme["invalid_bg"])],
            foreground=[("readonly", theme["entry_fg"])])
        self.style.configure("Error.GameVersion.TCombobox", **combo_settings)
        self.style.map("Error.GameVersion.TCombobox",
            fieldbackground=[("readonly", theme["entry_bg"])],
            foreground=[("readonly", theme["error_fg"])])

    def apply_theme_to_widget(self, widget, theme):
        widget.theme_colors = theme
        if isinstance(widget, ttk.Widget):
            for child in widget.winfo_children():
                self.apply_theme_to_widget(child, theme)
            return

        if isinstance(widget, (tk.Frame, tk.LabelFrame)):
            widget.configure(bg=theme["panel_bg"])
            if isinstance(widget, tk.LabelFrame):
                widget.configure(fg=theme["fg"])
        elif isinstance(widget, tk.Label):
            widget.configure(bg=theme["panel_bg"], fg=theme["fg"])
        elif isinstance(widget, tk.Checkbutton):
            widget.configure(bg=theme["panel_bg"], fg=theme["fg"],
                activebackground=theme["active_bg"], activeforeground=theme["fg"],
                selectcolor=theme["entry_bg"], disabledforeground=theme["disabled_fg"])
        elif isinstance(widget, tk.Button):
            widget.configure(bg=theme["button_bg"], fg=theme["button_fg"],
                activebackground=theme["active_bg"], activeforeground=theme["button_fg"],
                disabledforeground=theme["disabled_fg"])
        elif isinstance(widget, tk.Entry):
            widget.configure(bg=theme["entry_bg"], fg=theme["entry_fg"],
                insertbackground=theme["entry_fg"], selectbackground=theme["select_bg"],
                selectforeground=theme["select_fg"])
        elif isinstance(widget, tk.Text):
            widget.configure(bg=theme["text_bg"], fg=theme["fg"],
                insertbackground=theme["fg"], selectbackground=theme["select_bg"],
                selectforeground=theme["select_fg"])
        elif isinstance(widget, tk.Menu):
            widget.configure(bg=theme["button_bg"], fg=theme["button_fg"],
                activebackground=theme["active_bg"], activeforeground=theme["button_fg"])

        for child in widget.winfo_children():
            self.apply_theme_to_widget(child, theme)

    def configure_message_tags(self):
        theme = self.current_theme()
        for text_area in (getattr(self, "msg_area", None), getattr(self, "desc_area", None)):
            if text_area is not None:
                text_area.theme_colors = theme
        if hasattr(self, "msg_area"):
            self.msg_area.tag_config("error_red", foreground=theme["error_fg"])
            self.msg_area.tag_config("yay", foreground=theme["success_fg"])

    def configure_seed_entry_colors(self):
        if not hasattr(self, "seed_entry"):
            return
        theme = self.current_theme()
        self.entry_state.normal_color = theme["entry_fg"]
        self.entry_state.placeholder_color = theme["placeholder_fg"]
        if self.entry_state.with_placeholder:
            self.seed_entry.config(fg=self.entry_state.placeholder_color,
                font=self.entry_state.placeholder_font)
        else:
            self.seed_entry.config(fg=self.entry_state.normal_color,
                font=self.entry_state.normal_font)

    def update_starting_gift_menu_messages(self, enmenu_content_list, randomized_gifts):
        updated_count = 0
        for index, (file_id, filepath, filedata) in enumerate(enmenu_content_list):
            fmg_data = FMGHandler(FMGHandler.load_from_file_content(filedata))
            fmg_update_count = gift_s.update_gift_messages(fmg_data.messages, randomized_gifts)
            if fmg_update_count > 0:
                enmenu_content_list[index] = (file_id, filepath, fmg_data.export_as_binary())
                updated_count += fmg_update_count
        return updated_count
        
    def detect_game_version(self):
        for filepath in DS1R_GAMEPARAM_PATH_LIST:
            normed_path = os.path.normpath(os.path.join(os.getcwd(), filepath))
            if os.path.isfile(normed_path):
                self.game_version.set(rngopts.RandOptGameVersion.REMASTERED)
                return
        for filepath in PTDE_GAMEPARAM_PATH_LIST:
            normed_path = os.path.normpath(os.path.join(os.getcwd(), filepath))
            if os.path.isfile(normed_path):
                self.game_version.set(rngopts.RandOptGameVersion.PTDE)
                return
        self.game_version.set("No GameParam detected! Exporting has been disabled.")
        self.game_version_menu.configure(style="Error.GameVersion.TCombobox")
        self.export_button.config(state="disabled")
        
    def quit_button(self):
        self.root.destroy()
        
    def continue_button(self):
        self.msg_quit_button.lower()
        self.msg_continue_button.lower()
        self.msg_area.lower()
        
    def back_button(self):
        self.msg_quit_button.lower()
        self.back_button.lower()
        self.msg_area.lower()
        
    def lift_msg_area(self):
        self.msg_area.lift()
        self.msg_continue_button.lift()
        self.msg_quit_button.lift()
        
    def lift_sellout_area(self):
        self.msg_continue_button.lower()
        self.msg_area.config(state="normal")
        self.msg_area.delete(1.0, "end")
        self.msg_area.insert("end", "\n\n")
        self.msg_area.insert("end", "\tDark Soul Item Randomizer, developers:\n\n")
        self.msg_area.insert("end", "\t\thotpocketremix\n")
        self.msg_area.insert("end", "\t\tcaerulius\n")
        self.msg_area.insert("end", "\t\tforstycup\n")
        self.msg_area.insert("end", "\t\tAbscondWithAPie\n")
        self.msg_area.insert("end", "\t\tAzetinnitezA\n")
        self.msg_area.insert("end", "\t\teaglevis\n")
        self.msg_area.insert("end", "\t\tda66en\n")
        self.msg_area.insert("end", "\t\tPrimogenitor33\n")
        self.msg_area.insert("end", "\t\tFIPO\n")
        self.msg_area.config(state="disabled")
        self.msg_area.lift()
        self.back_button.lift()

    def normalize_game(self):
        if self.game_version.get() == rngopts.RandOptGameVersion.PTDE:
            paths_to_search = PTDE_GAMEPARAM_PATH_LIST
        elif self.game_version.get() == rngopts.RandOptGameVersion.REMASTERED:
            paths_to_search = DS1R_GAMEPARAM_PATH_LIST
        else:
            self.show_error("Critical error!")
            return

        gameparam_filepath = ""
        gameparambak_filepath = ""
        for filepath in paths_to_search:
            normed_path = os.path.normpath(os.path.join(os.getcwd(), filepath))
            if os.path.isfile(normed_path):
                gameparam_filepath = normed_path
                gameparambak_filepath = normed_path + ".bak"
                break

        #if gameparam_filepath == "" or not os.path.isfile(gameparam_filepath):
        #    self.show_error("GameParam.parambnd is missing or cannot be opened. File could not be located.")
        #    return

        if gameparambak_filepath == "" or not os.path.isfile(gameparambak_filepath):
            self.show_error("GameParam.parambnd.bak is missing or cannot be opened.  Game could be vanilla already.")
            return

        os.remove(gameparam_filepath)
        shutil.copy2(gameparambak_filepath, gameparam_filepath)

        if self.game_version.get() == rngopts.RandOptGameVersion.PTDE:
            paths_to_search = PTDE_ENGMENU_PATH_LIST
        elif self.game_version.get() == rngopts.RandOptGameVersion.REMASTERED:
            paths_to_search = DS1R_ENGMENU_PATH_LIST
        else:
            self.show_error("Critical error!")
            return
        
        enmenu_filepath = ""
        enmenubak_filepath = ""
        for filepath in paths_to_search:
            normed_path = os.path.normpath(os.path.join(os.getcwd(), filepath))
            if os.path.isfile(normed_path):
                enmenu_filepath = normed_path
                enmenubak_filepath = normed_path + ".bak"
                break

        #if enmenu_filepath == "" or not os.path.isfile(enmenu_filepath):
        #    self.show_error("ENGLISH/menu.msgbnd is missing or cannot be opened. File could not be located.")
        #    return

        if enmenubak_filepath == "" or not os.path.isfile(enmenubak_filepath):
            self.show_error("ENGLISH/menu.msgbnd.bak is missing or cannot be opened.  Game could be vanilla already.")
            return

        os.remove(enmenu_filepath)
        shutil.copy2(enmenubak_filepath, enmenu_filepath)

        self.show_success("Game has been reverted to vanilla Dark Souls.")

    def get_save_file_paths(self):
        if self.game_version.get() == rngopts.RandOptGameVersion.PTDE:
            save_folder_name = PTDE_SAVE_FOLDER_NAME
        elif self.game_version.get() == rngopts.RandOptGameVersion.REMASTERED:
            save_folder_name = DS1R_SAVE_FOLDER_NAME
        else:
            return None

        save_paths = {}
        for documents_dir in get_documents_dirs():
            save_dir = os.path.join(documents_dir, "NBGI", save_folder_name)
            if not os.path.isdir(save_dir):
                continue
            # DSR keeps saves in a per-account subfolder, PTDE directly in the folder.
            for (dirpath, dirnames, filenames) in os.walk(save_dir):
                for filename in filenames:
                    if filename.upper().startswith("DRAKS") and ".SL2" in filename.upper():
                        path = os.path.normpath(os.path.join(dirpath, filename))
                        save_paths.setdefault(os.path.normcase(path), path)
        return sorted(save_paths.values())

    def delete_save_files(self):
        save_paths = self.get_save_file_paths()
        if save_paths is None:
            self.show_error("No game version selected. Could not determine which save files to delete.")
            return
        if not save_paths:
            self.show_error("No " + self.game_version.get() + " save files were found.")
            return

        confirmed = tkMB.askyesno("Delete save files",
         "This will permanently delete ALL " + self.game_version.get() + " save files (every character):\n\n" +
         "\n".join(save_paths) + "\n\nThis cannot be undone. Continue?",
         icon="warning", default="no")
        if not confirmed:
            return

        failed_paths = []
        for path in save_paths:
            try:
                os.remove(path)
            except OSError as e:
                logging.exception('Could not delete save file {}: {}'.format(path, e))
                failed_paths.append(path)

        if failed_paths:
            self.show_error("Could not delete " + str(len(failed_paths)) + " save file(s). " +
             "Make sure the game is closed and try again.")
        else:
            self.show_success("Deleted " + str(len(save_paths)) + " save file(s).")

    #def hyperlink_enter(self):
    #    self.msg_area.config(cursor="hand2")
    
    #def hyperlink_leave(self):
    #    self.msg_area.config(cursor="")
        
    #def hyperlink_click(self):
    #    webbrowser.open_new_tab(r"https://twitch.streamlabs.com/hotpocketremix/")
        
    def get_current_desc_state(self):
        desc_specifiers = {
            "diff": (self.diff.get(), DescriptionState.NORMAL),
            "key_diff": (self.key_diff.get(), DescriptionState.NORMAL),
            "souls_diff": (self.soul_diff.get(), DescriptionState.NORMAL),
            "boss_soul_transpose_chance": (self.boss_soul_transpose_chance.get(), DescriptionState.NORMAL),
            "start_items": (self.start_items_diff.get(), DescriptionState.NORMAL),
            "fashion": (self.fashion_bool.get(), DescriptionState.NORMAL),
            "npc_armor": (self.npc_armor_bool.get(), DescriptionState.NORMAL),
            "npc_weapons": (self.npc_weapons_bool.get(), DescriptionState.NORMAL),
            "starting_gifts": (self.randomize_starting_gifts.get(), DescriptionState.NORMAL),
            "starting_stats": (self.randomize_starting_stats.get(), DescriptionState.NORMAL),
            "use_lv": (self.use_lordvessel.get(), DescriptionState.NORMAL),
            "use_lord_souls": (self.use_lord_souls.get(), DescriptionState.NORMAL),
            "ascend_weapons": (self.ascend_weapons_bool.get(), DescriptionState.NORMAL),
            "ascend_weapons_chance": (self.ascend_weapons_chance.get(), DescriptionState.NORMAL),
            "set_up_hints": (self.set_up_hints.get(), DescriptionState.NORMAL),
            "keys_not_in_dlc": (self.keys_not_in_dlc.get(), DescriptionState.NORMAL),
            "no_black_knight_weapons": (self.no_black_knight_weapons.get(), DescriptionState.NORMAL),
        }
        return DescriptionState(desc_specifiers, self.desc_area)
        
    def update_desc_with_fade(self, overwrite_desc_specifiers):
        current_state = self.get_current_desc_state()
        current_desc_specifiers = current_state.desc_specifiers
        for k in current_desc_specifiers:
            if k in overwrite_desc_specifiers:
                current_desc_specifiers[k] = overwrite_desc_specifiers[k]
            else:
                (current_val, current_tag) = current_desc_specifiers[k] 
                current_desc_specifiers[k] = (current_val, DescriptionState.DEEMPH)
        current_state.write_state_to_area()

    def update_desc_for_hover(self, hovered_parts, no_emph = False):
        overwrite_desc_specifiers = {}
        current_state = self.get_current_desc_state()
        for part in hovered_parts:
            if no_emph:
                # Only NORMAL the currently shown desc part, rather
                #  than EMPH the to-be-shown desc part.
                overwrite_desc_specifiers[part] = (current_state.desc_specifiers[part][0], DescriptionState.NORMAL)
            else:
                if hovered_parts[part] == current_state.desc_specifiers[part][0]:
                    overwrite_desc_specifiers[part] = (hovered_parts[part], DescriptionState.NORMAL)
                else:
                    overwrite_desc_specifiers[part] = (hovered_parts[part], DescriptionState.EMPH)
        self.update_desc_with_fade(overwrite_desc_specifiers)
        self.has_hovered_desc = True
        
    def setup_hover_events(self, hover_object, hovered_parts, no_emph=False):
        hover_object.bind("<Enter>", lambda _: self.update_desc_for_hover(hovered_parts, no_emph))
        hover_object.bind("<Leave>", lambda _: self.update_desc(respect_current_hover = False))
        hover_object.bind("<Return>", lambda _: self.update_desc(respect_current_hover = False))
        hover_object.bind("<space>", lambda _: self.update_desc(respect_current_hover = False))
        try:    # Combobox doesn't have 'configure' method
            hover_object.configure(command = lambda: self.update_desc_for_hover(hovered_parts, no_emph))
        except:
            pass
        
    def update_desc(self, respect_current_hover=True):
        if not (respect_current_hover and self.has_hovered_desc):
            self.has_hovered_desc = False
            self.get_current_desc_state().write_state_to_area()
            
    def update(self):
        if self.key_diff.get() == rngopts.RandOptKeyDifficulty.LEAVE_ALONE:
            #self.use_lordvessel.set(False)
            self.use_lordvessel.set(rngopts.RandOptLordvesselLocation.GWYNEVERE)
            self.use_lord_souls.set(False)
            self.keys_not_in_dlc.set(False)
            #self.lv_check.config(state="disabled")
            self.gui_lordvessel.config(state="disabled")
            self.lord_soul_check.config(state="disabled")
            self.keys_not_in_dlc_check.config(state="disabled")
        else:
            #self.lv_check.config(state="normal")
            self.gui_lordvessel.config(state="readonly")
            self.lord_soul_check.config(state="normal")
            self.keys_not_in_dlc_check.config(state="normal")

        """
        if self.key_diff.get() == rngopts.RandOptKeyDifficulty.SPEEDRUN_MODE:
            self.diff.set(rngopts.RandOptDifficulty.EASY)
            self.diff_rbutton1.config(state="disabled")
            self.diff_rbutton2.config(state="disabled")
            self.diff_rbutton3.config(state="disabled")
        else:
            self.diff_rbutton1.config(state="normal")
            self.diff_rbutton2.config(state="normal")
            self.diff_rbutton3.config(state="normal")
            """
        if self.key_diff.get() == rngopts.RandOptKeyDifficulty.SPEEDRUN_MODE:
            self.gui_diff.config(state="disabled")
        else:
            self.gui_diff.config(state="readonly")

        if self.soul_diff.get() == rngopts.RandOptSoulItemsDifficulty.TRANSPOSE:
            self.gui_boss_soul_transpose_chance.config(state="readonly")
        else:
            self.gui_boss_soul_transpose_chance.config(state="disabled")

        if self.ascend_weapons_bool.get():
            self.gui_ascend_weapons_chance.config(state="readonly")
        else:
            self.gui_ascend_weapons_chance.config(state="disabled")

        if self.game_version.get() == rngopts.RandOptGameVersion.REMASTERED:
            self.hint_check.config(state="normal")
        else:
            self.set_up_hints.set(False)
            self.hint_check.config(state="disabled")
        self.update_desc()
        
    def get_current_options(self):
        return rngopts.RandomizerOptions(self.diff.get(), self.fashion_bool.get(), 
         self.key_diff.get(), self.use_lordvessel.get(), self.use_lord_souls.get(), 
         self.soul_diff.get(), self.start_items_diff.get(), self.game_version.get(),
         self.npc_armor_bool.get(), self.ascend_weapons_bool.get(), self.keys_not_in_dlc.get(),
         self.set_up_hints.get(), self.no_black_knight_weapons.get(), self.reroll_seed.get(),
         self.npc_weapons_bool.get(), self.boss_soul_transpose_chance.get(),
         self.ascend_weapons_chance.get(), self.dark_mode.get(), self.randomize_starting_gifts.get(),
         self.randomize_starting_stats.get())

    def save_current_options(self):
        try:
            ini_parser.save_ini(INI_FILE, self.get_current_options())
            self.show_success("Settings have been saved as the default.")
        except Exception as e:
            logging.exception('Could not save default settings: {}'.format(e))
            self.show_error("Could not save settings as default.")

    def randomize_data(self, chr_init_data):
        options = self.get_current_options()

        rng = random.Random()
        rng.seed(int(hashlib.sha256(self.seed_string.get().encode('utf-8')).hexdigest(), 16))
        return options, randomize_item_table.build_table(options, rng, chr_init_data), rng
    
    def get_new_seed(self):
        new_hex_seed = hashlib.sha256(str(self.seed_rng.random()).encode('utf-8')).hexdigest()
        # Swap some letters in the hexadecimal seed to be more easily readable.
        #  Useful for distinguishing letters on-stream, and for those with
        #  impaired vision.
        
        SUBS_DICT = {'0': 'b', '1': 'c', '2': 'f', '3': 'i', '4': 'j',
         '5': 'k', '6': 'p', '7': 'q', '8': 'r', '9': 'v', 'a': 'x', 
         'b': 'y', 'c': 'z', 'd': '2', 'e': '4', 'f': '5'}
        
        self.seed_string.set(''.join([SUBS_DICT.get(c, '') for c in new_hex_seed]))
        self.seed_entry.config(fg=self.entry_state.normal_color, font=self.entry_state.normal_font)
        self.entry_state.with_placeholder = False

    def seed_changed(self):
        self.limit_seed_length()
        value = self.seed_string.get()
        self.seed_entry.config(bg=self.current_theme()["entry_bg"])
        
    def is_seed_empty(self):
        seed = self.seed_string.get()
        return seed is None or len(seed) < 1 or self.entry_state.with_placeholder

    def prepare_seed_for_randomization(self, honor_reroll=True):
        if (honor_reroll and self.reroll_seed.get()) or self.is_seed_empty():
            self.get_new_seed()
        
    def get_syncnum_string(self, random_source):
        syncnum = "%07d" % random_source.randrange(10000000)
        syncnum_str = syncnum[0:4] + "-" + syncnum[4:7]
        return syncnum_str
        
    def export_seed_info(self, syncnum=None, use_randomized_data=None):
        if use_randomized_data is None:
            self.prepare_seed_for_randomization(honor_reroll=False)
        if self.is_seed_empty():
            self.seed_entry.config(bg=self.current_theme()["invalid_bg"])
            return
        if self.game_version.get() not in [rngopts.RandOptGameVersion.PTDE, rngopts.RandOptGameVersion.REMASTERED]:
            self.game_version_menu.configure(style="Highlight.GameVersion.TCombobox")
            return
        
        new_dir_name = "random-seed-" + datetime.datetime.today().strftime("%Y-%m-%d--%H-%M-%S-%f")
        new_dirpath = os.path.join(os.getcwd(), new_dir_name)
        try: 
            os.makedirs(new_dirpath)
        except OSError:
            if not os.path.isdir(new_dirpath):
                raise
        
        if use_randomized_data:
            (options, randomized_data, rng) = use_randomized_data
        else:
            (options, randomized_data, rng) = self.randomize_data(None)
        (table, randomized_chr_data) = randomized_data
            
        #syncnum = self.get_syncnum_string(rng) #confused by this call as the sync already been changed
        
        result_ilp = table.build_itemlotparam()
        ilp_binary_export = result_ilp.export_as_binary()
        result_slp = table.build_shoplineup()
        slp_binary_export = result_slp.export_as_binary()
        chr_cheatsheet = randomized_chr_data.return_cheatsheet()
        cip_binary_export = randomized_chr_data.export_as_binary()
        cheat_string = table.build_cheatsheet(show_event_flags=False)
        hint_string = table.build_hintsheet()

        seed_info = "Randomizer version: " + VERSION_NUM \
            + "\n\nSeed: " + str(self.seed_string.get()) \
            + "\n\n" + options.as_string() \
            + "\nSyncNum: " + (syncnum if syncnum != None else "?") \
            + "\n\nSettings Sync:\n" + self.settings_string_io.construct().decode()

        if options.randomize_starting_gifts and hasattr(randomized_chr_data, "randomized_gifts"):
            seed_info += "\n\n" + gift_s.assignments_as_string(randomized_chr_data.randomized_gifts)


        ITEMLOT_FILEPATH = os.path.join(new_dirpath, "ItemLotParam.param")
        SHOPLINEUP_FILEPATH = os.path.join(new_dirpath, "ShopLineupParam.param")
        CHRINIT_FILEPATH = os.path.join(new_dirpath, "CharaInitParam.param")
        CHEATSHEET_FILEPATH = os.path.join(new_dirpath, "cheatsheet.txt")
        HINTSHEET_FILEPATH = os.path.join(new_dirpath, "hintsheet.txt")
        SEEDINFO_FILEPATH = os.path.join(new_dirpath, "seed_info.txt")
        HINTDEBUG_FILEPATH = os.path.join(new_dirpath, "hint_debug.txt")
        
        with open(ITEMLOT_FILEPATH, 'wb') as f:
            f.write(ilp_binary_export)
        with open(SHOPLINEUP_FILEPATH, 'wb') as f:
            f.write(slp_binary_export)
        with open(CHRINIT_FILEPATH, 'wb') as f:
            f.write(cip_binary_export)
        with open(CHEATSHEET_FILEPATH, 'w') as f:
            f.write(cheat_string + chr_cheatsheet)
        with open(HINTSHEET_FILEPATH, 'w') as f:
            f.write(hint_string)
        with open(SEEDINFO_FILEPATH, 'w') as f:
            f.write(seed_info)

        if (options.set_up_hints and (syncnum != None)):
            table.hint_builder.WriteDebugFile(HINTDEBUG_FILEPATH)
          
        if not use_randomized_data:
            self.msg_continue_button.lower()
            self.msg_area.config(state="normal")
            self.msg_area.delete(1.0, "end")
            self.msg_area.insert("end", "\n")
            self.msg_area.insert("end", "SUCCESS", "yay")
            self.msg_area.insert("end", "! The information for this seed has been exported in the directory\n  {}\n\n".format(new_dir_name))
            self.msg_area.insert("end", "SyncNum: {}\n  (When racing, all SyncNums should be equal or settings do not match.)\n\n".format(syncnum if syncnum != None else "?"))
            self.msg_area.insert("end", 'If you want to easily share this seed and settings with your friends, '
                                        'right click on this window and select "Copy settings sync". \n\n')
            self.msg_area.insert("end", "Click \"Back\" to begin again, or click \"Quit\" to exit.\n\n")
            self.configure_message_tags()
            self.msg_area.config(state="disabled")
            self.msg_area.lift()
            self.back_button.lift()
            self.msg_quit_button.lift()
            
        return new_dir_name
        
    def export_to_gameparam(self):
        if self.game_version.get() == rngopts.RandOptGameVersion.PTDE:
            paths_to_search = PTDE_GAMEPARAM_PATH_LIST
            menu_paths = PTDE_ENGMENU_PATH_LIST
        elif self.game_version.get() == rngopts.RandOptGameVersion.REMASTERED:
            paths_to_search = DS1R_GAMEPARAM_PATH_LIST
            menu_paths = DS1R_ENGMENU_PATH_LIST
        else:
            paths_to_search = []
        
        needs_menu_file = self.randomize_starting_gifts.get() or (
            self.game_version.get() == rngopts.RandOptGameVersion.REMASTERED and self.set_up_hints.get())

        # find our gameparam file
        gameparam_filepath = None
        gameparambak_filepath = None
        for filepath in paths_to_search:
            normed_path = os.path.normpath(os.path.join(os.getcwd(), filepath))
            if os.path.isfile(normed_path):
                gameparam_filepath = normed_path
                gameparambak_filepath = normed_path + ".bak"
                break

        # find our menu text file
        has_engmenu = False
        enmenu_filepath = None
        enmenubak_filepath = None
        for filepath in menu_paths:
            normed_path = os.path.normpath(os.path.join(os.getcwd(), filepath))
            if os.path.isfile(normed_path):
                has_engmenu = True
                enmenu_filepath = normed_path
                enmenubak_filepath = normed_path + ".bak"
                break
                
        is_remastered = (self.game_version.get() == rngopts.RandOptGameVersion.REMASTERED)
        
        if gameparam_filepath is None:
            self.msg_area.config(state="normal")
            self.msg_area.delete(1.0, "end")
            self.msg_area.insert("end", "\n\n")
            self.msg_area.insert("end", "ERROR", "error_red")
            self.msg_area.insert("end", ': GameParam.parambnd[.dcx] is missing or cannot be opened.'
                ' Check that this program is in the correct directory and GameParam.parambnd[.dcx] is present and retry.\n\n'
                'Click "Continue" to continue in seed-information-only mode, or'
                ' click "Quit" to exit.')
            self.configure_message_tags()
            self.msg_area.config(state="disabled")
            self.export_button.config(state="disabled")
            self.lift_msg_area()
            return
        if not has_engmenu and needs_menu_file:
            self.msg_area.config(state="normal")
            self.msg_area.delete(1.0, "end")
            self.msg_area.insert("end", "\n\n")
            self.msg_area.insert("end", "ERROR", "error_red")
            self.msg_area.insert("end", ": menu.msgbnd[.dcx] is missing or cannot be opened." + 
             " Check that this program is in the correct directory and menu.msgbnd[.dcx] is present and retry.\n\n" +
             "Click \"Continue\" to continue in seed-information-only mode, or" + 
             " click \"Quit\" to exit.")
            self.configure_message_tags()
            self.msg_area.config(state="disabled")
            self.export_button.config(state = "disabled")
            self.lift_msg_area()
            return
        else:
            if is_remastered:
                gp_filename = "GameParam.parambnd.dcx"
                enmenu_filename = "menu.msgbnd.dcx"
            else:
                gp_filename = "GameParam.parambnd"
                enmenu_filename = "menu.msgbnd"

            if os.path.isfile(gameparambak_filepath):
                shutil.copy2(gameparambak_filepath, gameparam_filepath)
            if has_engmenu and os.path.isfile(enmenubak_filepath):
                shutil.copy2(enmenubak_filepath, enmenu_filepath)
            
            # open our gameparam file
            with open(gameparam_filepath, "rb") as f:
                content = f.read()
            try:
                if is_remastered:
                    if not dcx_handler.appears_dcx(content):
                        raise ValueError(".dcx file does not appear to be DCX-compressed.")
                    content = dcx_handler.uncompress_dcx_content(content)
                content_list = bnd_rebuilder.unpack_bnd(content)
            except:
                self.msg_area.config(state="normal")
                self.msg_area.delete(1.0, "end")
                self.msg_area.insert("end", "\n\n")
                self.msg_area.insert("end", "ERROR", "error_red")
                self.msg_area.insert("end",
                   ': {0} is malformed or corrupted and cannot be parsed to export randomized items. If possible, restore '
                   '{0} from a backup copy.\n\nClick "Continue" to continue in seed-information-only mode, or '
                   'click "Quit" to exit.'.format(gp_filename))
                self.configure_message_tags()
                self.msg_area.config(state="disabled")
                self.export_button.config(state="disabled")
                self.lift_msg_area()
                return
            
            # open our menu text file
            # TODO: Consolidate this instead of duplicating
            if needs_menu_file:
                with open(enmenu_filepath, "rb") as f:
                    enmenu_content = f.read()
                try:
                    if is_remastered:
                        if not dcx_handler.appears_dcx(enmenu_content):
                            raise ValueError(".dcx file does not appear to be DCX-compressed.")
                        enmenu_content = dcx_handler.uncompress_dcx_content(enmenu_content)
                    enmenu_content_list = bnd_rebuilder.unpack_bnd(enmenu_content)
                except:
                    self.msg_area.config(state="normal")
                    self.msg_area.delete(1.0, "end")
                    self.msg_area.insert("end", "\n\n")
                    self.msg_area.insert("end", "ERROR", "error_red")
                    self.msg_area.insert("end", 
                    ": " + enmenu_filename + " is malformed or corrupted and cannot be" + 
                    " parsed to inject hints. If possible, restore " + enmenu_filename + " from a backup copy.\n\n" +
                    "Click \"Continue\" to continue in seed-information-only mode, or" + 
                    " click \"Quit\" to exit.")
                    self.configure_message_tags()
                    self.msg_area.config(state="disabled")
                    self.export_button.config(state = "disabled")
                    self.lift_msg_area()
                    return
            
            # Back up GameParam.parambnd if needed.
            if not os.path.isfile(gameparambak_filepath):
                shutil.copy2(gameparam_filepath, gameparambak_filepath)

            # Back up menu.msgbnd if needed.
            if needs_menu_file and not os.path.isfile(enmenubak_filepath):
                shutil.copy2(enmenu_filepath, enmenubak_filepath)
                
            self.prepare_seed_for_randomization()

            for index, (file_id, filepath, filedata) in enumerate(content_list):
                if (filepath == "N:\\FRPG\\data\\INTERROOT_win32\\param\\GameParam\\CharaInitParam.param" or
                 filepath == "N:\\FRPG\\data\\INTERROOT_x64\\param\\GameParam\\CharaInitParam.param"):
                    chr_init_data = filedata

            # TODO: Implement this system correctly by passing chr_init_data
            #  instead of None to preserve externally modified characters (e.g. another mod).
            #  However, we need some way to determine external modifications
            #  compared to data left over from a previous run that changed
            #  ChrInit data.
            (options, randomized_data, rng) = self.randomize_data(None)
            (item_table, randomized_chr_data) = randomized_data
            #syncnum = self.get_syncnum_string(rng)
            
            result_ilp = item_table.build_itemlotparam()
            ilp_binary_export = result_ilp.export_as_binary()
            result_slp = item_table.build_shoplineup()
            slp_binary_export = result_slp.export_as_binary()
            cip_binary_export = randomized_chr_data.export_as_binary()
            if options.set_up_hints:
                item_table.hint_builder.ConstructHintList(rng)

            syncnum = self.get_syncnum_string(rng)

            if options.randomize_starting_gifts:
                gift_update_count = self.update_starting_gift_menu_messages(
                    enmenu_content_list, randomized_chr_data.randomized_gifts)
                if gift_update_count == 0:
                    self.show_error("Could not find starting gift menu text to update.")
                    return
        
            for index, (file_id, filepath, filedata) in enumerate(content_list):
                if (filepath == "N:\\FRPG\\data\\INTERROOT_win32\\param\\GameParam\\ItemLotParam.param" or
                 filepath == "N:\\FRPG\\data\\INTERROOT_x64\\param\\GameParam\\ItemLotParam.param"):
                    content_list[index] = (file_id, filepath, ilp_binary_export)
                if (filepath == "N:\\FRPG\\data\\INTERROOT_win32\\param\\GameParam\\ShopLineupParam.param" or
                 filepath == "N:\\FRPG\\data\\INTERROOT_x64\\param\\GameParam\\ShopLineupParam.param"):
                    content_list[index] = (file_id, filepath, slp_binary_export)
                if (filepath == "N:\\FRPG\\data\\INTERROOT_win32\\param\\GameParam\\CharaInitParam.param" or
                 filepath == "N:\\FRPG\\data\\INTERROOT_x64\\param\\GameParam\\CharaInitParam.param"):
                     content_list[index] = (file_id, filepath, cip_binary_export)
            new_content = bnd_rebuilder.repack_bnd(content_list)
            if is_remastered:
                new_content = dcx_handler.compress_dcx_content(new_content)
            with open(gameparam_filepath, "wb") as f:
                f.write(new_content)
            
            # Write out our menu text if we need to
            if needs_menu_file:
                if options.set_up_hints:
                    for index, (file_id, filepath, filedata) in enumerate(enmenu_content_list):
                        if (filepath == "N:\\FRPG\\data\\Msg\\Data_ENGLISH\\Blood_writing_.fmg"):
                            fmgData = FMGHandler(FMGHandler.load_from_file_content(filedata))
                            item_table.hint_builder.AddHintsToBloodMessages(fmgData, rng)
                            enmenu_content_list[index] = (file_id, filepath, fmgData.export_as_binary())
                    new_content = bnd_rebuilder.repack_bnd(enmenu_content_list)
                    if is_remastered:
                        new_content = dcx_handler.compress_dcx_content(new_content)
                    with open(enmenu_filepath, "wb") as f:
                        f.write(new_content)
                elif options.randomize_starting_gifts:
                    new_content = bnd_rebuilder.repack_bnd(enmenu_content_list)
                    if is_remastered:
                        new_content = dcx_handler.compress_dcx_content(new_content)
                    with open(enmenu_filepath, "wb") as f:
                        f.write(new_content)
           
            seed_folder = self.export_seed_info(syncnum, (options, randomized_data, rng))
                
            self.msg_continue_button.lower()
            self.msg_area.config(state="normal")
            self.msg_area.delete(1.0, "end")
            self.msg_area.insert("end", "SUCCESS", "yay")
            self.msg_area.insert("end", "! {} has been modified successfully.\n\n"
                "The information for this seed has been exported in the directory\n\n  {}\n\n".format(gp_filename, seed_folder))
            self.msg_area.insert("end", "SyncNum: {}\n  (When racing, all SyncNums should be equal or settings do not match.)\n\n".format(syncnum))
            self.msg_area.insert("end", 'If you want to easily share this seed and settings with your friends, '
                                        'right click on this window and select "Copy settings sync". \n\n')
            self.msg_area.insert("end", 'Click "Back" to begin again, or click "Quit" to exit.')
            self.configure_message_tags()
            self.msg_area.config(state="disabled")
            self.msg_area.lift()
            self.back_button.lift()
            self.msg_quit_button.lift()
                
    def limit_seed_length(self):
        value = self.seed_string.get()
        if len(value) > MAX_SEED_LENGTH: 
            self.seed_string.set(value[:MAX_SEED_LENGTH])

    @staticmethod
    def add_placeholder_to(entry, placeholder, color="grey", font=None):
        normal_color = entry.cget("fg")
        normal_font = entry.cget("font")
        
        if font is None:
            font = normal_font

        state = Placeholder_State()
        state.normal_color = normal_color
        state.normal_font = normal_font
        state.placeholder_color = color
        state.placeholder_font = font
        state.placeholder_text = placeholder
        state.with_placeholder = True

        def on_focusin(event, entry=entry, state=state):
            if state.with_placeholder:
                entry.delete(0, "end")
                entry.config(fg=state.normal_color, font=state.normal_font)
                state.with_placeholder = False

        def on_focusout(event, entry=entry, state=state):
            if entry.get() == '':
                entry.insert(0, state.placeholder_text)
                entry.config(fg=state.placeholder_color, font=state.placeholder_font)
                state.with_placeholder = True

        def disable_placeholder(entry=entry, state=state):
            entry.config(fg=state.normal_color, font=state.normal_font)
            state.with_placeholder = False

        entry.insert(0, placeholder)
        entry.config(fg=color, font=font)

        entry.bind('<FocusIn>', on_focusin, add="+")
        entry.bind('<FocusOut>', on_focusout, add="+")

        entry.placeholder_state = state
        entry.disable_placeholder = disable_placeholder
        return state
        
    def check_for_new_version(self):
        CHECK_VERSION_URL = r'https://raw.githubusercontent.com/HotPocketRemix/DarkSoulsItemRandomizer/master/version.txt'
        try:
            r = requests.get(CHECK_VERSION_URL, timeout=2)
            if r.status_code == requests.codes.ok:
                page_content = r.content
                page_version_num = page_content.split(b'\n')[0].strip().decode('utf-8')
                if LooseVersion(page_version_num) > LooseVersion(VERSION_NUM):
                    self.back_button.lower()
                    self.msg_area.config(state="normal")
                    self.msg_area.delete(1.0, "end")
                    self.msg_area.insert("end", "\n\n")
                    self.msg_area.insert("end", "ATTENTION", "error_red")
                    self.msg_area.insert("end", "! There is a new version of the Item Randomizer available.\n\n" +
                    "It is recommended that you update to the newest version. Old versions\n" + 
                    "will NOT be supported and may have bugs fixed in the latest release." +
                    "\n\nClick \"Continue\" to use the current version anyway, or click \"Quit\" to exit.")
                    self.configure_message_tags()
                    self.msg_area.lift()
                    self.msg_continue_button.lift()
                    self.msg_quit_button.lift()
        except:
            pass

    def popup_menu_show(self, event):
        try:
            self.popup_menu.tk_popup(event.x_root, event.y_root, 0)
        finally:
            self.popup_menu.grab_release()

    def settings_string_copy(self):
        if self.is_seed_empty():
            self.get_new_seed()

        try:
            constructed_value = self.settings_string_io.construct()
            self.root.clipboard_clear()
            self.root.clipboard_append(constructed_value)
        except InvalidValueError:
            tkMB.showerror('Error copying data', 'Invalid or incomplete settings detected, cannot copy')
        except Exception as e:
            logging.exception('Could not copy settings sync string to clipboard: {}'.format(e))
            tkMB.showerror('Error copying data', 'Could not copy data to clipboard')

    def settings_string_paste(self):
        try:
            clipboard = self.root.clipboard_get()
            if not isinstance(clipboard, str) or len(clipboard) > 512:
                raise ValueError

            if not self.settings_string_io.parse(clipboard):
                raise Exception
            tkMB.showinfo('Yay!', 'Settings applied')

        except IncompatibleVersionError:
            tkMB.showerror('Error applying settings', 'Data from an incompatible version in the clipboard')

        except Exception as e:
            logging.exception('Could not parsesettings sync string from clipboard: {}'.format(e))
            tkMB.showerror('Error applying settings', 'Invalid data in the clipboard')

    def show_error(self, text):
        self.msg_area.config(state="normal")
        self.msg_area.delete(1.0, "end")
        self.msg_area.insert("end", "\n\n")
        self.msg_area.insert("end", "ERROR", "error_red")
        self.msg_area.insert("end", ": " + text)
        self.configure_message_tags()
        self.lift_msg_area()

    def show_success(self, text):
        self.msg_area.config(state="normal")
        self.msg_area.delete(1.0, "end")
        self.msg_area.insert("end", "\n\n")
        self.msg_area.insert("end", "SUCCESS", "yay")
        self.msg_area.insert("end", ": " + text)
        self.configure_message_tags()
        self.lift_msg_area()


if __name__ == "__main__":
    logging.basicConfig(stream=sys.stdout, level=logging.WARN)
    maingui = MainGUI()
    maingui.root.mainloop()
