class Entity():
    all_conditions = [
        "blinded",
        "charmed",
        "deafened",
        "frightened",
        "grappled",
        "incapacitated",
        "invisible",
        "paralyzed",
        "petrified",
        "poisoned",
        "prone",
        "restrained",
        "stunned",
        "unconscious",
    ]

    def __init__(self):
        self.action_points = 1
        self.bonus_points = 1
        self.reaction_points = 1
        # self.party =
        # self.uid =

        # self.base_pos