import random
import string

from stats import SessionStats
from words import WORDS, HINTS

# name -> (lives, score multiplier, points lost when the hint is used)
DIFFICULTIES = {
    "easy": {"lives": 8, "multiplier": 1, "hint_cost": 2},
    "medium": {"lives": 6, "multiplier": 2, "hint_cost": 4},
    "hard": {"lives": 4, "multiplier": 3, "hint_cost": 6},
}
DEFAULT_DIFFICULTY = "medium"
BASE_POINTS = 5


class QuitGame(Exception):
    """Raised when the player quits (/quit, q, Ctrl+C or end of input)."""


class HangmanGame:
    def __init__(self, input_func=input, rng=None):
        self._input = input_func
        self._rng = rng or random.Random()
        # Session state: survives across rounds.
        self.score = 0
        self.streak = 0
        self.stats = SessionStats()
        self.category = None
        self.difficulty = DEFAULT_DIFFICULTY
        # Round state: reset by start_round().
        self.secret = ""
        self.guessed = set()
        self.wrong = set()
        self.lives = DIFFICULTIES[self.difficulty]["lives"]
        self.hint_used = False

    # ------------------------------------------------------------ input
    def ask(self, prompt):
        """Read one line, normalised. Ctrl+C / Ctrl+D quit the game."""
        try:
            return self._input(prompt).strip().lower()
        except (EOFError, KeyboardInterrupt):
            print()
            raise QuitGame from None

    # ------------------------------------------------------------ round
    @property
    def rules(self):
        return DIFFICULTIES[self.difficulty]

    def start_round(self):
        """Reset only round-specific state."""
        self.secret = self._rng.choice(WORDS[self.category])
        self.guessed = set()
        self.wrong = set()
        self.lives = self.rules["lives"]
        self.hint_used = False

    def masked(self):
        return " ".join(ch if ch in self.guessed else "_" for ch in self.secret)

    def won(self):
        return all(ch in self.guessed for ch in set(self.secret))

    def guess(self, letter):
        """Apply one guess. Returns the feedback message.

        Each distinct letter changes the round at most once; invalid or
        repeated input never changes state.
        """
        if len(letter) != 1 or letter not in string.ascii_lowercase:
            return "Please enter exactly one letter from a to z."
        if letter in self.guessed or letter in self.wrong:
            return f"You already guessed '{letter}'. No life lost."
        if letter in self.secret:
            self.guessed.add(letter)
            count = self.secret.count(letter)
            return f"Correct! '{letter}' appears {count} time(s)."
        self.wrong.add(letter)
        self.lives -= 1
        return f"Wrong. '{letter}' is not in the word. {self.lives} lives left."

    def use_hint(self):
        """Reveal the hint. The penalty is applied once, at the end of a won round."""
        hint = HINTS.get(self.secret, "No hint available.")
        if self.hint_used:
            return f"Hint (already used, no extra cost): {hint}"
        self.hint_used = True
        return f"Hint (-{self.rules['hint_cost']} points if you win): {hint}"

    def round_points(self):
        """Points for a won round: base + streak + lives left, times multiplier,
        minus the hint cost. Never negative."""
        points = (BASE_POINTS + self.streak + self.lives) * self.rules["multiplier"]
        if self.hint_used:
            points -= self.rules["hint_cost"]
        return max(0, points)

    def show_status(self):
        print("\nWord:  ", self.masked())
        print("Wrong: ", " ".join(sorted(self.wrong)) or "-")
        print(f"Lives: {self.lives}   Score: {self.score}   Streak: {self.streak}"
              f"   [{self.category}, {self.difficulty}]")

    def play_round(self):
        """Play one round. Returns False if the player quit mid-round."""
        self.start_round()
        print(f"\nNew {self.difficulty} round in '{self.category}': "
              f"{len(self.secret)} letters, {self.lives} lives.")
        while self.lives > 0 and not self.won():
            self.show_status()
            raw = self.ask("Letter, /hint, /help or /quit: ")
            if not raw:
                print("Please type a letter or a command.")
            elif raw == "/quit":
                print("Round abandoned (not counted).")
                return False
            elif raw == "/hint":
                print(self.use_hint())
            elif raw == "/help":
                print("Type one letter to guess it. /hint shows a clue "
                      f"(costs {self.rules['hint_cost']} points if you win). "
                      "/quit ends the session.")
            elif raw.startswith("/"):
                print(f"Unknown command '{raw}'. Try /hint, /help or /quit.")
            else:
                print(self.guess(raw))

        if self.won():
            self.streak += 1
            points = self.round_points()
            self.score += points
            self.stats.record(True, self.streak)
            print(f"\nSolved: {self.secret}  (+{points} points)")
        else:
            self.streak = 0
            self.stats.record(False, self.streak)
            print(f"\nOut of lives. The word was: {self.secret}")
        return True

    # ------------------------------------------------------------ session
    def choose_category(self):
        names = list(WORDS)
        menu = "  ".join(f"{i}) {name}" for i, name in enumerate(names, 1))
        keep = f" (Enter = {self.category})" if self.category else ""
        while True:
            print("\nCategories:", menu)
            raw = self.ask(f"Choose category{keep}, or q to quit: ")
            if raw in ("q", "/quit"):
                raise QuitGame
            if not raw and self.category:
                return self.category
            if raw.isdigit() and 1 <= int(raw) <= len(names):
                return names[int(raw) - 1]
            if raw in WORDS:
                return raw
            print(f"'{raw}' is not a valid category." if raw else "Please choose a category.")

    def choose_difficulty(self):
        names = list(DIFFICULTIES)
        menu = "  ".join(
            f"{i}) {n} ({d['lives']} lives, x{d['multiplier']})"
            for i, n in enumerate(names, 1) for d in [DIFFICULTIES[n]])
        while True:
            print("Difficulty:", menu)
            raw = self.ask(f"Choose difficulty (Enter = {self.difficulty}): ")
            if raw in ("q", "/quit"):
                raise QuitGame
            if not raw:
                return self.difficulty
            if raw.isdigit() and 1 <= int(raw) <= len(names):
                return names[int(raw) - 1]
            for name in names:
                if raw in (name, name[0]):
                    return name
            print(f"'{raw}' is not a valid difficulty.")

    def ask_again(self):
        while True:
            raw = self.ask("Another round? [y/n]: ")
            if raw in ("y", "yes"):
                return True
            if raw in ("n", "no", "q", "/quit"):
                return False
            print("Please answer y or n.")

    def print_summary(self):
        print("\nSession over.")
        print("Rounds played:", self.stats.rounds, " Rounds won:", self.stats.wins)
        print("Best streak:", self.stats.best_streak, " Final score:", self.score)

    def run(self):
        print("Hangman Challenge")
        print("A session consists of multiple rounds.")
        try:
            while True:
                self.category = self.choose_category()
                self.difficulty = self.choose_difficulty()
                if not self.play_round() or not self.ask_again():
                    break
        except QuitGame:
            pass
        self.print_summary()
