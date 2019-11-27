import math
import pickle
import random
import re

turn = 0
steep = 1
roomCount = 0
realRoomCount = 0

myscore = 0
################################################################################
#TODO
#Implement dropping
#Implement leveling
#Implement some fun powers


################################################################################
#POWER BLOCK
powers = [] #a list of all registered powers
class power:
    def __init__(self, name, powerType, skillTree, level):
        self.name = name
        self.powerType = powerType
        self.skillTree = skillTree
        self.level = level


class attackPower(power):
    def __init__(self, name, powerType, skillTree, level, powerlist, 
            targeting, cost, blurb):
        super().__init__(name, powerType, skillTree, level)
        self.targeting = targeting
        self.cost = cost
        self.powerlist = powerlist
        self.blurb = blurb

    def powerfunc(self, hero, monster):
        global gameRoom
        if 'basicAttack' in self.powerlist:
            hero.attack(monster)
        if auraDam in self.powerlist:
            amount = random.randint(auraDam[0], auraDam[1])
            for target in hero.targets:
                target.damage(amount)
                print(f"{hero.name} deals {amount} damage to {target.name}.")
        if extraAttackRoom in self.powerlist:
            if any([command for command in extraAttackRoom \
                    if command in gameRoom.size or command in gameRoom.desc]):
                hero.attack(monster)
        if 'stun' in self.powerlist:
            monster.stunned = True
            print(f"{hero.name} rings {monster.name}'s bell!")

    def usePower(self, hero, target):
        global gameRoom
        print(f"{hero.name} {self.blurb}")
        if target == gameRoom:
            #power is an AOE power targeting certain kinds of units in the 
            #whole room
            if self.targeting:
                monsters = [monster for monster in gameRoom.monsters if \
                        monster.path in self.targeting]
            else:
                monsters = [gameRoom.monsters]
            if monsters:
                for monster in monsters:
                    #print(f"DEBUG: self is a {type(self)}, hero is a {type(hero)}, target is a {type(target)}")
                    self.powerfunc(hero, monster)
            else:
                print(f"{hero.name} attempted to use the power of {self.name}, "
                    "but nothing happened!1!")
        else:
            #target is a single monster ("attackee")
            if isinstance(self.targeting, list):
                if target in self.targeting:
                    self.powerfunc(hero, target)
                else:
                    print(f"{hero.name} attempted to use the power of "
                            f"{self.name}, but nothing happened!2!")
            else:
                #print(f"DEBUG: self is a {type(self)}, hero is a {type(hero)}, target is a {type(target)}")
                self.powerfunc(hero, target)


def registerpower(name, powerType, skillTree, level, powerlist, targets, cost,
        blurb):
    global powers
    if powerType == 'attack':
        newPower = attackPower(name, powerType, skillTree, level, powerlist, 
                targets, cost, blurb)
        powers.append(newPower)
    else:
        print("This powerType has not been defined (Config Issue).")

def doPowerDrop(party):
    activePowers = [power for power in powers if power.skillTree in \
            [tree for treelist in [hero.trees for hero in party] \
            for tree in treelist]]
    if not activePowers:
        return
    newPower = random.choice(activePowers)
    eligible = [hero.name for hero in party if newPower.skillTree in hero.trees \
            and newPower not in hero.skills]
    if not eligible:
        return
    print(f"You found a level {newPower.level} {newPower.skillTree} power, "
            f"\"{newPower.name}\"!")
    print(f"Eligible heroes: {', '.join(map(str, eligible))}")
    recipientName = input("Who do you want to assign this power to? ")
    assigned = False
    while assigned == False:
        if recipientName in [hero.name for hero in party]:
            recipient = [hero for hero in party \
                    if hero.name == recipientName][0]
            if newPower.skillTree in recipient.trees:
                recipient.skills.append(newPower)
                assigned = True
            else:
                print(f"{recipientName} cannot receive this power because "
                        f"{recipientName} does not have access to " 
                        f"{newPower.skillTree} powers.")
                print(f"Eligible heroes: {', '.join(map(str, eligible))}")
                recipientName = input("Who do you want to assign this power "
                        "to? ")

        else:
            print("There is no hero with that name in the party. Type your "
                    "hero's names carefully.")
            print(f"Eligible heroes: {', '.join(map(str, eligible))}")
            recipientName = input("Who do you want to assign this power to? ")


#here is an example power to give me an idea of what powers need to do
registerpower('heaven and earth', 'attack', 'holy', 1, ['basicAttack'], 
        ['dragonstork', 'teaspirit'], 6, "summons the fire of heaven to smite "
        "all the flying enemies!")
auraDam = [1, 1]
registerpower('swipe', 'attack', 'savagery', 1, [auraDam, 'basicAttack'], None, 
        3, "rakes clawlike hands across the monster's faces.")
extraAttackRoom = ['cramped', 'small']
registerpower('knife party', 'attack', 'fury', 1, ['basicAttack', 
        extraAttackRoom], None, 3, "stabs at the enemy once, and a second time "
        "if they can't get away.")
registerpower('stunning blow', 'attack', 'arms', 1, ['basicAttack', 'stun'],
        None, 4, "slams a monster in the head, causing it to skip its next "
        "action.")



###################1#############################################################
#CHARACTER BLOCK
class meep:
    def __init__(self):
        self.team = 'neutral'
        self.hp = random.randint(15, 25)

    def damage(self, amount):
        self.hp -= amount
        if self.hp <= 0:
            print(f"{self.name} has died of their wounds.")

    def heal(self, amount):
        self.hp += amount
        print(f"{self.name} has {self.hp} hit points.")
        

