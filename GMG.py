import math
import pickle
import random
import re

turn = 0
steep = 1
roomCount = 0

myscore = 0
################################################################################
# TODO:

# scoring!


class meep:
    def __init__(self):
        self.team = 'neutral'
        self.hp = random.randint(15, 25)

    def damage(self, amount):
        self.hp -= amount
        if self.hp <= 0:
            print("{} has died of their wounds.".format(self.name))

    def heal(self, amount):
        self.hp += amount
        print("{} has {} hit points.".format(self.name, self.hp))
        

class hero(meep):
    def __init__(self, path):
        print("With a sound like an angel clapping, a hero joins the party!")
        self.team = 'good'
        self.hp = random.randint(45, 105)
        self.path = path
        print(f"The new hero is a {self.path} of the light with {self.hp} hit " 
                f"points.")
        self.name = input("What is this hero's name? ")
        self.targets = []
        self.poison = 0

    def attack(self, target):
        if target.team != 'evil':
            print("Good meeps cannot fight meeps that are not evil.")
        else:
            amount = random.randint(2, 15)
            print("{} strikes a righteous blow against "
                    "{} for {} damage!".format(self.name, target.name, amount))
            target.damage(amount)

    def combat(self, gameRoom, party):
        if len(gameRoom.monsters) == 0:
            return
        for monster in gameRoom.monsters:
            if monster.hp <= 0:
                gameRoom.monsters.remove(monster)
                for hero in party:
                    if monster in hero.targets:
                        hero.targets.remove(monster)
        while len(self.targets) < 3 and \
                len(gameRoom.monsters) > len(self.targets):
            self.targets.append(random.choice(
                    [monster for monster in gameRoom.monsters 
                    if monster not in self.targets]))
        for monster in self.targets:
            monster.announce(self)
        target = str(input("Which one do you want to attack? "))
        if target not in [monster.name for monster in self.targets]:
            print("You missed! Type enemy names more carefully.")
            target = str(input("Which one do you want to attack? "))
            if target not in [monster.name for monster in self.targets]:
                print("You missed! Type enemy names more carefully.")
        if target in [monster.name for monster in self.targets]:
            attackee = min([monster for monster in self.targets \
                    if monster.name == target])
            self.attack(attackee)
            if attackee.hp <= 0:
                print("{} has fallen!".format(attackee.name))
                gameRoom.monsters.remove(attackee)
                for hero in party: 
                    if attackee in hero.targets:
                        hero.targets.remove(attackee)
                global myscore 
                myscore += 1

    def transition(self, party):
        if hero.poison > 0:
            hero.damage(hero.poison)
            print("The poison coursing in {}'s veins ".format(hero.name) +
                    "deals {} damage.".format(hero.poison))
            hero.poison = math.floor(hero.poison / 2)
        if hero.poison < 0:
            hero.heal(-1 * hero.poison)
            print(f"The lingering touch of nature heals {-1 * hero.poison} "
                    f"damage from {hero.name}.")
            hero.poison = math.floor(hero.poison / 2)
        if hero.hp < 0:
            if hero in party:
                party.remove(hero)
            if len(party) > 0:
                print("{} has fallen. The party mourns.".format(hero.name))
            else:
                print("The party has fallen...")

    def turn(self, gameRoom, party):
        print(" ")
        for monster in gameRoom.monsters:
            if monster.hp <= 0:
                print(f"{monster.name} has fallen!")
                gameRoom.monsters.remove(monster)
                for hero in party:
                    if monster in hero.targets:
                        hero.targets.remove(monster)
        self.combat(gameRoom, party)

################################################################################
#   HERO CLASSES
################################################################################

