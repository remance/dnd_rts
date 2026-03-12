class Character():
    character_list: dict = None

    def __init__(self, character_id):
        character_stat = self.character_list[character_id]
        self.name = character_stat["name"]
        self.strength = character_stat["strength"]
        self.dexterity = character_stat["dexterity"]
        self.constitution = character_stat["constitution"]
        self.intelligence = character_stat["intelligence"]
        self.wisdom = character_stat["wisdom"]
        self.charisma = character_stat["charisma"]