class hero(meep):
    def __init__(self, path):
        print("With a sound like an thunderclap, a hero joins the party!")
        self.team = 'good'
        self.hp = random.randint(45, 105)
        self.path = path
        print(f"The new hero is a {self.path} of the light with {self.hp} hit " 
                "points.")
        self.name = input("What is this hero's name? ")
        self.targets = []
        self.poison = 0
        if self.path == 'barista':
            self.trees = random.sample(['restoration', 'fire', 'frost', 
                    'earth', 'scholasticism'], 3)
        elif self.path == 'crusher':
            self.trees = random.sample(['fury', 'outlander', 'savagery',
                    'retribution', 'survival'], 3)
        elif self.path == 'druid':
            self.trees = random.sample(['restoration', 'balance', 'savagery',
                    'earth', 'survival'], 3)
        elif self.path == 'janissary':
            self.trees = random.sample(['spirit', 'arms', 'wind', 'outlander', 
                    'fury'], 3)
        elif self.path == 'paladin':
            self.trees = random.sample(['holy', 'arms', 'retribution',
                    'protection', 'discipline'], 3)
        elif self.path == 'priest':
            self.trees = random.sample(['holy', 'discipline', 'spirit',
                    'scholasticism', 'protection'], 3)
        self.level = 1
        self.trophies = []
        self.xp = 0
        self.skills = []
        self.skillCharges = 1

    def attack(self, target):
        global bonus
        amount = random.randint(2, 15)
        print(f"{self.name} strikes a righteous blow against {target.name} "
                f"for {amount} damage!")
        target.damage(amount)
        self.xp += amount / target.startinghp / math.sqrt(self.level)
        bonus += amount / 50

    def chooseSkill(self, targets, powerType):
        possibleSkills = self.getUsuablePowers(powerType)
        if possibleSkills is None:
            return None
        for skill in possibleSkills:
            print(f"{hero.name} can use {skill.name}, which {skill.blurb}")
            command = input("Do you want to use it? ")
            if command in ('Yes', 'Y', 'y', 'yes', 'sure'):
                self.skillCharges -= skill.cost
                return skill
        return None

    def chooseRandomSkill(self, targets, powerType):
        possibleSkills = self.getUsuablePowers(powerType)
        if possibleSkills:
            return random.choice(possibleSkills)
        return None

    def combat(self, gameRoom, party):
        global bonus
        global myscore 
        if len(gameRoom.monsters) == 0:
            return
        for monster in gameRoom.monsters:
            if monster.hp <= 0:
                myscore += math.ceil(monster.score)
                print(f"You got {math.ceil(monster.score)} points!")
                gameRoom.monsters.remove(monster)
                for hero in party:
                    if monster in hero.targets:
                        hero.targets.remove(monster)
                if monster.path not in self.trophies:
                    print(f"{self.name} gathered a trophy from {monster.name}!")
                    self.trophies.append(monster.path)
                    self.xp += 49 / math.sqrt(self.level)
                else:
                    self.xp += monster.startinghp / math.sqrt(self.level)
        while len(self.targets) < 3 and \
                len(gameRoom.monsters) > len(self.targets):
            self.targets.append(random.choice(
                    [monster for monster in gameRoom.monsters 
                    if monster not in self.targets]))
        for monster in self.targets:
            monster.announce(self)
        chooseSkill = None
        if self.skills:
            self.skillCharges += 1
            if 0 < self.skillCharges < 11:
                chooseSkill = self.chooseSkill(self.targets, 'attack')
            else:
                print(f"{self.name} overflows with power, suddenly manifesting "
                        "a secret attack!")
                chooseSkill = self.chooseRandomSkill(self.targets, 'attack')
                self.skillCharges = 0
        if chooseSkill is None or chooseSkill.targeting is None:
            target = str(input("Which one do you want to attack? "))
            if target not in [monster.name for monster in self.targets]:
                print("You missed! Type enemy names more carefully.")
                target = str(input("Which one do you want to attack? "))
                if target not in [monster.name for monster in self.targets]:
                    print("You missed! Type enemy names more carefully.")
            if target in [monster.name for monster in self.targets]:
                attackee = min([monster for monster in self.targets \
                        if monster.name == target])
                if chooseSkill:
                    chooseSkill.usePower(self, attackee)
                else:
                    self.attack(attackee)
                if attackee.hp <= 0:
                    print(f"{attackee.name} has fallen!")
                    myscore += math.ceil(attackee.score)
                    print(f"You got {math.ceil(attackee.score)} points!")
                    gameRoom.monsters.remove(attackee)
                    for hero in party: 
                        if attackee in hero.targets:
                            hero.targets.remove(attackee)
                    if attackee.path not in self.trophies:
                        print(f"{self.name} gathered a trophy from {attackee.name}!")
                        self.trophies.append(attackee.path)
                        self.xp += 49 / math.sqrt(self.level)
                    else:
                        self.xp += attackee.startinghp / math.sqrt(self.level)
                    bonus += 1
        elif isinstance(chooseSkill.targeting, list):
            chooseSkill.usePower(self, gameRoom)

    def getUsuablePowers(self, powerType):
        listofPowers = [skill for skill in self.skills if \
                self.level >= skill.level and self.skillCharges >= skill.cost \
                and skill.powerType == powerType]
        return listofPowers

    def levelUp(self):
        self.level += 1
        self.xp = 0
        print(f"{self.name} becomes level {self.level}!".upper())
        for skill in self.skills:
            if skill.level == self.level:
                print(f"{self.name} can use {skill.name} now!")

    def transition(self, party):
        global bonus
        if hero.poison > 0:
            hero.damage(hero.poison)
            print(f"The poison coursing in {hero.name}'s veins deals "
                    f"{hero.poison} damage.")
            hero.poison = math.floor(hero.poison / 2)
        if hero.poison < 0:
            print(f"The lingering touch of nature heals {-1 * hero.poison} "
                    f"damage from {hero.name}.")
            hero.heal(-1 * hero.poison)
            hero.poison = math.floor(hero.poison / 2)
        if hero.hp < 0:
            if hero in party:
                party.remove(hero)
            if len(party) > 0:
                print(f"{hero.name} has fallen. The party mourns.")
                bonus -= 1
            else:
                print("The party has fallen...")
                bonus -= 2

    def turn(self, gameRoom, party):
        global bonus
        global myscore
        print(" ")
        for monster in gameRoom.monsters:
            if monster.hp <= 0:
                print(f"{monster.name} has fallen!")
                bonus += 1
                myscore += math.ceil(monster.score)
                print(f"You got {math.ceil(monster.score)} points!")
                gameRoom.monsters.remove(monster)
                for hero in party:
                    if monster in hero.targets:
                        hero.targets.remove(monster)
        self.combat(gameRoom, party)
        if self.xp >= 100:
            self.levelUp()