class barista(hero):
    def __init__(self):
        super().__init__('barista')
        self.orders = 0

    def combat(self, gameRoom, party):
        if len(gameRoom.monsters) == 0:
            return
        self.orders += 1
        while len(self.targets) < 3 and \
                len(gameRoom.monsters) > len(self.targets):
            self.targets.append(random.choice(
                    [monster for monster in gameRoom.monsters 
                    if monster not in self.targets]))
        for monster in self.targets:
            for hero in party:
                if hero != self:
                    if monster in hero.targets:
                        self.orders += 1
            monster.announce(self)
        target = str(input("Which one do you want to attack? "))
        if target not in [monster.name for monster in self.targets]:
            print("You missed! Type enemy names more carefully.")
            target = str(input("Which one do you want to attack? "))
            if target not in [monster.name for monster in self.targets]:
                print("You missed! Type enemy names more carefully.")
        if target in [monster.name for monster in self.targets]:
            attackee = min([monster for monster in self.targets \
                    if monster.name == target])
            self.attack(attackee)
            if attackee.hp <= 0:
                print("{} has fallen!".format(attackee.name))
                gameRoom.monsters.remove(attackee)
                for hero in party: 
                    if attackee in hero.targets:
                        hero.targets.remove(attackee)
                global myscore
                myscore += 1

    def damage(self, amount):
        super().damage(amount)
        if self.hp > 0 and self.orders > 0:
            for target in self.targets:
                target.damage(amount)
                print(f"{self.name} spills a hot drink on {target.name}, "
                    f"dealing {amount} damage")
            self.orders = 0

    def transition(self, party):
        super().transition(party)
        if self.hp > 0 and self.orders > 0:
            target = random.choice([hero for hero in party 
                    if hero.hp == min(hero.hp for hero in party)])
            print("{} serves a highly-customized beverage to ".format(self.name) +
                    "{}, healing {} hit points!".format(target.name, 
                    self.orders * 3))
            target.heal(self.orders * 3)
            self.orders = 0


class crusher(hero):
    def __init__(self):
        super().__init__('crusher')

    def attack(self, target):
        amount = max(math.floor(target.hp / 2), random.randint(1,4))
        if amount > 4:
            print("{} grips the monster tightly until the ".format(self.name) +
                    "monster falls apart, dealing {} damage".format(amount))
        else:
            print("{} strikes a righteous blow against "
                    "{} for {} damage!".format(self.name, target.name, amount))
        target.damage(amount)


class druid(hero):
    def __init__(self):
        super().__init__('druid')
        self.form = 'new'
        self.naturepower = 0

    def attack(self, target):
        if self.form == 'cassowary':
            bonus = math.ceil(self.naturepower / 3)
            amount = random.randint(2, 15) + bonus
            print("{} kicks {} for {} damage!".format(self.name, 
                    target.name, amount))
            target.damage(amount)
            naturepower += math.ceil(amount / 5)
        else:
            super().attack(target)

    def combat(self, gameRoom, party):
        if len(gameRoom.monsters) == 0:
            return
        if self.form == 'healer' and self.naturepower > 10:
            print("{} overflows with the benevolent power of " +
                    "creation!").format(self.name)
            target = random.choice([hero for hero in party 
                    if hero.hp <= self.hp])
            target.heal(6)
            target.poison(-2)
            self.naturepower -= 10
            return
        elif self.form == 'healer':
            super().combat(gameRoom, party)
        elif self.form == 'wolbear':
            if len(self.targets) > 3:
                self.targets = self.targets[:2]
            super().combat(gameRoom, party)
            self.targets = [monster for monster in gameRoom.monsters]
        else:
            self.savetargets = len(self.targets)
            super().combat(gameRoom, party)
            if len(self.targets) < self.savetargets:
                self.combat(gameRoom, party)
            global myscore
            myscore += 1

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
            print("{} transforms into a mighty {}.".format(self.name, 
                    self.form))
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
            print("{} transforms into a mighty {}.".format(self.name, 
                    self.form))
        super().transition(party)


