# GitHub Copilot Instructions

## Project Overview

This project is a Flask-based Sudoku game. The goal is to refactor the legacy
application into a clean, maintainable, responsive, and accessible Sudoku game
with modern functionality.

## Code Quality

Use clear, readable, and maintainable Python code.
Follow PEP 8 conventions.
Use descriptive names for variables, functions, classes, and files.
Keep functions focused on one responsibility.
Avoid unnecessary duplication.
Prefer modular and reusable components.
Add comments only when they explain non-obvious logic.
Use consistent error handling.
Do not introduce unnecessary dependencies.

## Project Structure

Keep application logic separated into logical components:

Flask routes and request handling
Sudoku generation and solving logic
Game validation
Scoreboard and persistence
Frontend templates
CSS styling
JavaScript interactivity
Automated tests

## Sudoku Requirements

Generate valid 9x9 Sudoku puzzles.
Every generated puzzle must have exactly one unique solution.
Support Easy, Medium, and Hard difficulty levels.
Difficulty should control the number of prefilled cells.
Prefilled cells must be locked.
Invalid entries should provide immediate visual feedback.
A completed valid puzzle should display a congratulatory message.

## Game Features

Implement:

Timer
Check button
Hint button
Dark mode toggle
Top 10 leaderboard
Player name
Completion time
Difficulty level
Number of hints used
Persistent leaderboard storage using browser localStorage

The Hint button must fill one correct empty cell and lock that cell.

The Check button must identify incorrect user entries without incorrectly
marking empty cells as wrong.

## Frontend and Accessibility

Support desktop and mobile screen sizes.
Use responsive layouts.
Use alternating visual styling for the 3x3 Sudoku boxes.
Ensure text and controls are readable in light and dark modes.
Use semantic HTML where possible.
Ensure buttons and form controls are keyboard accessible.
Maintain sufficient color contrast.

## Testing

Run tests before and after major changes.
Do not remove existing tests without a valid reason.
Add tests for important Sudoku logic where appropriate.
Confirm that the application still runs after each major change.

## GitHub Copilot Usage

Use Copilot as an assistant, not as an unquestioned source of truth.

Before accepting generated code:

1. Understand what the code does.
2. Check that it follows the project requirements.
3. Check for unnecessary complexity.
4. Test the code.
5. Reject or modify suggestions that do not fit the project.

When making large changes, prefer planning and reviewing the approach before
implementing it.

Use focused prompts for individual tasks and keep Copilot conversations
organized by milestone.

## Important Development Principle

Preserve working functionality while adding new features. Make changes
incrementally, test frequently, and keep the codebase stable throughout
development.