################################################################################
#   HERO CLASSES
################################################################################

class barista(hero):
    def __init__(self):
        super().__init__('barista')
        self.orders = 0
        print(f"{self.name}'s powers are served from a cup of {self.trees[0]}, "
                f"{self.trees[1]}, and {self.trees[2]}!")

    def combat(self, gameRoom, party):
        global bonus
        global myscore
        if len(gameRoom.monsters) == 0:
            return
        self.orders += 1
        while len(self.targets) < 3 and \
                len(gameRoom.monsters) > len(self.targets):
            self.targets.append(random.choice(
                    [monster for monster in gameRoom.monsters 
                    if monster not in self.targets]))
        for monster in gameRoom.monsters:
            if monster.hp <= 0:
                myscore += math.ceil(monster.score)
                print(f"You got {math.ceil(monster.score)} points!")
                gameRoom.monsters.remove(monster)
                for hero in party:
                    if monster in hero.targets:
                        hero.targets.remove(monster)
                if monster.path not in self.trophies:
                    print(f"{self.name} gathered a trophy from {monster.name}!")
                    self.trophies.append(monster.path)
                    self.xp += 49 / math.sqrt(self.level)
                else:
                    self.xp += monster.startinghp / math.sqrt(self.level)
        for monster in self.targets:
            for hero in party:
                if hero != self:
                    if monster in hero.targets:
                        self.orders += 1
            monster.announce(self)
        self.skillCharges += 1
        if 0 < self.skillCharges < 11:
            chooseSkill = self.chooseSkill(self.targets, 'attack')
        else:
            print(f"{self.name} overflows with power, suddenly manifesting "
                    "a secret attack!")
            chooseSkill = self.chooseRandomSkill(self.targets, 'attack')
            self.skillCharges = 0
        if chooseSkill is None or chooseSkill.targeting is None:
            target = str(input("Which one do you want to attack? "))
            if target not in [monster.name for monster in self.targets]:
                print("You missed! Type enemy names more carefully.")
                target = str(input("Which one do you want to attack? "))
                if target not in [monster.name for monster in self.targets]:
                    print("You missed! Type enemy names more carefully.")
            if target in [monster.name for monster in self.targets]:
                attackee = min([monster for monster in self.targets \
                        if monster.name == target])
                if chooseSkill:
                    chooseSkill.usePower(self, attackee)
                else:
                    self.attack(attackee)
                if attackee.hp <= 0:
                    print(f"{attackee.name} has fallen!")
                    myscore += math.ceil(monster.score)
                    print(f"You got {math.ceil(monster.score)} points!")
                    gameRoom.monsters.remove(attackee)
                    for hero in party: 
                        if attackee in hero.targets:
                            hero.targets.remove(attackee)
                    if attackee.path not in self.trophies:
                        print(f"{self.name} gathered a trophy from "
                                f"{attackee.name}!")
                        self.trophies.append(attackee.path)
                        self.xp += 49 / math.sqrt(self.level)
                    else:
                        self.xp += attackee.startinghp / math.sqrt(self.level)
                    bonus += 1
        elif isinstance(chooseSkill.targeting, list):
            chooseSkill.usePower(self, gameRoom)

    def damage(self, amount):
        global bonus
        super().damage(amount)
        if self.hp > 0 and self.orders > 0:
            for target in self.targets:
                print(f"{self.name} spills a hot drink on {target.name}, "
                    f"dealing {amount} damage")
                target.damage(amount)
            bonus += self.orders / 50
            self.orders = 0

    def transition(self, party):
        global bonus
        super().transition(party)
        if self.hp > 0 and self.orders > 0:
            target = random.choice([hero for hero in party 
                    if hero.hp == min(hero.hp for hero in party)])
            print(f"{self.name} serves a highly-customized beverage to "
                    f"{target.name}, healing {self.orders * 2} hit points!")
            target.heal(self.orders * 2)
            bonus += self.orders / 25
            self.orders = 0


class crusher(hero):
    def __init__(self):
        super().__init__('crusher')
        print(f"{self.name}'s power-hoard includes {self.trees[0]}, "
                f"{self.trees[1]}, and {self.trees[2]}.")

    def attack(self, target):
        global bonus
        amount = math.floor(target.hp / 2)
        if amount >= math.floor(self.hp / 8):
            print(f"{self.name} grips the monster tightly until the "
                    f"{target.path} falls apart, dealing {amount} damage.")
            target.damage(amount)
        elif amount * 2 >= math.floor(self.hp / 8):
            super().attack(target)
        else:
            print(f"{self.name} crushes {target.name}'s head.")
            amount = target.hp
            target.damage(amount)
        self.xp += amount / target.startinghp / math.sqrt(self.level)
        bonus += amount / 50