class janissary(hero):
    def __init__(self):
        super().__init__('janissary')

    def combat(self, gameRoom, party):
        global myscore
        if len(gameRoom.monsters) == 0:
            return
        while len(self.targets) < 3 and len(gameRoom.monsters) > len(self.targets):
            self.targets.append(random.choice(
                    [monster for monster in gameRoom.monsters 
                    if monster not in self.targets]))
        for monster in self.targets:
            monster.announce(self)
        target = str(input("Which one do you want to attack? "))
        if target not in [monster.name for monster in self.targets]:
            print("You missed! Type enemy names more carefully.")
            target = str(input("Which one do you want to attack? "))
            if target not in [monster.name for monster in self.targets]:
                print("You missed! Type enemy names more carefully.")
        if target in [monster.name for monster in self.targets]:
            attackee = min([monster for monster in self.targets \
                    if monster.name == target])
            spirithp = attackee.hp
            self.attack(attackee)
            spirithp = spirithp - math.ceil(attackee.hp * 0.7)
            if attackee.hp <= 0:
                print("{} has fallen!".format(attackee.name))
                for hero in party:
                    if attackee in hero.targets:
                        hero.targets.remove(attackee)
                gameRoom.monsters.remove(attackee)
                
                myscore += 1
            if len(gameRoom.monsters) > 0 and spirithp > 0:
                target2 = random.choice([monster 
                        for monster in gameRoom.monsters])
                print("A spirit force deals {} damage to {}".format(spirithp, 
                        target2.name))
                target2.damage(spirithp)
                if target2.hp <= 0:
                    print("{} has fallen!".format(target2.name))
                    for hero in party:
                        if target2 in hero.targets:
                            hero.targets.remove(target2)
                    if target2 in gameRoom.monsters:
                        gameRoom.monsters.remove(target2)
                    
                    myscore += 1


class paladin(hero):
    def __init__(self):
        super().__init__('paladin')
        self.weapon = random.choice(['mace', 'sword', 'fork', 'mug', 
                'claymore'])
        print("{} wields a holy {}, blessed by God himself.".format(self.name,
                self.weapon))

    def attack(self, target):
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


class priest(hero):
    def __init__(self):
        super().__init__('priest')
        self.faith = 3

    def turn(self, gameRoom, party):
        print(" ")
        do = str(input("Do you want {} to Pray? ".format(self.name)))
        if do in ("Pray", "pray", "P", "Y", "Yes", "yes"):
            self.targets = []
            self.faith += 1
            print("{}'s faith is strengthened to {}.".format(self.name,
                    self.faith))
        else: 
            print("{} channels the light to heal the party ".format(self.name) +
                    "for {} hit points!".format(self.faith))
            for hero in party:
                hero.heal(self.faith)
            self.combat(gameRoom, party)

################################################################################

class monster(meep):
    def __init__(self, path):
        print("A monster appears!")
        super().__init__()
        self.path = path
        self.team = 'evil'
        self.name = None

    def announce(self, hero):
        print("{} faces a {} named {} with {} hp.".format(hero.name, 
                self.path, self.name, self.hp))

    def attack(self, target):
        amount = random.randint(1,8)
        print("{} attacks {} for {} damage!".format(self.name, 
                target.name, amount))
        target.damage(amount)

    def doLeftAlone(self, gameRoom, party):
        pass

    def turn(self, gameRoom, party):
        print(" ")
        targetList = [hero for hero in party if self in hero.targets]
        if self.hp <= 0:
            for hero in party:
                if self in hero.targets:
                    hero.targets.remove(self)
            if self in gameRoom.monsters:
                gameRoom.monsters.remove(self)
            return
        if any(targetList):
            target = random.choice([hero for hero in party 
                    if self in hero.targets])
            monster.attack(target)
            if target.hp < 0:
                if target in party:
                    party.remove(target)
                if len(party) > 0:
                    print("{} has fallen. The party mourns.".format(target.name))
                else:
                    print("The party has fallen...")
        else:
            monster.doLeftAlone(gameRoom, party)

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
        amount = random.randint(2,5)
        for monster in gameRoom.monsters:
            monster.heal(amount)
            self.damage(amount)
        print("{} sacrifices its health to heal the monsters ".format(self.name) +
                "for {} hit points.".format(amount))
        if self.hp < 0:
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
        print("{} takes 1 damage from the sheer pain of ".format(hero.name) +
                "of looking at {}.".format(self.name))
        hero.damage(1)

    def doLeftAlone(self, gameRoom, party):
        print("{} sits alone in the dark, ignored by ".format(self.name) +
                "everyone. Which is how it should be.")


