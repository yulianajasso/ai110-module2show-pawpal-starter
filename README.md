# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample Output

Run `python main.py` to see a demo schedule in the terminal:

```
====================================================
  PawPal+ — Daily Schedule for Alex
====================================================
Daily plan for Alex:

  08:00 — 08:10  Feeding (Biscuit, 10 min, priority: high)
  08:10 — 08:20  Feeding (Luna, 10 min, priority: high)
  08:20 — 08:30  Litter box (Luna, 10 min, priority: high)
  08:30 — 09:00  Morning walk (Biscuit, 30 min, priority: high)
  09:00 — 09:15  Brush coat (Luna, 15 min, priority: medium)
  09:15 — 09:30  Enrichment toy (Biscuit, 15 min, priority: medium)

Skipped tasks:
  - Grooming (Biscuit): not enough time remaining
  - Vet check (Luna): not enough time remaining
====================================================
  Time used:      90 / 90 min
  Tasks scheduled: 6
  Tasks skipped:   2
====================================================
```

## 🧪 Testing PawPal+

```bash
# Run the full test suite:
python -m pytest tests/test_pawpal.py -v

# Run with coverage:
python -m pytest --cov
```

Sample test output:

```
============================= test session starts ==============================
platform darwin -- Python 3.13.1, pytest-9.1.1, pluggy-1.6.0
rootdir: /Users/yuli/Desktop/ai110-module2show-pawpal-starter-1
collecting ... collected 3 items

tests/test_pawpal.py::test_mark_complete_changes_status PASSED           [ 33%]
tests/test_pawpal.py::test_mark_complete_sets_last_completed PASSED      [ 66%]
tests/test_pawpal.py::test_add_task_increases_pet_task_count PASSED      [100%]

============================== 3 passed in 0.01s ===============================
```

## 📐 Smarter Scheduling

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Scheduler.generate_plan()`, `Scheduler.sort_by_time()` | `generate_plan()` sorts candidates by priority → duration → name before assigning slots. `sort_by_time()` re-sorts the finished schedule by HH:MM start time for display. |
| Filtering | `Scheduler.filter_by_pet(pet_name)`, `Owner.get_tasks_for_pet(pet_name)`, `Owner.get_incomplete_tasks()` | Filter the generated schedule to one pet's slots, or query all tasks by pet name or completion status. |
| Conflict handling | `Scheduler.detect_conflicts()`, `Scheduler.force_schedule()` | `detect_conflicts()` checks every slot pair for overlapping time windows using the standard interval condition; returns warning strings instead of raising. `force_schedule()` bypasses normal scheduling to inject a task at a fixed time (used for testing). |
| Recurring tasks | `Task.is_due_today()`, `Task.mark_complete()` | `mark_complete()` uses `timedelta` to compute `next_due`: +1 day for daily, +7 days for weekly, `None` for as-needed. `is_due_today()` uses `next_due` as the primary gate when set. |

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
