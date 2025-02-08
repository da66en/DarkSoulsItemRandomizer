import item_lot_formatter
import items_setup as item_s
import locations_setup as loc_s
import random
import fmg_handler

HINT_LOCATIONS = {
    8110: {"id": 8110, "area": "Undead Asylum", "original_text": "Exchange"},
    1200: {"id": 1200, "area": "Firelink Shrine", "original_text": "Path ahead"},
    1201: {"id": 1201, "area": "Firelink Shrine", "original_text": "Here!"},
    1202: {"id": 1202, "area": "Undead Burg", "original_text": "Imminent Merchant"},
    1100: {"id": 1100, "area": "Undead Burg", "original_text": "Imminent drake..."},
    1104: {"id": 1104, "area": "Undead Burg", "original_text": "Jumping off ahead"},
    1101: {"id": 1101, "area": "Undead Burg", "original_text": "Prisoner ahead"},
    1102: {"id": 1102, "area": "Undead Parish", "original_text": "Prisoner ahead"},
    1103: {"id": 1103, "area": "Undead Parish", "original_text": "Blacksmith ahead"},
    2000: {"id": 2000, "area": "Darkroot Garden", "original_text": "Follow the shining flowers"},
    2001: {"id": 2001, "area": "Darkroot Garden", "original_text": "Are the trees moving?"},
    1003: {"id": 1003, "area": "Depths", "original_text": "I can't take this"},
    1000: {"id": 1000, "area": "Depths", "original_text": "Try sliding down"},
    1002: {"id": 1002, "area": "Depths", "original_text": "Imminent shortcut"},
    1001: {"id": 1001, "area": "Depths", "original_text": "Weakness: Head"},
    4001: {"id": 4001, "area": "Blighttown", "original_text": "Path Ahead"},
    4000: {"id": 4000, "area": "Quelaag's Domain", "original_text": "Illusory Wall"},
    3001: {"id": 3001, "area": "The Catacombs", "original_text": "Try divine"},
    3000: {"id": 3000, "area": "The Catacombs", "original_text": "Treasure"},
    3002: {"id": 3002, "area": "The Catacombs", "original_text": "Blacksmith ahead"},
    3003: {"id": 3003, "area": "The Catacombs", "original_text": "Liar"},
    3004: {"id": 3004, "area": "The Catacombs", "original_text": "Up"},
    3100: {"id": 3100, "area": "The Catacombs", "original_text": "Shortcut ahead"},
    6000: {"id": 6000, "area": "New Londo Ruins", "original_text": "Need Curses"},
    6002: {"id": 6002, "area": "New Londo Ruins", "original_text": "Imminent jumping off..."},
    6001: {"id": 6001, "area": "New Londo Ruins", "original_text": "Need Covenant"},
    5000: {"id": 5000, "area": "Sen's Fortress", "original_text": "Prisoner ahead"},
    5101: {"id": 5101, "area": "Anor Londo", "original_text": "Path ahead"},
    5100: {"id": 5100, "area": "Anor Londo", "original_text": "Try Projectile"},
    6003: {"id": 6003, "area": "Valley of Drakes", "original_text": "Ring Ahead"},
    4100: {"id": 4100, "area": "Demon Ruins", "original_text": "Safe Zone Ahead"},
    7001: {"id": 7001, "area": "Crystal Cave", "original_text": "Path Ahead"}
}