class dragonstork(monster):
    def __init__(self):
        super().__init__('dragonstork')
        self.deepbreath = 1

    def attack(self, target):
        amount = random.randint(1,4) * self.deepbreath
        print("{} is burned for {} damage!".format(target.name, amount))
        target.damage(amount)

    def doLeftAlone(self, gameRoom, party):
        print("{} takes a deep breath!")
        self.deepbreath += 1

    def turn(self, gameRoom, party):
        print(" ")
        targetList = [hero for hero in party if self in hero.targets]
        if self.hp <= 0:
            for hero in party:
                if self in hero.targets:
                    hero.targets.remove(self)
            if self in gameRoom.monsters:
                gameRoom.monsters.remove(self)
            return
        if any(targetList):
            print("{} breathes out fire!".format(self.name))
            for target in targetList:
                monster.attack(target)
                if target.hp < 0:
                    party.remove(target)
                    if len(party) > 0:
                        print("{} has fallen. The party mourns.".format(target.name))
                    else:
                        print("The party has fallen...")
            self.deepbreath = 1
        else:
            monster.doLeftAlone(gameRoom, party)


class orc(monster):
    def __init__(self):
        super().__init__('orc')

    def attack(self, target):
        if self.hp > 7:
            super().attack(target)
        else:
            amount = random.randint(1, 12)
            target.damage(amount)
            print("{} screams in bestial rage and slices ".format(self.name) +
                    "{} for {} damage.".format(hero.name, amount))
            if target.hp < 0:
                party.remove(target)
                if len(party) > 0:
                    print("{} has fallen. The party mourns.".format(target.name))
                else:
                    print("The party has fallen...")


    def doLeftAlone(self, gameRoom, party):
        target = random.choice([hero for hero in party 
                if len(hero.targets) == 
                max([len(hero.targets) for hero in party])])
        target.targets.append(self)
        print("{} charges into battle against {}!".format(self.name, 
                target.name))
        self.attack(target)
        if target.hp < 0:
            party.remove(target)
            if len(party) > 0:
                print("{} has fallen. The party mourns.".format(target.name))
            else:
                print("The party has fallen...")


class reject(monster):
    def __init__(self):
        super().__init__('reject')

    def attack(self, target):
        super().attack(target)
        if self in target.targets:
            target.targets.remove(self)

    def doLeftAlone(self, gameRoom, party):
        target = random.choice([hero for hero in party])
        print("{} sneaks up behind {}...".format(self.name, target.name))
        self.attack(target)
        self.attack(target)
        self.attack(target)
        if target.hp < 0:
            party.remove(target)
            if len(party) > 0:
                print("{} has fallen. The party mourns.".format(target.name))
            else:
                print("The party has fallen...")


class spider(monster):
    def __init__(self):
        super().__init__('spider')

    def attack(self, target):
        super().attack(target)
        if random.randint(1,3) == 1:
            target.poison += 1
            print("{} doesn't feel so good.".format(target.name))

    def doLeftAlone(self, gameRoom, party):
        print("{} sprays a green ichor from its jaws!".format(self.name))
        for hero in party:
            amount = random.randint(0,3)
            if amount != 0:
                target.poison += amount
                print("{} really doesn't feel good.".format(target.name))


