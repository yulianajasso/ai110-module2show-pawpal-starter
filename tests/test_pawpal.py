from datetime import date, timedelta
import pytest
from pawpal_system import Task, Pet, Owner, Scheduler


# ---------------------------------------------------------------------------
# Helpers — reusable fixtures built as plain functions so each test gets
# a fresh object with no shared state.
# ---------------------------------------------------------------------------

def make_owner(minutes=120, start=480):
    owner = Owner(name="Alex", available_time=minutes, start_time=start)
    return owner


def make_pet_with_tasks():
    pet = Pet(name="Biscuit", species="dog", breed="Golden Retriever", age=3)
    pet.add_task(Task("Feeding",        10, "high",   "daily"))
    pet.add_task(Task("Morning walk",   30, "high",   "daily"))
    pet.add_task(Task("Enrichment toy", 15, "medium", "daily"))
    pet.add_task(Task("Grooming",       20, "low",    "weekly"))
    return pet


# ===========================================================================
# Task — completion and recurrence
# ===========================================================================

def test_mark_complete_changes_status():
    task = Task(name="Morning walk", duration=30, priority="high", recurrence="daily")
    assert task.completed_today is False
    task.mark_complete()
    assert task.completed_today is True


def test_mark_complete_sets_last_completed():
    task = Task(name="Grooming", duration=20, priority="low", recurrence="weekly")
    assert task.last_completed is None
    task.mark_complete()
    assert task.last_completed == date.today().isoformat()


def test_daily_task_next_due_is_tomorrow():
    task = Task(name="Feeding", duration=10, priority="high", recurrence="daily")
    task.mark_complete()
    assert task.next_due == (date.today() + timedelta(days=1)).isoformat()


def test_weekly_task_next_due_is_seven_days():
    task = Task(name="Grooming", duration=20, priority="low", recurrence="weekly")
    task.mark_complete()
    assert task.next_due == (date.today() + timedelta(days=7)).isoformat()


def test_completed_daily_task_not_due_today():
    task = Task(name="Walk", duration=30, priority="high", recurrence="daily")
    task.mark_complete()
    assert task.is_due_today() is False


def test_as_needed_task_has_no_next_due():
    task = Task(name="Vet check", duration=60, priority="low", recurrence="as-needed")
    task.mark_complete()
    assert task.next_due is None


def test_weekly_task_not_due_before_seven_days():
    # Completed 6 days ago — should NOT be due yet
    six_days_ago = (date.today() - timedelta(days=6)).isoformat()
    task = Task(name="Grooming", duration=20, priority="low", recurrence="weekly",
                last_completed=six_days_ago,
                next_due=(date.today() + timedelta(days=1)).isoformat())
    assert task.is_due_today() is False


def test_weekly_task_due_after_seven_days():
    # next_due is today — should be due
    task = Task(name="Grooming", duration=20, priority="low", recurrence="weekly",
                next_due=date.today().isoformat())
    assert task.is_due_today() is True


# ===========================================================================
# Pet — task management
# ===========================================================================

def test_add_task_increases_pet_task_count():
    pet = Pet(name="Biscuit", species="dog", breed="Golden Retriever", age=3)
    assert len(pet.tasks) == 0
    pet.add_task(Task(name="Feeding", duration=10, priority="high", recurrence="daily"))
    assert len(pet.tasks) == 1
    pet.add_task(Task(name="Walk", duration=30, priority="high", recurrence="daily"))
    assert len(pet.tasks) == 2


def test_pet_with_no_tasks_returns_empty_due_list():
    pet = Pet(name="Luna", species="cat", breed="Siamese", age=5)
    assert pet.get_due_tasks() == []


def test_remove_task_reduces_count():
    pet = make_pet_with_tasks()
    before = len(pet.tasks)
    pet.remove_task("Feeding")
    assert len(pet.tasks) == before - 1
    assert all(t.name != "Feeding" for t in pet.tasks)


# ===========================================================================
# Scheduler — priority ordering
# ===========================================================================

def test_high_priority_scheduled_before_low():
    owner = make_owner(minutes=60)
    pet = Pet(name="Biscuit", species="dog", breed="Golden Retriever", age=3)
    pet.add_task(Task("Low task",  10, "low",  "daily"))
    pet.add_task(Task("High task", 10, "high", "daily"))
    owner.add_pet(pet)

    scheduler = Scheduler(owner)
    scheduler.generate_plan()

    task_names = [s["task"] for s in scheduler.schedule]
    assert task_names.index("High task") < task_names.index("Low task")


def test_same_priority_shorter_task_scheduled_first():
    owner = make_owner(minutes=60)
    pet = Pet(name="Biscuit", species="dog", breed="Golden Retriever", age=3)
    pet.add_task(Task("Long high",  30, "high", "daily"))
    pet.add_task(Task("Short high", 10, "high", "daily"))
    owner.add_pet(pet)

    scheduler = Scheduler(owner)
    scheduler.generate_plan()

    task_names = [s["task"] for s in scheduler.schedule]
    assert task_names.index("Short high") < task_names.index("Long high")


