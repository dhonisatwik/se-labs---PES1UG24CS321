"""Tests for the Hangman game. Run with:  python -m unittest -v"""
import contextlib
import io
import random
import unittest

from game import HangmanGame, DIFFICULTIES


def scripted(lines):
    it = iter(lines)

    def fake_input(_prompt):
        try:
            return next(it)
        except StopIteration:
            raise EOFError from None
    return fake_input


def new_game(secret="python", difficulty="medium", lines=()):
    game = HangmanGame(input_func=scripted(lines))
    game.category = "technology"
    game.difficulty = difficulty
    game.start_round()
    game.secret = secret
    return game


def run_session(lines, seed=0):
    game = HangmanGame(input_func=scripted(lines), rng=random.Random(seed))
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        game.run()
    return game, out.getvalue()


class GuessState(unittest.TestCase):
    def test_repeated_wrong_letter_costs_one_life(self):
        g = new_game()
        g.guess("z")
        g.guess("z")
        g.guess("z")
        self.assertEqual(g.lives, DIFFICULTIES["medium"]["lives"] - 1)
        self.assertEqual(g.wrong, {"z"})

    def test_repeated_correct_letter_counted_once(self):
        g = new_game()
        g.guess("p")
        before = (set(g.guessed), set(g.wrong), g.lives)
        msg = g.guess("p")
        self.assertIn("already", msg)
        self.assertEqual(before, (g.guessed, g.wrong, g.lives))

    def test_invalid_input_never_changes_state(self):
        g = new_game()
        for bad in ["", "ab", "1", "?", " ", "é", "py"]:
            g.guess(bad)
        self.assertEqual((g.guessed, g.wrong), (set(), set()))
        self.assertEqual(g.lives, DIFFICULTIES["medium"]["lives"])


class Scoring(unittest.TestCase):
    def test_difficulty_sets_lives(self):
        for name, rules in DIFFICULTIES.items():
            self.assertEqual(new_game(difficulty=name).lives, rules["lives"])

    def test_hint_cost_applied_once(self):
        g = new_game()
        clean = g.round_points()
        g.use_hint()
        g.use_hint()
        self.assertTrue(g.hint_used)
        self.assertEqual(g.round_points(),
                         clean - DIFFICULTIES["medium"]["hint_cost"])

    def test_hint_does_not_change_score_immediately(self):
        g = new_game()
        g.score = 0
        g.use_hint()
        self.assertEqual(g.score, 0)

    def test_harder_difficulty_scores_more(self):
        pts = [new_game(difficulty=d).round_points() for d in ("easy", "medium", "hard")]
        self.assertEqual(pts, sorted(pts))


class Session(unittest.TestCase):
    def solve_lines(self, word):
        return list(dict.fromkeys(word))

    def test_multiple_rounds_stats_and_streak(self):
        rng = random.Random(0)
        first = rng.choice(["python", "compiler", "database", "algorithm", "network"])
        # Round 1: win. Round 2: lose (6 wrong letters). Round 3: quit at menu.
        lines = ["1", "", *self.solve_lines(first), "y",
                 "", "", *"qjxzvf", "y", "q"]
        game, out = run_session(lines, seed=0)
        self.assertEqual(game.stats.rounds, 2)
        self.assertEqual(game.stats.wins, 1)
        self.assertEqual(game.stats.best_streak, 1)
        self.assertEqual(game.streak, 0)
        self.assertIn("Rounds played: 2", out)

    def test_category_and_difficulty_preserved(self):
        lines = ["2", "hard", "/quit"]
        game, _ = run_session(lines)
        self.assertEqual((game.category, game.difficulty), ("science", "hard"))

    def test_new_round_resets_only_round_state(self):
        g = new_game()
        g.guess("z")
        g.use_hint()
        g.score, g.streak = 10, 2
        g.difficulty = "easy"
        g.start_round()
        self.assertEqual((g.wrong, g.guessed, g.hint_used), (set(), set(), False))
        self.assertEqual(g.lives, DIFFICULTIES["easy"]["lives"])
        self.assertEqual((g.score, g.streak), (10, 2))

    def test_invalid_menu_input_and_commands(self):
        lines = ["", "banana", "9", "1", "x", "", "  ", "/foo", "abc", "/hint",
                 "/hint", "maybe", "/quit"]
        game, out = run_session(lines)
        self.assertIn("'banana' is not a valid category", out)
        self.assertIn("'x' is not a valid difficulty", out)
        self.assertIn("Unknown command '/foo'", out)
        self.assertEqual(out.count("already used, no extra cost"), 1)
        self.assertEqual(game.stats.rounds, 0)

    def test_quit_and_eof(self):
        _, out = run_session(["q"])
        self.assertIn("Session over.", out)
        _, out = run_session([])  # Ctrl+D / end of input
        self.assertIn("Session over.", out)


if __name__ == "__main__":
    unittest.main()
