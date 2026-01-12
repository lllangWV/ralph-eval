# General Task Guidelines
- Always make a todo list on how to complete the task before starting.
- The todo list should start with creating tests for a new behavior, bug fix, or feature.
- Keep iterating until all the tests are passing. This should be module specific, do not worry about tests in other unrelated modules.

# Development and Testing Guidelines
- Install deps: `pixi install -e dev`
- To run in environment shell: `pixi shell -e dev`
- To run in terminal: `pixi run -e dev`
- Run tests on single testing files and not the full test suite. example: `pixi run -e tests pytest tests/pyprocar/core/test_dos.py`
- Use generated test data for testing.
- These should be testing different execution paths of a layer. They should be contained within a single function with an appropriate name. 
- Prefer a single assert per test.
- create new test files in the `tests/` directory. 

# Code Style Conventions
- Variable and function names must be snake_case
- Class names must be PascalCase
- Use type hints.
- If there are any packages with missing type stubs, create the type stubs for them.
- Prefer to use guard clauses for early returns and error handling.
- Do not use nested functions.


# Logging Conventions
- Loggers should be accessed by their name. example: `logging.getLogger(__name__)`
- Use user logger `logging.getLogger("user")` for user facing messages.
- Use info level for initialization and completion messages.
- Use debug level to get more detailed information such as array shapes, float, string, int values.
- Never return array values in logs, return the array shape instead.
- Use warning level for warnings.
- Use error level for errors.
- Use critical level for critical errors.
- When adding logs, prefer to add them at the start and end of a functions.

# Security
- Do NOT commit `.env` file
