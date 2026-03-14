class Party():
    def __init__(self):
        self.members = []
        self.total_member = 0

    def add_member(self, member):
        member.party = self
        self.members.append(member)
        self.total_member += 1

    def remove_memeber(self, member):
        member.party = None
        self.members.remove(member)
        self.total_member -= 1
