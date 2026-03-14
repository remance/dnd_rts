class Monster():
    monster_list: dict = None
    # challenge_to_exp_table

    def __init__(self, monster_id):
        monster_stat = self.monster_list[monster_id]
        self.alignment = monster_stat["alignment"]
        self.species = monster_stat["species"]
        self.size = monster_stat["size"]
        self.name = monster_stat["name"]
        self.strength = monster_stat["strength"]
        self.dexterity = monster_stat["dexterity"]
        self.constitution = monster_stat["constitution"]
        self.intelligence = monster_stat["intelligence"]
        self.wisdom = monster_stat["wisdom"]
        self.charisma = monster_stat["charisma"]
        self.hit_points = monster_stat["hit_points"]
        self.hit_dice = monster_stat["hit_dice"]
        self.proficiencies = monster_stat["proficiencies"]
        self.armour_class = monster_stat["armour_class"]
        self.challenge = monster_stat["challenge"]
        self.experience = monster_stat["experience"]
        self.immunities = monster_stat["immunities"]
        self.condition_immunities = monster_stat["condition_immunities"]
        self.resistances = monster_stat["resistances"]
        self.vulnerabilities = monster_stat["vulnerabilities"]
        self.actions = monster_stat["actions"]
        self.abilities = monster_stat["abilities"]