TRASH_HINTS = {
    "That's what she said.",
    "Right you are, Kenny!",
    "It's a secret to everybody.",
    "Grumble grumble grumble...",
    "It is dangerous to go alone!",
    "Have you tried turning it off and back on again?",
    "The right man in the wrong place can make all the difference in the world.",
    "I watched C-beams glitter in the dark near the Tannhäuser Gate",
    "55 Burgers, 55 Fries, 55 Tacos, 55 Pies...",
    "Rip and Tear until it is done.",
    "These pretzels are making me thirsty.",
    "Stay awhile and listen.",
    "Thou hast lost an eighth.",
    "Remember your mantra.",
    "I used to be an adventurer like you. Then I took an arrow in the knee...",
    "Bingpot!",
    "Did I do that?",
    "Rise and shine Mr. Freeman.",
    "We are the things that were and shall be again!",
    "Hail to the king, baby!",
    "Never half-ass two things. Whole-ass one thing.",
    "Treat yo'self.",
    "Let’s-a-go!",
    "What's a Paladin?",
    "Adjust gamma until picture on the left is barely visible.",
    "Darmok and Jalad... at Tanagra.",
    "Some days, you just can't get rid of a bomb!",
    "Bill, strange things are afoot at the Circle K.",
    "No matter where you go, there you are.",
    "Do you know of the Klingon proverb that tells us revenge is a dish that is best served cold?",
    "Ray, if someone asks you if you're a god, you say YES!",
    "Hokey religions and ancient weapons are no substitute for a good blaster at your side, kid.",
    "Worst. Seed. Ever.",
    "Goonies never say die.",
    "Would you say I have a plethora of pinatas?",
    "Never go in against a Sicilian when death is on the line!",
    "Kneel before Zod."
}

USEFUL_LOCATIONS = {
    2540: {"name": "Sif", "location_id": 2540, "hint_text": "Great Wolf Sif holds \n{0}"},
    2580: {"name": "Bed of Chaos", "location_id": 2580, "hint_text": "Bed of Chaos holds \n{0}"},
    2700: {"name": "Manus", "location_id": 2700, "hint_text": "Manus, Father of the Abyss holds \n{0}"},
    2710: {"name": "Kalameet", "location_id": 2710, "hint_text": "Black Dragon Kalameet holds \n{0}"},
    2630: {"name": "4 Kings", "location_id": 2630, "hint_text": "The Four Kings watch over \n{0}"},
    2560: {"name": "Nito", "location_id": 2560, "hint_text": "Gravelord Nito holds \n{0}"},
    35300000: {"name": "Ash Lake Hydra", "location_id": 35300000, "hint_text": "The Hydra in Ash Lake holds \n{0}"},
    34510000: {"name": "Everlasting Dragon Tail", "location_id": 34510000, "hint_text": "The Everlasting Dragon's tail contains \n{0}"},
    1320100: {"name": "Great Hollow Branch", "location_id": 1320100, "hint_text": "The slippery branch in Great Hollow has \n{0}"},
    1700160: {"name": "Crystal Caves path", "location_id": 1700160, "hint_text": "The unseen path in Crystal Caves leads to \n{0}"},
    1500420: {"name": "Cage Key", "location_id": 1500420, "hint_text": "The cage key locks away \n{0}"},
    1010510: {"name": "Residence Key", "location_id": 1010510, "hint_text": "Griggs is imprisoned in Lower Burg with \n{0}"},
    1810060: {"name": "Asylum West 2 Key", "location_id": 1810060, "hint_text": "The locked door in the Asylum yields \n{0}"},
    1700020: {"name": "Avelyn Check", "location_id": 1700020, "hint_text": "Inside a chest on top of a bookshelf rests \n{0}"},
    1700200: {"name": "Giant Cell Key", "location_id": 1700200, "hint_text": "Logan's cell in Seath's prison contains \n{0}"},
    1700530: {"name": "Seath's Room", "location_id": 1700530, "hint_text": "The chest in Seath's study holds \n{0}"},
    1210510: {"name": "Light Check 1", "location_id": 1210510, "hint_text": "Try light in Oolacile to find \n{0}"},
    1210520: {"name": "Light Check 2", "location_id": 1210520, "hint_text": "Let there be light in Oolacile and get \n{0}"},
    1210500: {"name": "Royal Wood Chest", "location_id": 1210500, "hint_text": "A chest in the Royal Wood holds \n{0}"},
    34200200: {"name": "Undead Dragon - Valley", "location_id": 34200200, "hint_text": "The Undead Dragon of the Valley holds \n{0}"},
    1310500: {"name": "Andre - ToTG", "location_id": 1310500, "hint_text": "Andre's statue in the Tomb grasps \n{0}"},
    1100370: {"name": "Andre - Annex Key", "location_id": 1100370, "hint_text": "Andre's statue in the Painting grasps \n{0}"},
    27100200: {"name": "Broken Pendant Golem", "location_id": 27100200, "hint_text": "A blue golem in the Archives holds \n{0}"},
    1100: {"name": "Ingward", "location_id": 1100, "hint_text": "The keeper of New Londo holds \n{0}"},
    41601000: {"name": "Oolacile Sorc", "location_id": 41601000, "hint_text": "A lonely sorcerer in Oolacile guards \n{0}"},
    2520: {"name": "Priscilla", "location_id": 2520, "hint_text": "Crossbreed Priscilla holds onto \n{0}"},
    1300100: {"name": "Vamos Ledge", "location_id": 1300100, "hint_text": "On a ledge above Vamos lies \n{0}"},
    1410060: {"name": "Lava island", "location_id": 1410060, "hint_text": "On ledge surrounded by Tauros Demons rests \n{0}"},
    1410100: {"name": "Demon Ruins Chest", "location_id": 1410100, "hint_text": "The chest in Demon Ruins holds \n{0}"},
    1300100: {"name": "Vamos Ledge", "location_id": 1300100, "hint_text": "On a ledge above Vamos lies \n{0}"},
}

