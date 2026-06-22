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

## ✨ Features

- **Priority-first scheduling** — high-priority tasks are always placed first; within the same priority, shorter tasks come first so the maximum number of tasks fits in the available time window
- **Time budget enforcement** — the owner sets how many minutes they have free; tasks that don't fit are skipped with a reason rather than crashing or silently dropping
- **Recurring task automation** — `mark_complete()` uses Python's `timedelta` to automatically compute the next due date: daily tasks reset to tomorrow, weekly tasks to 7 days out
- **Conflict detection** — after generating a plan, `detect_conflicts()` scans every slot pair for overlapping time windows and surfaces `st.warning` banners in the UI so issues can't be missed
- **Sorting by time** — `sort_by_time()` ensures the displayed schedule always reads chronologically, regardless of the order tasks were added
- **Per-pet filtering** — `filter_by_pet()` lets the owner focus on one animal's schedule at a time in both the CLI and the Streamlit UI
- **Multi-pet support** — one owner can manage any number of pets; each pet owns its own task list and the scheduler aggregates tasks across all of them

---

## 🖥️ Sample Output

Run `python main.py` to see a demo schedule in the terminal:

```
====================================================
  Full Schedule (sorted by start time)
====================================================
  08:00 — 08:10  Feeding (Luna, 10 min, high)
  08:10 — 08:20  Litter box (Luna, 10 min, high)
  08:20 — 08:50  Morning walk (Biscuit, 30 min, high)
  08:50 — 09:05  Brush coat (Luna, 15 min, medium)
  09:05 — 09:20  Enrichment toy (Biscuit, 15 min, medium)

====================================================
  Biscuit's Scheduled Tasks (filtered)
====================================================
  08:20 — 08:50  Morning walk (30 min)
  09:05 — 09:20  Enrichment toy (15 min)

====================================================
  Incomplete Tasks Across All Pets (filtered)
====================================================
  [Biscuit] Enrichment toy — medium priority, due today
  [Biscuit] Grooming — low priority, due today
  [Biscuit] Morning walk — high priority, due today
  [Luna] Brush coat — medium priority, due today
  [Luna] Vet check — low priority, due today
  [Luna] Litter box — high priority, due today
  [Luna] Feeding — high priority, due today

====================================================
  Skipped Tasks
====================================================
  - Grooming (Biscuit): not enough time remaining
  - Vet check (Luna): not enough time remaining

====================================================
  Summary: 5 scheduled, 2 skipped
====================================================

====================================================
  Conflict Detection Demo
====================================================
  WARNING: 'Morning walk' (Biscuit, 08:20–08:50) overlaps with 'Evening walk' (Biscuit, 08:30–09:00)
  WARNING: 'Brush coat' (Luna, 08:50–09:05) overlaps with 'Evening walk' (Biscuit, 08:30–09:00)
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

The app runs at `http://localhost:8501` after `streamlit run app.py`. A user follows four sections top to bottom.

### Step-by-step workflow

1. **Set up owner profile** — Enter your name, how many minutes you have free today (e.g. 90), and what time your day starts (e.g. 8 for 8:00 AM). Click "Save owner profile." The owner object is stored in session state and persists for the rest of the session.

2. **Add pets** — Click "Add a new pet," fill in name, species, breed, and age, then click "Add pet." Repeat for each animal. Each pet's profile line (e.g. `Biscuit (Golden Retriever dog, age 3)`) appears above the form showing task count.

3. **Add tasks to each pet** — Use the pet selector to choose which pet you are adding tasks for. The task table shows all existing tasks with columns for duration, priority, recurrence, whether it's done today, and its next due date. Click "Add a task," fill in the task details (name, duration, priority, recurrence), and submit. The table updates immediately.

4. **Mark tasks complete** — Use the "Mark complete" dropdown to record that a task was done. The app calls `mark_complete()` which automatically calculates and displays the next due date (tomorrow for daily, 7 days out for weekly). Completed tasks disappear from the scheduler's candidate pool.

5. **Generate today's schedule** — Click the blue "Generate schedule" button. The scheduler runs `generate_plan()` (priority-first greedy fill), then `sort_by_time()` (chronological display), then `detect_conflicts()`. Three metric cards appear: tasks scheduled, tasks skipped, and time used.

6. **Read conflict warnings** — If any scheduled slots overlap in time, amber `st.warning` banners appear *above* the schedule table naming both conflicting tasks and their exact time windows. A green `st.success` banner confirms no conflicts when the schedule is clean.

7. **Filter by pet** — Use the "Filter by pet" dropdown to narrow the schedule table to a single animal's tasks. Selecting "All pets" restores the full view.

8. **Review skipped tasks** — Expand the "Skipped tasks" section to see which tasks didn't make the cut and why (e.g., "not enough time remaining").

9. **Read the full explanation** — Expand "Full plan explanation" to see the plain-text output from `explain_plan()`, which lists every scheduled slot with its time window and notes every skipped task with a reason.

### Key scheduler behaviors visible in the UI

- **Sorting** — schedule rows always appear in HH:MM order regardless of task input order
- **Priority ordering** — all high-priority tasks appear before medium/low ones
- **Duration tiebreaker** — among same-priority tasks, shorter ones are placed first to maximize the number of tasks that fit
- **Conflict warnings** — shown as amber banners immediately when detected, not buried in output
- **Recurrence automation** — "Next due" column updates the moment a task is marked complete