class druid(hero):
    def __init__(self):
        super().__init__('druid')
        self.form = 'new'
        self.naturepower = 0
        print(f"{self.name} was trained by the {self.trees[0]} circle, but "
                f"went on to learn {self.trees[1]} and {self.trees[2]} in "
                "nature.")

    def attack(self, target):
        global bonus
        if self.form == 'cassowary':
            attackBonus = math.ceil(self.naturepower / 3)
            self.naturepower -= attackBonus
            amount = random.randint(2, 15) + attackBonus
            print(f"{self.name} kicks {target.name} for {amount} damage!")
            target.damage(amount)
            bonus += amount / 50
            self.naturepower += math.ceil(amount / 5)
            self.xp += amount / target.startinghp / math.sqrt(self.level)
        else:
            super().attack(target)

    def combat(self, gameRoom, party):
        global bonus
        global myscore
        if len(gameRoom.monsters) == 0:
            return
        if self.form == 'healer' and self.naturepower > 10:
            print(f"{self.name} overflows with the benevolent power of " +
                    "creation!")
            target = random.choice([hero for hero in party 
                    if hero.hp <= self.hp])
            target.heal(6)
            target.poison += -2
            self.naturepower -= 10
            return
        elif self.form == 'healer':
            super().combat(gameRoom, party)
            self.naturepower += len(party)
        elif self.form == 'wolbear':
            if len(self.targets) > 3:
                self.targets = self.targets[:3]
            super().combat(gameRoom, party)
            self.targets = [monster for monster in gameRoom.monsters]
        else: #form == cassowary
            if len(gameRoom.monsters) == 0:
                return
            for monster in gameRoom.monsters:
                if monster.hp <= 0:
                    myscore += math.ceil(monster.score)
                    print(f"You got {math.ceil(monster.score)} points!")
                    gameRoom.monsters.remove(monster)
                    for hero in party:
                        if monster in hero.targets:
                            hero.targets.remove(monster)
                    if monster.path not in self.trophies:
                        print(f"{self.name} gathered a trophy from {monster.name}!")
                        self.trophies.append(monster.path)
                        self.xp += 49 / math.sqrt(self.level)
                    else:
                        self.xp += monster.startinghp / math.sqrt(self.level)
                    bonus += 1
            while len(self.targets) < 3 and \
                    len(gameRoom.monsters) > len(self.targets):
                self.targets.append(random.choice(
                        [monster for monster in gameRoom.monsters 
                        if monster not in self.targets]))
            self.savetargets = len(self.targets)
            super().combat(gameRoom, party)
            if len(self.targets) < self.savetargets and \
                    len(gameRoom.monsters) > 0:
                print(f"{self.name} flies into a frenzy!")
                self.combat(gameRoom, party)

    def damage(self, amount):
        super().damage(amount)
        if self.hp > 0 and self.form == 'wolbear':
            self.poison -= math.ceil(amount / 3)
            self.naturepower += math.ceil(amount / 3)

    def transition(self, party):
        #change forms before poison kicks in
        if self.form == 'new':
            countdruids = len([hero for hero in party if 
                    hero.path == 'druid' and hero.form == 'new'])
            if countdruids % 3 == 0:
                self.form = 'healer'
            elif countdruids % 3 == 1:
                self.form = 'wolbear'
            elif countdruids % 3 == 2:
                self.form = 'cassowary'
            print(f"{self.name} transforms into a mighty {self.form}.")
        else:
            forms = ["healer", "wolbear", "cassowary"]
            hcount = len([hero for hero in party 
                    if hero.path == 'druid' and hero.form == 'healer'])
            pcount = len([hero for hero in party 
                    if hero.path == 'druid' and hero.form == 'cassowary'])
            wcount = len([hero for hero in party 
                    if hero.path == 'druid' and hero.form == 'wolbear'])
            count = min(hcount, pcount, wcount)
            self.canbe = []
            if hcount == count:
                self.canbe.append("healer")
            if pcount == count:
                self.canbe.append("cassowary")
            if wcount == count:
                self.canbe.append("wolbear")
            self.form = random.choice(self.canbe)
            print(f"{self.name} transforms into a mighty {self.form}.")
        super().transition(party)


class janissary(hero):
    def __init__(self):
        super().__init__('janissary')
        print(f"{self.name} tapped into the power of {self.trees[0]}, "
                f"{self.trees[1]}, and {self.trees[2]} at a young age.")

    def combat(self, gameRoom, party):
        global bonus
        global myscore
        if len(gameRoom.monsters) == 0:
            return
        while len(self.targets) < 3 and len(gameRoom.monsters) > \
                len(self.targets):
            self.targets.append(random.choice(
                    [monster for monster in gameRoom.monsters 
                    if monster not in self.targets]))
        for monster in self.targets:
            monster.announce(self)
        self.skillCharges += 1
        if 0 < self.skillCharges < 11:
            chooseSkill = self.chooseSkill(self.targets, 'attack')
        else:
            print(f"{self.name} overflows with power, suddenly manifesting "
                    "a secret attack!")
            chooseSkill = self.chooseRandomSkill(self.targets, 'attack')
            self.skillCharges = 0
        if chooseSkill is None or chooseSkill.targeting is None:
            target = str(input("Which one do you want to attack? "))
            if target not in [monster.name for monster in self.targets]:
                print("You missed! Type enemy names more carefully.")
                target = str(input("Which one do you want to attack? "))
                if target not in [monster.name for monster in self.targets]:
                    print("You missed! Type enemy names more carefully.")
            if target in [monster.name for monster in self.targets]:
                attackee = min([monster for monster in self.targets \
                        if monster.name == target])
                if chooseSkill:
                    chooseSkill.usePower(self, attackee)
                else:
                    spirithp = attackee.hp
                    self.attack(attackee)
                    spirithp = math.floor(spirithp * (random.randint(35,65) / 100))
                    if len(gameRoom.monsters) > 0 and spirithp > 0:
                        target2 = random.choice([monster 
                                for monster in gameRoom.monsters])
                        print(f"A spirit force deals {spirithp} damage to "
                                f"{target2.name}")
                        target2.damage(spirithp)
                        if target2.hp <= 0:
                            print("{} has fallen!".format(target2.name))
                            myscore += math.ceil(target2.score)
                            print(f"You got {math.ceil(target2.score)} points!")
                            for hero in party:
                                if target2 in hero.targets:
                                    hero.targets.remove(target2)
                            if target2 in gameRoom.monsters:
                                gameRoom.monsters.remove(target2)
                            if target2.path not in self.trophies:
                                print(f"{self.name} gathered a trophy from {target2.name}!")
                                self.trophies.append(target2.path)
                                self.xp += 49 / math.sqrt(self.level)
                            else:
                                self.xp += target2.startinghp / math.sqrt(self.level)
                            bonus += 0.5
                    if attackee.hp <= 0:
                        print(f"{attackee.name} has fallen!")
                        myscore += math.ceil(attackee.score)
                        print(f"You got {math.ceil(attackee.score)} points!")
                        for hero in party:
                            if attackee in hero.targets:
                                hero.targets.remove(attackee)
                        gameRoom.monsters.remove(attackee)
                        if attackee.path not in self.trophies:
                            print(f"{self.name} gathered a trophy from {attackee.name}!")
                            self.trophies.append(attackee.path)
                            self.xp += 49 / math.sqrt(self.level)
                        else:
                            self.xp += attackee.startinghp / math.sqrt(self.level)
                        bonus += 1
        elif isinstance(chooseSkill.targeting, list):
            chooseSkill.usePower(self, gameRoom)


