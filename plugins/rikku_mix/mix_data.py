# Rikku's Mix Database and Formula Engine

# List of all available ingredients in FFX
INGREDIENTS = sorted([
    "Potion", "Hi-Potion", "X-Potion", "Mega-Potion", "Ultra Potion",
    "Ether", "Turbo Ether", "Elixir", "Megalixir",
    "Antidote", "Eye Drops", "Echo Screen", "Soft", "Holy Water",
    "Remedy", "Al Bhed Potion",
    "Phoenix Down", "Mega Phoenix",
    "Sleeping Powder", "Silence Mine", "Smoke Bomb", "Shadow Gem",
    "Power Distiller", "Mana Distiller", "Speed Distiller", "Ability Distiller",
    "Healing Spring", "Mana Spring", "Stamina Spring", "Soul Spring",
    "Light Curtain", "Lunar Curtain", "Star Curtain",
    "Chocobo Feather", "Chocobo Wing",
    "Stamina Tonic", "Mana Tonic", "Twin Stars", "Three Stars",
    "Hero Drink", "Dark Matter", "Underdog's Secret", "Winning Formula",
    "Key to Success", "Wings to Discovery", "Door to Tomorrow", "Gambler's Spirit"
])

# Dict of mix outcomes, details, and common/practical formulas
MIX_OUTCOMES = {
    "Trio of 9999": {
        "description": "All attacks and heals deal/restore 9,999 damage/HP for the current battle.",
        "recipes": [
            ("Dark Matter", "Potion"),
            ("Dark Matter", "Hi-Potion"),
            ("Wings to Discovery", "Wings to Discovery"),
            ("Door to Tomorrow", "Door to Tomorrow"),
            ("Gambler's Spirit", "Gambler's Spirit"),
            ("Underdog's Secret", "Underdog's Secret"),
            ("Key to Success", "Potion")
        ]
    },
    "Hyper Mighty G": {
        "description": "Applies Haste, Protect, Shell, Regen, and Auto-Life to all active characters.",
        "recipes": [
            ("Underdog's Secret", "Healing Spring"),
            ("Underdog's Secret", "Chocobo Feather"),
            ("Underdog's Secret", "Light Curtain"),
            ("Underdog's Secret", "Star Curtain"),
            ("Megalixir", "Chocobo Wing"),
            ("Wings to Discovery", "Chocobo Wing")
        ]
    },
    "Ultra NulAll": {
        "description": "Applies NulFire, NulFrost, NulThunder, NulTide, and 5 stacks of Cheer, Focus, Aim, and Reflex to active party.",
        "recipes": [
            ("Healing Spring", "Healing Spring"),
            ("Healing Spring", "Chocobo Feather"),
            ("Light Curtain", "Light Curtain"),
            ("Lunar Curtain", "Lunar Curtain"),
            ("Star Curtain", "Star Curtain")
        ]
    },
    "Final Elixir": {
        "description": "Fully restores HP and MP, revives fallen allies, and cures all status ailments (except zombie).",
        "recipes": [
            ("Key to Success", "Potion"),
            ("Key to Success", "Hi-Potion"),
            ("Megalixir", "Potion"),
            ("Elixir", "Phoenix Down")
        ]
    },
    "Super Mighty G": {
        "description": "Applies Haste, Protect, Shell, and Regen to the active party.",
        "recipes": [
            ("Chocobo Feather", "Light Curtain"),
            ("Chocobo Feather", "Star Curtain"),
            ("Chocobo Feather", "Lunar Curtain"),
            ("Chocobo Wing", "Light Curtain")
        ]
    },
    "Mighty G": {
        "description": "Applies Haste, Protect, and Shell to all active party members.",
        "recipes": [
            ("Chocobo Feather", "Potion"),
            ("Chocobo Feather", "Hi-Potion"),
            ("Power Distiller", "Power Distiller"),
            ("Mana Distiller", "Mana Distiller")
        ]
    },
    "Eccentrick": {
        "description": "Doubles the rate of Overdrive gauge charge for the active party.",
        "recipes": [
            ("Underdog's Secret", "Megalixir"),
            ("Megalixir", "Megalixir"),
            ("Megaphoenix", "Megalixir")
        ]
    },
    "Hot Spurs": {
        "description": "Multiplies the rate of Overdrive charge by 1.5 for all active party members.",
        "recipes": [
            ("Underdog's Secret", "Potion"),
            ("Underdog's Secret", "Hi-Potion"),
            ("Underdog's Secret", "X-Potion"),
            ("Underdog's Secret", "Elixir")
        ]
    },
    "Freedom X": {
        "description": "Reduces MP cost of all spells and abilities to 0 for all active party members.",
        "recipes": [
            ("Three Stars", "Three Stars"),
            ("Twin Stars", "Twin Stars"),
            ("Three Stars", "Twin Stars")
        ]
    },
    "Sunburst": {
        "description": "Deals exactly 19,998 fixed, non-elemental damage to all enemies.",
        "recipes": [
            ("Underdog's Secret", "Underdog's Secret"),
            ("Underdog's Secret", "Winning Formula"),
            ("Winning Formula", "Winning Formula")
        ]
    },
    "Super Nova": {
        "description": "Deals exactly 19,998 fire-elemental damage to all enemies.",
        "recipes": [
            ("Dark Matter", "Dark Matter"),
            ("Dark Matter", "Bomb Fragment"),
            ("Dark Matter", "Electro Marble")
        ]
    },
    "Hazardous Shell": {
        "description": "Deals heavy physical damage and inflicts Poison, Darkness, Silence, and Sleep on all enemies.",
        "recipes": [
            ("Sleeping Powder", "Power Distiller"),
            ("Silence Mine", "Power Distiller"),
            ("Smoke Bomb", "Power Distiller")
        ]
    },
    "Mega Vitality": {
        "description": "Doubles the Max HP of all active party members for the current battle.",
        "recipes": [
            ("Stamina Tonic", "Stamina Tonic"),
            ("Stamina Tonic", "Potion"),
            ("Stamina Tonic", "Hi-Potion")
        ]
    },
    "Mega Mana": {
        "description": "Doubles the Max MP of all active party members for the current battle.",
        "recipes": [
            ("Mana Tonic", "Mana Tonic"),
            ("Mana Tonic", "Potion"),
            ("Mana Tonic", "Hi-Potion")
        ]
    },
    "Ultra Potion": {
        "description": "Fully restores HP to all active party members (exceeds the 9,999 limit).",
        "recipes": [
            ("Potion", "Potion"),
            ("Potion", "Hi-Potion"),
            ("Hi-Potion", "Hi-Potion")
        ]
    },
    "Hero Drink": {
        "description": "Makes all physical attacks of one character deal critical damage.",
        "recipes": [
            ("Hero Drink", "Potion"),
            ("Hero Drink", "Hi-Potion")
        ]
    },
    "Miracle Drink": {
        "description": "Makes all physical attacks of all active party members deal critical damage.",
        "recipes": [
            ("Hero Drink", "Hero Drink"),
            ("Hero Drink", "Underdog's Secret")
        ]
    }
}