USEFUL_ITEMS = {
    390: {"item_id": 390, "item_name": "Fire Keeper Soul"},
    391: {"item_id": 391, "item_name": "Fire Keeper Soul"},
    392: {"item_id": 392, "item_name": "Fire Keeper Soul"},
    393: {"item_id": 393, "item_name": "Fire Keeper Soul"},
    394: {"item_id": 394, "item_name": "Fire Keeper Soul"},
    395: {"item_id": 395, "item_name": "Fire Keeper Soul"},
    396: {"item_id": 396, "item_name": "Fire Keeper Soul"},
    800: {"item_id": 800, "item_name": "Large Ember"},
    801: {"item_id": 801, "item_name": "Very Large Ember"},
    813: {"item_id": 813, "item_name": "Chaos Flame Ember"},
    190000: {"item_id": 190000, "item_name": "Sunlight Maggot"},
}

USEFUL_RINGS = {
    100: {"item_id": 100, "item_name": "Havel's Ring"},
    125: {"item_id": 125, "item_name": "Rusted Iron Ring"},
    143: {"item_id": 143, "item_name": "Ring of Favor and Protection"},
    146: {"item_id": 146, "item_name": "Wolf Ring"},
}

KEY_ITEMS = {
    2013: {"item_id": 2013, "item_name": "Key to the Seal"},
    2014: {"item_id": 2014, "item_name": "Key to the Depths"},
    2016: {"item_id": 2016, "item_name": "Undead Asylum F2 West Key"},
    2021: {"item_id": 2021, "item_name": "Residence Key"},
    2003: {"item_id": 2003, "item_name": "Cage Key"},
    2006: {"item_id": 2006, "item_name": "Archive Tower Giant Cell Key"},
    2022: {"item_id": 2022, "item_name": "Crest Key"},
    2520: {"item_id": 2520, "item_name": "Broken Pendant"},
}

KEY_RINGS = {
    139: {"item_id": 139, "item_name": "Orange Charred Ring"},
    138: {"item_id": 138, "item_name": "Covenant of Artorias"},
}

BIG_KEY_ITEMS = {
    2500: {"item_id": 2500, "item_name": "Lord Soul"},
    2501: {"item_id": 2501, "item_name": "Lord Soul"},
    2502: {"item_id": 2502, "item_name": "Lord Soul"},
    2503: {"item_id": 2503, "item_name": "Lord Soul"},
    2510: {"item_id": 2510, "item_name": "Lordvessel"},
}