class paladin(hero):
    def __init__(self):
        super().__init__('paladin')
        self.weapon = random.choice(['mace', 'sword', 'fork', 'mug', 
                'claymore'])
        print(f"{self.name} wields a holy {self.weapon}, blessed by God "
                "himself, and a matching set of armor.")
        print(f"If that wasn't enough, {self.name} also is gifted with "
                f"{self.trees[0]}, {self.trees[1]}, and {self.trees[2]}.")
        self.armor = 0

    def attack(self, target):
        global bonus
        if target.team != 'evil':
            print("Good meeps cannot fight meeps that are not evil.")
        else:
            amount = random.randint(1, 10)
            if self.weapon == 'mace':
                weapondmg = random.randint(1,6)
            if self.weapon == 'sword':
                weapondmg = random.randint(0,7)
            if self.weapon == 'fork':
                weapondmg = random.choice([1, 1, 1, 3, 3, 3, 9])
            if self.weapon == 'mug':
                weapondmg = 2
            if self.weapon == 'claymore':
                weapondmg = random.choice([0, 0, 0, 0, 2, 4, 6, 8, 10, 12])

            print("{} strikes a righteous blow against "
                    "{} for {} damage!".format(self.name, target.name, 
                    amount + weapondmg))
            target.damage(amount + weapondmg)
            self.xp += amount / target.startinghp / math.sqrt(self.level)
            bonus += amount / 50

    def damage(self, amount):
        self.armor += 1
        if self.armor >= amount:
            self.armor -= amount
            print(f"{self.name}'s holy armor absorbs the attack.")
        else:
            super().damage(amount)


class priest(hero):
    def __init__(self):
        super().__init__('priest')
        self.faith = 3
        print(f"{self.name} adheres to the strictest traditions of "
                f"{self.trees[0]}, {self.trees[1]}, and {self.trees[2]}.")

    def turn(self, gameRoom, party):
        global bonus
        print(" ")
        if len(gameRoom.monsters) != 0:
            do = str(input(f"Do you want {self.name} to Pray? ")).lower()
            amount = math.ceil(self.faith / len(party))
            print(f"{self.name} channels faith to heal the party for "
                    f"{amount} hit points!")
            for hero in party:
                hero.heal(amount)
            if do in ("pray", "p", "y", "yes"):
                self.targets = []
                self.faith += 1
                print(f"{self.name}'s faith is strengthened to {self.faith}.")
                bonus += self.faith / 50
            else: 
                self.combat(gameRoom, party)

################################################################################

class monster(meep):
    global totalturns
    def __init__(self, path):
        super().__init__()
        self.stunned = False
        self.path = path
        self.team = 'evil'
        self.name = None
        self.score = math.ceil(self.hp * 10 / totalturns)
        self.startinghp = self.hp

    def announce(self, hero):
        print(f"{hero.name} faces a {self.path} named {self.name} with "
                f"{self.hp} hp.")

    def attack(self, target):
        amount = random.randint(1,8)
        print(f"{self.name} attacks {target.name} for {amount} damage!")
        target.damage(amount)

    def doLeftAlone(self, gameRoom, party):
        pass

    def turn(self, gameRoom, party):
        global bonus
        global myscore
        if self.stunned:
            print(f"{self.name} is stunned!")
            self.stunned = False
            return
        targetList = [hero for hero in party if self in hero.targets]
        if self.hp <= 0:
            myscore += math.ceil(self.score)
            print(f"You got {math.ceil(self.score)} points!")
            for hero in party:
                if self in hero.targets:
                    hero.targets.remove(self)
            if self in gameRoom.monsters:
                gameRoom.monsters.remove(self)
            bonus += 1
            return
        if any(targetList):
            target = random.choice([hero for hero in party 
                    if self in hero.targets])
            monster.attack(target)
            if target.hp < 0:
                if target in party:
                    party.remove(target)
                if len(party) > 0:
                    print(f"{target.name} has fallen. The party mourns.")
                    bonus -= 1
                else:
                    print("The party has fallen...")
                    bonus -= 2
        else:
            monster.doLeftAlone(gameRoom, party)
        print(" ")

################################################################################
#   MONSTER CLASSES
################################################################################

class bloodknight(monster):
    def __init__(self):
        super().__init__('blood knight')

    def attack(self, target):
        amount = random.randint(1, 8)
        heal = math.ceil(amount / 3)
        print("{} strikes {} with an unholy ".format(self.name, target.name) +
                "blade, dealing {} damage and leaching {} ".format(amount, heal) +
                "hit points!")
        target.damage(amount + heal)
        if self.hp > 0:
            self.heal(heal)

    def doLeftAlone(self, gameRoom, party):
        global myscore
        amount = random.randint(2,5)
        print(f"{self.name} sacrifices its health to heal the monsters for "
                f"{amount} hit points.")
        for monster in gameRoom.monsters:
            monster.heal(amount)
            self.damage(amount)
        if self.hp < 0:
            myscore += math.ceil(self.score)
            print(f"You got {math.ceil(self.score)} points!")
            for hero in party:
                if self in hero.targets:
                    hero.targets.remove(self)
            gameRoom.monsters.remove(self)
            gameRoom.monstercount -= 1


