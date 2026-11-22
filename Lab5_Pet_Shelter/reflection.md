# Lab 5 – Reflection

**SRN:** PES1UG24CS321

### 1. Which issues were the easiest to fix, and which were the hardest? Why?

The easiest were the style issues: long lines, the one-line `if ... : return`, missing docstrings and the camelCase function names. Each one is local and the tool says exactly what to change.

The hardest was the global `adoption_count`. Pylint only says "using the global statement", but removing it made me look at what the counter meant. It also went up when `adopt()` got an id that did not exist, or a pet that was already adopted. The fix was to work the count out from the database and have `adopt()` report whether it changed anything. That needed thinking about the program's logic, not just the line Pylint flagged.

### 2. Did the static analysis tools report any false positives? If so, describe one example.

There were no real false positives, but some warnings are about context. Bandit's B311 (`random` is not cryptographically safe) is only a real problem if the value has to be hard to guess. For a demo it could be a false positive. Adoption codes may be used to claim a pet, though, so switching to `secrets` was cheap and sensible. Pylint's "constant should be UPPER_CASE" for `adoption_count` was also misleading: the value was not a constant at all. The real issue was the mutable global.

### 3. How would you integrate static analysis tools into your actual software development workflow?

- Run Flake8 and Pylint in the editor and as a **pre-commit hook**, so style problems never reach a commit.
- Run all three tools in **CI** (e.g. a GitHub Actions job) on every push and pull request. Fail the build on any Bandit Medium/High finding, any Flake8 error, or a Pylint score below a set threshold such as 9.5.
- Keep a shared config (`.pylintrc`, `setup.cfg`/`.flake8`, `bandit.yaml`) in the repo so everyone gets the same rules. Where a warning is truly not relevant, suppress it with a commented `# nosec` or `# pylint: disable=` rather than ignoring the report.

### 4. What tangible improvements did you observe in the code quality, readability, or potential robustness after applying the fixes?

- **Security:** the SQL injection is gone because of the parameterised query. A pet name with a quote (e.g. `O'Malley`) also no longer crashes the program.
- **Correctness:** tags no longer leak between calls. The adoption count is always right. Errors are no longer silently swallowed. Writes are committed.
- **Readability:** consistent snake_case names, a docstring on every function and short lines make the file much easier to scan.
- **Reusability:** the module can be imported without running the demo.
- **Measured:** Pylint went from 3.95 to 10.00, and Bandit and Flake8 went from 3 and 5 findings to 0. The program prints the same output as before.
