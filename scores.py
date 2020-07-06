import json
import time

PLAYER_NAMES = ["Niels", "Dirk", "Alewijn", "Scott", "Jan Hein", "Ruben", "Roeland"]

class Game: 

    TOTAL_POINTS = 0
    TOTAL_PLAYED = 0
    TOTAL_DURATION = 0

    def __init__(self, name, players, duration, scores):
        if len(scores) != len(players): 
            raise Exception
        for player in players: 
            if player not in PLAYER_NAMES: 
                raise Exception
        if duration <= 45:
            if sum(scores) != 1: 
                raise Exception
        elif duration <= 90:
            if sum(scores) != 2: 
                raise Exception
        elif duration <= 180: 
            if sum(scores) != 3:
                raise Exception
        else:
            if sum(scores) != 4: 
                raise Exception
        self.name = name 
        self.duration = duration
        self.players = players 
        self.scores = scores
        Game.TOTAL_PLAYED += 1
        Game.TOTAL_POINTS += self.points
        Game.TOTAL_DURATION += self.duration
        
    @property
    def points(self):
        return sum(self.scores)

    def player_points(self, name):
        return self.scores[self.players.index(name)]

    @classmethod
    def from_dict(cls, game):
        return cls(**game)


class Player: 

    def __init__(self, name):
        self.name = name
        self.games = []

    @property 
    def score(self):
        try: 
            return 50 * (self.total_won / self.total_played) + 50 * (self.total_played / Game.TOTAL_POINTS)
        except ZeroDivisionError: 
            return 0

    def add_game(self, game: Game): 
        if self.name in game.players: 
            # self.total_won += game.player_score(self.name)
            # self.total_played += game.points
            self.games.append(game)
    
    @property 
    def total_won(self):
        return sum([game.player_points(self.name) for game in self.games])

    @property
    def total_played(self):
        return sum([game.points for game in self.games])

    def __str__(self):
        return f"Player {self.name} has a score of {self.score:.2f} and participated in {len(self.games)} games"

    def __lt__(self, other): 
        if self.score < other.score:
            return True 
        else: 
            return False

# Create players
players = [Player(name) for name in PLAYER_NAMES]

# Read games
with open('scores.json') as f:
    games = [Game.from_dict(game) for game in json.load(f)]
    
# Add games to players
for game in games:
    for player in players: 
        player.add_game(game)
players.sort()

# Print output
print("Allright... here we go!!\n")

print(
    f"Total number of games played is {Game.TOTAL_PLAYED}, " 
    f"with a duration of {Game.TOTAL_DURATION} minutes, "
    f"and a total of {Game.TOTAL_POINTS:.0f} points to be earned..."
)

time.sleep(3)

print("\nAnd now for the individual scores...\n")

time.sleep(2)
for player in players[:-1]: 
    print(player)
    time.sleep(2)

print(f"\nAnd with a score of {players[-1].score:.2f}, the leader is... *DRUMROLL*\n")
time.sleep(3)
print(players[-1].name.upper() + "!!!!")
print()