class CRT(monster):
    def __init__(self):
        super().__init__('CRT')

    def announce(self, hero):
        super().announce(hero)
        print(f"{hero.name} takes 1 damage from the sheer pain of looking at "
                f"{self.name}.")
        hero.damage(1)

    def doLeftAlone(self, gameRoom, party):
        print(f"{self.name} sits alone in the dark, ignored by everyone. Which "
                "is how it should be.")


class dragonstork(monster):
    def __init__(self):
        super().__init__('dragonstork')
        self.deepbreath = 1

    def attack(self, target):
        amount = random.randint(1,4) + self.deepbreath
        print(f"{target.name} is burned for {amount} damage!")
        target.damage(amount)
        self.deepbreath += 1
        self.score *= 1.1

    def doLeftAlone(self, gameRoom, party):
        print(f"{self.name} takes a deep breath!")
        self.deepbreath *= 2
        self.score += math.ceil(self.hp * 10 / totalturns)

    def turn(self, gameRoom, party):
        global bonus
        print(" ")
        if self.stunned:
            print(f"{self.name} is stunned!")
            self.stunned = False
            return
        targetList = [hero for hero in party if self in hero.targets]
        if self.hp <= 0:
            for hero in party:
                if self in hero.targets:
                    hero.targets.remove(self)
            if self in gameRoom.monsters:
                gameRoom.monsters.remove(self)
            bonus += 0.4
            return
        if any(targetList):
            print("{} breathes out fire!".format(self.name))
            for hero in party:
                monster.attack(hero)
                if hero.hp < 0:
                    party.remove(hero)
                    if len(party) > 0:
                        print(f"{hero.name} has fallen. The party mourns.")
                        bonus -= 0.5
                    else:
                        print("The party has fallen...")
                        bonus -= 1
        else:
            monster.doLeftAlone(gameRoom, party)


class orc(monster):
    def __init__(self):
        super().__init__('orc')

    def attack(self, target):
        global bonus
        if self.hp > 7:
            super().attack(target)
        else:
            amount = random.randint(1, 12)
            target.damage(amount)
            print(f"{self.name} screams in bestial rage and slices {hero.name} "
                    f"for {amount} damage.")
            if target.hp < 0:
                party.remove(target)
                if len(party) > 0:
                    print(f"{target.name} has fallen. The party mourns.")
                    bonus -= 0.5
                else:
                    print("The party has fallen...")
                    bonus -= 1


    def doLeftAlone(self, gameRoom, party):
        global bonus
        target = random.choice([hero for hero in party 
                if len(hero.targets) == 
                max([len(hero.targets) for hero in party])])
        target.targets.append(self)
        print(f"{self.name} charges into battle against {target.name}!")
        self.attack(target)
        self.attack(target)
        if target.hp < 0:
            party.remove(target)
            if len(party) > 0:
                print(f"{target.name} has fallen. The party mourns.")
                bonus -= 0.5
            else:
                print("The party has fallen...")
                bonus -= 1


class reject(monster):
    def __init__(self):
        super().__init__('reject')

    def attack(self, target):
        super().attack(target)
        if self in target.targets:
            target.targets.remove(self)

    def doLeftAlone(self, gameRoom, party):
        global bonus
        target = random.choice([hero for hero in party])
        print(f"{self.name} sneaks up behind {target.name}...")
        self.attack(target)
        self.attack(target)
        self.attack(target)
        if target.hp < 0:
            party.remove(target)
            if len(party) > 0:
                print(f"{target.name} has fallen. The party mourns.")
                bonus -= 0.5
            else:
                print("The party has fallen...")
                bonus -= 1


class spider(monster):
    def __init__(self):
        super().__init__('spider')

    def attack(self, target):
        super().attack(target)
        if random.randint(1,3) == 1:
            target.poison += 1
            print(f"{target.name} doesn't feel so good.")

    def doLeftAlone(self, gameRoom, party):
        print(f"{self.name} sprays a green ichor from its jaws!")
        for hero in party:
            amount = random.randint(0,5)
            if amount != 0:
                hero.poison += amount
                print(f"{hero.name} really doesn't feel good.")


class teaspirit(monster):
    def __init__(self):
        global steep
        super().__init__('tea spirit')
        self.brew = 1
        self.score = math.ceil(self.score * (1 + (steep / 10)))

    def attack(self, target):
        global steep
        amount = math.floor(random.randint(1,8) * (1 + (steep / 10)))
        if self.name == "The Iron Maiden of Mercy":
            print(f"{self.name} heals {target.name} for {amount} hit points, "
                    "but will exact a terrible price later.")
            target.heal(amount)
            target.poison += math.ceil(amount * 1.5)
        else:
            print(f"{self.name} attacks {target.name} for {amount} damage!")
            target.damage(amount)

    def doLeftAlone(self, gameRoom, party):
        global steep
        roll = random.randint(1, 3)
        if roll == 1:
            self.brew *= 2
            brewhealth = math.ceil(self.hp / self.brew) + steep
            print(f"{self.name} brews up a new monster with {brewhealth} "
                    "hit points!")
            new = newmonster(gameRoom.monsters)
            new.hp = brewhealth
            new.score = new.hp
            self.hp -= math.ceil(self.hp / 2)
            if self.hp <= 0:
                for hero in party:
                    if self in hero.targets:
                        hero.targets.remove(self)
                if self in gameRoom.monsters:
                    gameRoom.monsters.remove(self)
            else:
                self.hp += steep
            gameRoom.monsters.append(new)
        else:
            print("The air around {} fills with a ".format(self.name) +
                    "colored, liquidy power, as if {} ".format(self.name) +
                    "was steeping in the dungeon room.")
            steep += 1

    def turn(self, gameRoom, party):
        global bonus
        global myscore
        global steep
        print(" ")
        if self.stunned:
            print(f"{self.name} is stunned!")
            self.stunned = False
            return
        targetList = [hero for hero in party if self in hero.targets]
        if self.hp <= 0:
            myscore += math.ceil(self.score)
            print(f"You got {math.ceil(self.score)} points!")
            for hero in party:
                if self in hero.targets:
                    hero.targets.remove(self)
            if self in gameRoom.monsters:
                gameRoom.monsters.remove(self)
            return
        #always attacks if cornered, otherwise only 1/3 of the time
        roll = random.randint(1, 3)
        if any(targetList):
            if len(targetList) == len(party) or roll == 3:
                target = random.choice([hero for hero in party 
                        if self in hero.targets])
                monster.attack(target)
                if target.hp < 0:
                    party.remove(target)
                    if len(party) > 0:
                        print(f"{target.name} has fallen. The party mourns.")
                        bonus -= 0.5
                    else:
                        print("The party has fallen...")
                        bonus -= 1
            elif roll == 1:
                self.brew *= 2
                brewhealth = math.ceil(self.hp / self.brew) + steep
                print(f"{self.name} brews up a new monster with {brewhealth} "
                        "hit points!")
                new = newmonster(gameRoom.monsters)
                new.hp = brewhealth
                new.score = new.hp
                self.hp -= math.ceil(self.hp / 2)
                if self.hp <= 0:
                    for hero in party:
                        if self in hero.targets:
                            hero.targets.remove(self)
                    if self in gameRoom.monsters:
                        gameRoom.monsters.remove(self)
                else:
                    self.hp += steep
                gameRoom.monsters.append(new)
            else:
                print("The air around {} fills with a ".format(self.name) +
                        "colored, liquidy power, as if {} ".format(self.name) +
                        "was steeping in the dungeon room.")
                steep += 1
        else:
            monster.doLeftAlone(gameRoom, party)


