# Lab 4 – Hangman changes (PES1UG24CS321)

## Task 1 – Guess-state correctness
**Bug reproduced:** guessing the same wrong letter (e.g. `z`) four times cost 4 lives.
`guess()` only checked `self.guessed` (correct letters), not `self.wrong`.
**Fix:** a letter already in `guessed` *or* `wrong` returns "You already guessed 'x'. No life lost." and changes nothing.

## Task 2 – Session model
`SessionStats` (from `stats.py`) is now used. Every finished round calls `stats.record(won, streak)`, which tracks rounds played, rounds won and best streak.
`start_round()` resets only round state: word, guessed/wrong letters, lives and the hint flag. Score, streak and stats carry on across the session.
A round abandoned with `/quit` is not counted. A summary is printed on every way out.

## Task 3 – Difficulty and scoring
| Difficulty | Lives | Multiplier | Hint cost |
|---|---|---|---|
| easy | 8 | x1 | 2 |
| medium (default) | 6 | x2 | 4 |
| hard | 4 | x3 | 6 |

Won round: `points = (5 + streak + lives_left) * multiplier - hint_cost (if used)`, never below 0. A lost round scores 0.
The hint penalty is applied once, at the end of the round. Before, it was taken from the total straight away and was free when the score was 0.
Category and difficulty are remembered; press Enter to keep the previous choice.

## Task 4 – Robust input and feedback
- Category and difficulty can be picked by number, by name or (for difficulty) by first letter. Invalid choices are re-asked.
- Empty input, several letters, digits, symbols and non-ASCII letters are rejected without changing state.
- `/hint`, `/help` and `/quit` work. Unknown `/commands` get a clear message. A second `/hint` shows the hint again at no extra cost.
- "Another round?" accepts y/yes/n/no and re-asks otherwise.
- Ctrl+C / Ctrl+D quit cleanly with the session summary.

## Testing
`python -m unittest -v` runs 12 tests. They cover repeated correct and wrong guesses, hints, category and difficulty changes, several rounds, streak resets, invalid input and quitting.
Only the standard library is used, and all state stays in memory.