# Fast lookup map populated from the outcomes database
FORMULA_LOOKUP = {}
for outcome, details in MIX_OUTCOMES.items():
    for r1, r2 in details["recipes"]:
        # Ensure commutative pairs are saved
        FORMULA_LOOKUP[(r1, r2)] = outcome
        FORMULA_LOOKUP[(r2, r1)] = outcome

def calculate_mix(item1, item2):
    """
    Returns the resulting mix name and its details.
    Uses precise lookup and smart fallback rules to resolve any ingredient pair.
    """
    # 1. Direct Lookup
    pair = (item1, item2)
    if pair in FORMULA_LOOKUP:
        name = FORMULA_LOOKUP[pair]
        return name, MIX_OUTCOMES[name]["description"]
        
    # 2. General Fallback Rules
    # If using Dark Matter with anything, usually outputs Trio of 9999 or Super Nova
    if item1 == "Dark Matter" or item2 == "Dark Matter":
        return "Trio of 9999", MIX_OUTCOMES["Trio of 9999"]["description"]
        
    # If using Underdog's Secret or Winning Formula with anything, usually Hot Spurs
    if item1 in ("Underdog's Secret", "Winning Formula") or item2 in ("Underdog's Secret", "Winning Formula"):
        return "Hot Spurs", MIX_OUTCOMES["Hot Spurs"]["description"]
        
    # Standard fallback is Ultra Potion (for restorative combos) or Mighty G
    if any(item in item1.lower() or item in item2.lower() for item in ("potion", "elixir", "tonic")):
        return "Ultra Potion", MIX_OUTCOMES["Ultra Potion"]["description"]
        
    if any(item in item1.lower() or item in item2.lower() for item in ("curtain", "feather", "wing")):
        return "Mighty G", MIX_OUTCOMES["Mighty G"]["description"]
        
    # Damage fallback
    return "Hazardous Shell", MIX_OUTCOMES["Hazardous Shell"]["description"]