AREA_HINT_NAMES = {
    loc_s.AREA.NONE: "None",
    loc_s.AREA.MOVING_NPC: "Gift/Drop/Shop from an NPC that moves around",
    loc_s.AREA.DEPTHS: "Depths",
    loc_s.AREA.LOWER_UNDEAD_BURG: "Lower Undead Burg",
    loc_s.AREA.LOWER_UNDEAD_BURG_RESIDENCE: "Lower Undead Burg",
    loc_s.AREA.UNDEAD_BURG: "Undead Burg",
    loc_s.AREA.UNDEAD_BURG_RESIDENCE: "Undead Burg",
    loc_s.AREA.WATCHTOWER_BASEMENT: "Watchtower Basement",
    loc_s.AREA.UNDEAD_PARISH: "Undead Parish",
    loc_s.AREA.FIRELINK: "Firelink Shrine",
    loc_s.AREA.PAINTED_WORLD: "Painted World of Ariamis",
    loc_s.AREA.PAINTED_WORLD_ANNEX: "Painted World of Ariamis",
    loc_s.AREA.DARKROOT_GARDEN: "Darkroot Garden",
    loc_s.AREA.DARKROOT_FOREST: "Darkroot Garden",
    loc_s.AREA.DARKROOT_BASIN: "Darkroot Basin",
    loc_s.AREA.OOLACILE_SANCTUARY: "Oolacile Sanctuary",
    loc_s.AREA.ROYAL_WOOD: "Royal Wood",
    loc_s.AREA.OOLACILE_TOWNSHIP: "Oolacile Township",
    loc_s.AREA.OOLACILE_HIDDEN: "Oolacile Township",
    loc_s.AREA.KALAMEET_FIGHT: "Royal Wood",
    loc_s.AREA.CHASM_OF_THE_ABYSS: "Chasm of the Abyss",
    loc_s.AREA.CATACOMBS: "Catacombs",
    loc_s.AREA.TOMB_OF_THE_GIANTS_PRE_LV: "Tomb of the Giants",
    loc_s.AREA.TOMB_OF_THE_GIANTS_POST_LV: "Tomb of the Giants",
    loc_s.AREA.GREAT_HOLLOW: "Great Hollow",
    loc_s.AREA.ASH_LAKE: "Ash Lake",
    loc_s.AREA.BLIGHTTOWN: "Blighttown",
    loc_s.AREA.QUELAAGS_DOMAIN: "Quelaag's Domain",
    loc_s.AREA.DEMON_RUINS_NO_LAVA_PRE_LV: "Demon Ruins",
    loc_s.AREA.DEMON_RUINS_NO_LAVA_POST_LV: "Demon Ruins",
    loc_s.AREA.DEMON_RUINS_LAVA: "Demon Ruins",
    loc_s.AREA.LOST_IZALITH: "Lost Izalith",
    loc_s.AREA.SENS_FORTRESS: "Sen's Fortress",
    loc_s.AREA.SENS_CAGE: "Sen's Fortress",
    loc_s.AREA.ANOR_LONDO: "Anor Londo",
    loc_s.AREA.DARKMOON_TOMB: "Anor Londo",
    loc_s.AREA.NEW_LONDO_PRE_SEAL: "New Londo Ruins",
    loc_s.AREA.NEW_LONDO_POST_LV: "New Londo Ruins",
    loc_s.AREA.NEW_LONDO_POST_SEAL: "New Londo Ruins",
    loc_s.AREA.NEW_LONDO_POST_SEAL_SKIP: "New Londo Ruins",
    loc_s.AREA.VALLEY_OF_DRAKES: "Valley of Drakes",
    loc_s.AREA.POST_4K: "After defeating the Four Kings",
    loc_s.AREA.DUKES_PRISON: "The Duke's Archives",
    loc_s.AREA.DUKES_PRISON_EXTRA: "The Duke's Archives",
    loc_s.AREA.DUKES_PRISON_GIANT_CELL: "The Duke's Archives",
    loc_s.AREA.DUKES_ARCHIVES: "The Duke's Archives",
    loc_s.AREA.CRYSTAL_CAVE: "Crystal Cave",
    loc_s.AREA.KILN: "Kiln of the First Flame",
    loc_s.AREA.UNDEAD_ASYLUM: "Undead Asylum",
    loc_s.AREA.UNDEAD_ASYLUM_F2_WEST: "Undead Asylum",
    loc_s.AREA.NPC_RNG_DROP: "Random Enemy Drop"
}