# ===========================================================================
# Scheduler — time budget
# ===========================================================================

def test_task_exactly_fitting_available_time_is_scheduled():
    owner = make_owner(minutes=30)
    pet = Pet(name="Biscuit", species="dog", breed="Golden Retriever", age=3)
    pet.add_task(Task("Walk", 30, "high", "daily"))
    owner.add_pet(pet)

    scheduler = Scheduler(owner)
    scheduler.generate_plan()

    assert len(scheduler.schedule) == 1
    assert scheduler.schedule[0]["task"] == "Walk"


def test_task_one_minute_over_budget_is_skipped():
    owner = make_owner(minutes=29)
    pet = Pet(name="Biscuit", species="dog", breed="Golden Retriever", age=3)
    pet.add_task(Task("Walk", 30, "high", "daily"))
    owner.add_pet(pet)

    scheduler = Scheduler(owner)
    scheduler.generate_plan()

    assert len(scheduler.schedule) == 0
    assert len(scheduler.skipped) == 1


def test_owner_with_zero_minutes_skips_everything():
    owner = make_owner(minutes=0)
    pet = make_pet_with_tasks()
    owner.add_pet(pet)

    scheduler = Scheduler(owner)
    scheduler.generate_plan()

    assert len(scheduler.schedule) == 0
    assert len(scheduler.skipped) > 0


def test_owner_with_no_pets_produces_empty_schedule():
    owner = make_owner()
    scheduler = Scheduler(owner)
    scheduler.generate_plan()

    assert scheduler.schedule == []
    assert scheduler.skipped == []


# ===========================================================================
# Scheduler — sorting
# ===========================================================================

def test_sort_by_time_returns_chronological_order():
    owner = make_owner(minutes=120)
    pet = make_pet_with_tasks()
    owner.add_pet(pet)

    scheduler = Scheduler(owner)
    scheduler.generate_plan()

    sorted_slots = scheduler.sort_by_time()
    start_times = [s["start"] for s in sorted_slots]
    # Each start time should be <= the next
    assert start_times == sorted(start_times)


def test_filter_by_pet_returns_only_that_pets_slots():
    owner = make_owner(minutes=120)
    biscuit = Pet(name="Biscuit", species="dog", breed="Golden Retriever", age=3)
    biscuit.add_task(Task("Walk", 20, "high", "daily"))
    luna = Pet(name="Luna", species="cat", breed="Siamese", age=5)
    luna.add_task(Task("Feeding", 10, "high", "daily"))
    owner.add_pet(biscuit)
    owner.add_pet(luna)

    scheduler = Scheduler(owner)
    scheduler.generate_plan()

    biscuit_slots = scheduler.filter_by_pet("Biscuit")
    assert all(s["pet"] == "Biscuit" for s in biscuit_slots)


def test_filter_by_unknown_pet_returns_empty_list():
    owner = make_owner()
    pet = make_pet_with_tasks()
    owner.add_pet(pet)

    scheduler = Scheduler(owner)
    scheduler.generate_plan()

    assert scheduler.filter_by_pet("Ghost") == []


# ===========================================================================
# Scheduler — conflict detection
# ===========================================================================

def test_no_conflicts_in_normal_schedule():
    owner = make_owner(minutes=120)
    pet = make_pet_with_tasks()
    owner.add_pet(pet)

    scheduler = Scheduler(owner)
    scheduler.generate_plan()

    assert scheduler.detect_conflicts() == []


def test_forced_overlap_triggers_conflict_warning():
    owner = make_owner(minutes=60)
    pet = Pet(name="Biscuit", species="dog", breed="Golden Retriever", age=3)
    pet.add_task(Task("Walk", 30, "high", "daily"))
    owner.add_pet(pet)

    scheduler = Scheduler(owner)
    scheduler.generate_plan()  # Walk is scheduled 08:00–08:30

    overlap = Task("Bath", 30, "medium", "weekly")
    scheduler.force_schedule(overlap, "Biscuit", "08:15")  # overlaps 08:00–08:30

    conflicts = scheduler.detect_conflicts()
    assert len(conflicts) == 1
    assert "WARNING" in conflicts[0]


def test_adjacent_slots_do_not_conflict():
    # A ends at 08:30, B starts at 08:30 — touching but not overlapping
    owner = make_owner(minutes=60)
    pet = Pet(name="Biscuit", species="dog", breed="Golden Retriever", age=3)
    pet.add_task(Task("Walk",    30, "high",   "daily"))
    pet.add_task(Task("Feeding", 10, "medium", "daily"))
    owner.add_pet(pet)

    scheduler = Scheduler(owner)
    scheduler.generate_plan()

    # Normal sequential schedule never conflicts
    assert scheduler.detect_conflicts() == []