class turtle(monster):
    def __init__(self):
        super().__init__('turtle')
        self.hp = random.randint(12, 20)
        self.score = math.ceil(self.hp * 10 / totalturns)
        self.shell = 0

    def damage(self, amount):
        global bonus
        if self.shell == 1:
            print("{}'s shell absorbs the damage!".format(self.name))
            bonus -= amount / 100
        else:
            super().damage(amount)
            if self.hp > 0 and not self.stunned:
                self.shell = 1
                print("{} recedes into its shell".format(self.name))

    def doLeftAlone(self, gameRoom, party):
        if self.shell == 0:
            print(f"Despite near-safety, {self.name} recedes back into its "
                    "shell")
            self.shell = 1

    def turn(self, gameRoom, party):
        if self.stunned:
            print(f"{self.name} is stunned!")
            self.stunned = False
            return
        if self.shell == 1:
            self.shell = 0
            print("{} emerges from its shell".format(self.name))
        super().turn(gameRoom, party)


def recruit():
    path = random.choice(['paladin', 'priest', 'janissary', 'crusher',
            'barista', 'druid'])
    if path == 'crusher':
        newrecruit = crusher()
    if path == 'janissary':
        newrecruit = janissary()
    if path == 'priest':
        newrecruit = priest()
    if path == 'paladin':
        newrecruit = paladin()
    if path == 'barista':
        newrecruit = barista()
    if path == 'druid':
        newrecruit = druid()
    return newrecruit


def newmonster(monsters):
    path = random.choice(['orc', 'CRT', 'spider', 'reject',
            'blood knight', 'dragonstork', 'turtle', 'tea spirit'])
    if path == 'blood knight':
        new = bloodknight()
        namelist = ("Elric", "Vlad", "Arthas", "Shah", "Guld", "Elroy", "Aaral",
                "Zeld", "Marcos", "Alastor", "Zol", "Darksol", "Johan", "Olam")
        new.name = random.choice([name for name in namelist 
                if name not in [monster.name for monster in monsters]])
        print("{} the blood knight approaches.".format(new.name))
    elif path == 'CRT':
        new = CRT()
        namelist = ("RCA", "Gauss", "Nimo", "Zeus", "Sony", "Panasonic",
                "Toshiba", "Crookes", "Penetron", "Tritron", "Telefunk")
        new.name = random.choice([name for name in namelist 
                if name not in [monster.name for monster in monsters]])
        print("To your horror, you realize that a CRT, " +
                "{}, is here.".format(new.name))
    elif path == 'dragonstork':
        new = dragonstork()
        namelist = ("Smog", "Error", "Firfir", "Mnemne", "Pyral", "Bleu", "Eld",
                "Draco", "Lili", "Dental", "Spike", "Tia", "Yssie", "Alie", 
                "Noz")
        new.name = random.choice([name for name in namelist 
                if name not in [monster.name for monster in monsters]])
        print("Awash in flame, the dragonstork {} alights.".format(new.name))
    elif path == 'orc':
        new = orc()
        namelist = ("Aar", "Bar", "Dar", "Gar", "Har", "Lar", "Kar", "Mar",
                "Nar", "Roar", "Sar", "Tar", "Var", "Zar", "Oor", "Chew")
        new.name = random.choice([name for name in namelist 
                if name not in [monster.name for monster in monsters]])
        print("An orc, {}, is here. It's angry, as usual.".format(new.name))
    elif path == 'reject':
        new = reject()
        namelist = ("Slade", "Otis", "Slim", "Hands", "McCoy", "Lue", "Amy",
                "Riddle", "Betsy", "Davey", "Reggie", "Black", "Pete", "Kyle")
        new.name = random.choice([name for name in namelist 
                if name not in [monster.name for monster in monsters]])
        print("{} the reject sneers and sharpens two thin blades.".format(new.name))
    elif path == 'spider':
        new = spider()
        namelist = ("Eensy", "Weensy", "Parker", "Ith", "Zith", "Vixh", "Zlit",
                "Viih", "Liix", "Vrin", "Vril", "Vilk", "Meel", "Mree", "Veem")
        new.name = random.choice([name for name in namelist 
                if name not in [monster.name for monster in monsters]])
        print("The giant spider {} decends from the ceiling.".format(new.name))
    elif path == 'turtle':
        new = turtle()
        namelist = ("Mike", "Leo", "Fel", "Donna", "Grim", "Wiseman", "Rocky",
                "Snap", "Green", "Adam", "'Toise", "Darwin", "Speedy", "Nope")
        new.name = random.choice([name for name in namelist 
                if name not in [monster.name for monster in monsters]])
        print("{} the turtle slowly peers at you, then attacks.".format(new.name))
    elif path == 'tea spirit':
        new = teaspirit()
        namelist = ("Leaf", "Chai", "Pearl", "Dragon", "Pu'erh", "Red",
                "White", "Dian", "Earl", "Chaga", "Mo", "d'Arco", "Senna",
                "The Iron Maiden of Mercy")
        new.name = random.choice([name for name in namelist 
                if name not in [monster.name for monster in monsters]])
        print("A familiar, pungent scent begins to fill the room. It's "
                "unmistakeable; {} smells like tea spirit.".format(new.name))
    return new