class teaspirit(monster):
    def __init__(self):
        super().__init__('tea spirit')
        self.brew = 1

    def attack(self, target):
        global steep
        amount = math.floor(random.randint(1,8) * (1 + (steep / 10)))
        if self.name == "The Iron Maiden of Mercy":
            print("{} heals {} for {} hit points, ".format(self.name, 
                    target.name, amount) + "but will exact a terrible price "
                    "later.")
            target.heal(amount)
            target.poison += math.ceil(amount * 1.5)
        else:
            target.damage(amount)
            print("{} attacks {} for {} damage!".format(self.name, 
                    target.name, amount))

    def doLeftAlone(self, gameRoom, party):
        global steep
        roll = random.randint(1, 3)
        if roll == 1:
            print("{} brews up a new monster!".format(self.name))
            self.brew *= 2
            new = newmonster(gameRoom.monsters)
            new.hp = math.ceil(new.hp / self.brew) + steep
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
        global steep
        print(" ")
        targetList = [hero for hero in party if self in hero.targets]
        if self.hp <= 0:
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
                        print("{} has fallen. The party mourns.".format(target.name))
                    else:
                        print("The party has fallen...")
            elif roll == 1:
                print("{} brews up a new monster!".format(self.name))
                self.brew *= 2
                new = newmonster(gameRoom.monsters)
                new.hp = math.ceil(new.hp / self.brew) + steep
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
        self.shell = 0

    def damage(self, amount):
        if self.shell == 1:
            print("{}'s shell absorbs the damage!".format(self.name))
        else:
            super().damage(amount)
            self.shell = 1
            print("{} recedes into its shell".format(self.name))

    def doLeftAlone(self, gameRoom, party):
        if self.shell == 0:
            print("Despite near-safety, {} recedes back into ".format(self.name) +
                    "its shell")
            self.shell = 1

    def turn(self, gameRoom, party):
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
                "Draco", "Lili", "Dental", "Spike", "Tia", "Yssie", "Alie", "Noz")
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
        self.size = random.choice(['cramped', 'huge', 'small', 'low-roofed'])
        self.desc = random.choice(['well-lit', 'smelly', 'blue', 'dark',
                'empty'])
        print("You stand in a {}, {} room.".format(self.size, self.desc))
        self.monsters = []
        if self.desc != 'empty':
            #right now, there's a 33% chance of an empty room anyhow
            self.monstercount = random.choice([0, 
                    random.randint(len(party), len(party)* 2), 
                    random.randint(len(party), len(party)* 2)])
            for m in range(self.monstercount):
                self.monsters.append(newmonster(self.monsters))
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
for hero in party:
    hero.transition(party)
while turn <= totalturns and len(party) > 0:
    if turn == totalturns:
        print("IT IS THE LAST TURN!!!2!")
    if len(gameRoom.monsters) == 0:
        print("This room is empty! Time to go to a new room!")
        if myscore > 0:
            print("Your current score is {}!".format(myscore))
        print(" ")
        for hero in party:
            hero.transition(party)
        roomCount += 1
        gameRoom = room(party)
        if roomCount % 5 == 0:
            party.append(recruit())
    else:
        for hero in party:
            hero.turn(gameRoom, party)
        for monster in gameRoom.monsters:
            monster.turn(gameRoom, party)
        herohp = sum([hero.hp for hero in party])
        if herohp < 200:
            myscore += math.ceil(
                    sum([monster.hp for monster in gameRoom.monsters]) *
                    (1 + ((200 - herohp) / 100)) *
                    turn / totalturns)
        else:
            myscore += math.ceil(
                    sum([monster.hp for monster in gameRoom.monsters]) *
                    (math.floor(200 / sum([hero.hp for hero in party]))) *
                    turn / totalturns)
    turn += 1
if len(gameRoom.monsters) == 0:
    print("{} stands, panting, over the prone ".format(party[0].name) +
            "body of the last monster. {} is ".format(party[0].name) +
            "victorious!")
elif len(party) == 0:
    print("The story closes on a bitter note.")
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
            scores = scores[:10]
        elif any([myscore > score[1] for score in scores]):
            print("A new high score!!!")
            scoreName = input("Tell me your name, champion! ")
            scores.insert(0, (scoreName, myscore))
            scores.sort(key = lambda x: int(x[1]), reverse = True)
            scores = scores[:10]
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