class HintBuilder:
    def __init__(self):
        self.useful_locations = []
        self.useful_items = []
        self.key_items = []
        self.big_keys = []
        self.hint_list = []
        self.hint_locations = HINT_LOCATIONS.copy()

    def AddItemOrLocationToHintBuilder(self, itemlotpart, loc_id):
        item_name = ""
        
        location = loc_s.LOCATIONS[loc_id]
        if location.diff in [loc_s.LOC_DIF.IGNORE, loc_s.LOC_DIF.EMPTY, loc_s.LOC_DIF.LEAVE_ALONE]:
            return

        item = itemlotpart.items[0]
        if item.item_type == item_s.ITEM_TYPE.ARMOR:
            item_name = item_lot_formatter.ARMOR[item.item_id]
        elif item.item_type == item_s.ITEM_TYPE.ITEM:
            item_name = item_lot_formatter.ITEMS[item.item_id]
        elif item.item_type == item_s.ITEM_TYPE.WEAPON:
            item_name = item_lot_formatter.WEAPONS[item.item_id]
        elif item.item_type == item_s.ITEM_TYPE.RING:
            item_name = item_lot_formatter.RINGS[item.item_id]
        

        if loc_id in USEFUL_LOCATIONS:
            hint_string = USEFUL_LOCATIONS[loc_id]["hint_text"]   

            hint_string = hint_string.format(item_name)
            self.useful_locations.append(hint_string)

        hint_string = "Amazing {0} \nfound in {1}"        
        loc_area = AREA_HINT_NAMES[location.area]

        hint_string = hint_string.format(item_name, loc_area)

        # filter our strings into our appropriate hint buckets
        if item.item_type == item_s.ITEM_TYPE.ITEM:
            if item.item_id in USEFUL_ITEMS:
                self.useful_items.append(hint_string)
            elif item.item_id in KEY_ITEMS:
                self.key_items.append(hint_string)
            elif item.item_id in BIG_KEY_ITEMS:
                self.big_keys.append(hint_string)
        elif item.item_type == item_s.ITEM_TYPE.RING:
            if item.item_id in USEFUL_RINGS:
                self.useful_items.append(hint_string)
            elif item.item_id in KEY_RINGS:
                self.key_items.append(hint_string)
                                         
    def ConstructHintList(self, rng: random):
        # 32 total hint slots available
        # take 2 of the big key hints and put them in twice (4 slots)
        # take 6 of the key hints, and put them in twice (12 slots, 16 total)
        # take 4 of the useful items, put them in (4 slots, 20 total)
        # take 6 of the useful locations, put them in (6 slots, 26 total)
        # take 3 trash hints, shuffle them in twice (6 slots, 32 total)

        big_keys = rng.sample(self.big_keys, 2)
        key_items = rng.sample(self.key_items, 6)
        useful_items = rng.sample(self.useful_items, 4)
        useful_locations = rng.sample(self.useful_locations, 6)
        trash_hints = rng.sample(list(TRASH_HINTS), 3)

        self.hint_list = big_keys + big_keys + key_items + key_items + useful_items + useful_locations + trash_hints + trash_hints

    def AddHintsToBloodMessages(self, blood_messages: fmg_handler.FMGHandler, rng: random):
        rng.shuffle(self.hint_list)
        hint_index = 0

        for event in blood_messages.messages:
            if event.id in self.hint_locations and hint_index < len(self.hint_list):
                event.text = self.hint_list[hint_index]
                self.hint_locations[event.id]["new_text"] = event.text
                hint_index += 1

    def WriteDebugFile(self, filepath: str):
        """
        Prints the seed's hint locations into a file at the provided filepath
        """

        hint_debug_text = ""

        for location_id in self.hint_locations:
            location = self.hint_locations[location_id]

            # Remove the line break introduced into the hint text for the game
            single_line_hint = location["new_text"].replace("\n", "")

            # Each hint will be a single line, "<location> - <original message>: <hint message>"
            hint_debug_text += (
                f"{location['area']} - {location['original_text']}: "
                f"{single_line_hint}\n"
            )

        with open(filepath, 'w') as f:
            f.write(hint_debug_text)