class room:
    def __init__(self, party):
        global roomCount
        global realRoomCount
        self.size = random.choice(['cramped', 'huge', 'small', 'low-roofed'])
        self.desc = random.choice(['well-lit', 'smelly', 'blue', 'dark',
                'empty'])
        print("You stand in a {}, {} room.".format(self.size, self.desc))
        self.monsters = []
        roomCount += 1
        if self.desc != 'empty':
            #right now, there's a 33% chance of an empty room anyhow
            self.monstercount = random.choice([0, 
                    random.randint(len(party), len(party)* 2), 
                    random.randint(len(party), len(party)* 2)])
            if self.monstercount == 1:
                print("A monster appears!")
            elif self.monstercount > 1:
                print(f"{self.monstercount} monsters appear!")
            for m in range(self.monstercount):
                self.monsters.append(newmonster(self.monsters))
            if self.monstercount > 0:
                realRoomCount += 1
        else:
            self.monstercount = 0


#scoring
# load the previous score if it exists
try:
    with open('GMG.dat', 'rb') as file:
        scoredict = pickle.load(file)
except:
    scoredict = {}


#The Game Begins
totalturns = int(input("How many turns do you want the game to last? ")) - 1
print("As the sun rises, you awaken and steel yourself to face the day.")
print("You yearn to see the sun again, but before you can do that, you "
        "must face a gauntlet of monsters. For this is...")
print(" ")
print("GOOD MORNING, GAUNTLET")
print(" ")
if scoredict:
    if totalturns in scoredict:
        highscores = scoredict[totalturns]
        if highscores is not None:
            print(f"High score: {highscores[0][0]}: {highscores[0][1]}")
print("The game will last {} turns. Good luck!".format(totalturns + 1))

party = []
party.append(recruit())
party.append(recruit())
gameRoom = room(party)
bonus = 10
for hero in party:
    hero.transition(party)
while turn <= totalturns and len(party) > 0:
    if turn > 0:
        herohp = sum([hero.hp for hero in party])
        if herohp < 150:
            scoreUp = math.ceil(
                    ((sum([monster.score for monster in gameRoom.monsters]) /2) + 
                    len(gameRoom.monsters) + realRoomCount) * 
                    (1 + ((100 - herohp) / 100)) * bonus * 
                    realRoomCount / totalturns)
            if scoreUp >= 0:
                print(f"You got {scoreUp} points!")
                myscore += scoreUp
        else:
            scoreUp = math.ceil(
                    ((sum([monster.score for monster in gameRoom.monsters]) / 2) + 
                    len(gameRoom.monsters) + realRoomCount) * 
                    (100 / sum([hero.hp for hero in party])) * bonus * 
                    realRoomCount / totalturns)
            if scoreUp >= 0:
                print(f"You got {scoreUp} points!")
                myscore += scoreUp
    bonus = 10
    if turn == totalturns:
        print("IT IS THE LAST TURN!!!2!")
    if len(gameRoom.monsters) == 0:
        print("This room is empty!")
        if sum([len(hero.skills) for hero in party]) < realRoomCount:
            doPowerDrop(party)
        print("Time to go to a new room!")
        if myscore > 0:
            print(f"Your current score is {myscore}!")
        print(" ")
        for hero in party:
            hero.transition(party)
        if roomCount % 5 == 0:
            party.append(recruit())
        roomCount += 1
        gameRoom = room(party)
    else:
        for hero in party:
            if hero.hp > 0:
                hero.turn(gameRoom, party)
        for monster in gameRoom.monsters:
            if monster.hp > 0:
                monster.turn(gameRoom, party)
    turn += 1
if len(party) == 0:
    print("The story closes on a bitter note.")
elif len(gameRoom.monsters) == 0:
    print(f"{party[0].name} stands, panting, over the prone body of the last "
            f"monster. {party[0].name} is victorious!")
else:
    print("We leave our hero(es). Fate will play out, but we've lost interest.")
print("The final score is {}.".format(myscore))


def scorecrunch(scoredict, myscore, totalturns):
    try:
        scores = scoredict[totalturns]
    except KeyError:
        scoredict[totalturns] = []
        scores = scoredict[totalturns]
    if any(scores):
        scores.sort(key = lambda x: int(x[1]), reverse = True)
        if all([myscore > score[1] for score in scores]):
            print("A NEW HIGH SCORE YOU AMAZING MUFFIN!!")
            scoreName = input("TELL ME YOUR NAME, CHAMPION! ")
            scores.insert(0, (scoreName, myscore))
            scoredict[totalturns] = scores[:10]
        elif len(scores) < 10 or any([myscore > score[1] for score in scores]):
            print("A new high score!!!")
            scoreName = input("Tell me your name, champion! ")
            scores.insert(0, (scoreName, myscore))
            scores.sort(key = lambda x: int(x[1]), reverse = True)
            scoredict[totalturns] = scores[:9]
    else:
        print("a new high score. You amazing muffin. I didn't know you "
                "had it in you.")
        scoreName = input("tell me your name, you champion you. ")
        scores.append((scoreName, myscore))

scorecrunch(scoredict, myscore, totalturns)

for score in scoredict[totalturns]:
    print(f"{score[0]}: {score[1]}")

# save the score
with open('GMG.dat', 'wb') as file:
    pickle.dump(scoredict, file)

input("Press any key ")

