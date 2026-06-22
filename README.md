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

### How to run

```bash
# Run the full test suite:
python -m pytest tests/test_pawpal.py -v
```

### What the tests cover

23 automated tests across 6 areas:

| Area | What's verified |
|------|----------------|
| **Recurrence logic** | Daily tasks are due every day; weekly tasks become due again after 7 days; `mark_complete()` sets `next_due` correctly via `timedelta` |
| **Task completion** | `mark_complete()` flips `completed_today`, records `last_completed`, computes `next_due` for daily/weekly, leaves `next_due` as `None` for as-needed |
| **Pet management** | Adding/removing tasks updates the count; a pet with no tasks returns an empty due list |
| **Priority ordering** | High-priority tasks are scheduled before low; when priority ties, shorter tasks come first |
| **Time budget** | Tasks that exactly fit are scheduled; tasks 1 minute over are skipped; zero available time skips everything; no pets produces an empty schedule |
| **Sorting & filtering** | `sort_by_time()` returns chronological order; `filter_by_pet()` isolates one pet's slots; unknown pet name returns empty list |
| **Conflict detection** | A clean sequential schedule has no conflicts; a force-scheduled overlap triggers a warning; adjacent (touching) slots do not count as conflicts |

### Test output

```
============================= test session starts ==============================
platform darwin -- Python 3.13.1, pytest-9.1.1, pluggy-1.6.0
rootdir: /Users/yuli/Desktop/ai110-module2show-pawpal-starter-1
collecting ... collected 23 items

tests/test_pawpal.py::test_mark_complete_changes_status PASSED           [  4%]
tests/test_pawpal.py::test_mark_complete_sets_last_completed PASSED      [  8%]
tests/test_pawpal.py::test_daily_task_next_due_is_tomorrow PASSED        [ 13%]
tests/test_pawpal.py::test_weekly_task_next_due_is_seven_days PASSED     [ 17%]
tests/test_pawpal.py::test_completed_daily_task_not_due_today PASSED     [ 21%]
tests/test_pawpal.py::test_as_needed_task_has_no_next_due PASSED         [ 26%]
tests/test_pawpal.py::test_weekly_task_not_due_before_seven_days PASSED  [ 30%]
tests/test_pawpal.py::test_weekly_task_due_after_seven_days PASSED       [ 34%]
tests/test_pawpal.py::test_add_task_increases_pet_task_count PASSED      [ 39%]
tests/test_pawpal.py::test_pet_with_no_tasks_returns_empty_due_list PASSED [ 43%]
tests/test_pawpal.py::test_remove_task_reduces_count PASSED              [ 47%]
tests/test_pawpal.py::test_high_priority_scheduled_before_low PASSED     [ 52%]
tests/test_pawpal.py::test_same_priority_shorter_task_scheduled_first PASSED [ 56%]
tests/test_pawpal.py::test_task_exactly_fitting_available_time_is_scheduled PASSED [ 60%]
tests/test_pawpal.py::test_task_one_minute_over_budget_is_skipped PASSED [ 65%]
tests/test_pawpal.py::test_owner_with_zero_minutes_skips_everything PASSED [ 69%]
tests/test_pawpal.py::test_owner_with_no_pets_produces_empty_schedule PASSED [ 73%]
tests/test_pawpal.py::test_sort_by_time_returns_chronological_order PASSED [ 78%]
tests/test_pawpal.py::test_filter_by_pet_returns_only_that_pets_slots PASSED [ 82%]
tests/test_pawpal.py::test_filter_by_unknown_pet_returns_empty_list PASSED [ 86%]
tests/test_pawpal.py::test_no_conflicts_in_normal_schedule PASSED        [ 91%]
tests/test_pawpal.py::test_forced_overlap_triggers_conflict_warning PASSED [ 95%]
tests/test_pawpal.py::test_adjacent_slots_do_not_conflict PASSED         [100%]

============================== 23 passed in 0.02s ==============================
```

### Confidence level

⭐⭐⭐⭐ (4/5)

The core scheduling logic — priority ordering, time budget enforcement, recurrence, and conflict detection — is well covered. One star withheld because the tests run against in-memory objects only; there are no integration tests covering the Streamlit UI layer or persistence across sessions, so edge cases introduced by user interaction remain untested.

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
