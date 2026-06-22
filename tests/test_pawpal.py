from datetime import date, timedelta
from pawpal_system import Task, Pet


def test_mark_complete_changes_status():
    task = Task(name="Morning walk", duration=30, priority="high", recurrence="daily")
    assert task.completed_today is False

    task.mark_complete()

    assert task.completed_today is True


def test_mark_complete_sets_last_completed():
    from datetime import date
    task = Task(name="Grooming", duration=20, priority="low", recurrence="weekly")
    assert task.last_completed is None

    task.mark_complete()

    assert task.last_completed == date.today().isoformat()


def test_daily_task_next_due_is_tomorrow():
    task = Task(name="Feeding", duration=10, priority="high", recurrence="daily")
    task.mark_complete()
    expected = (date.today() + timedelta(days=1)).isoformat()
    assert task.next_due == expected


def test_weekly_task_next_due_is_seven_days():
    task = Task(name="Grooming", duration=20, priority="low", recurrence="weekly")
    task.mark_complete()
    expected = (date.today() + timedelta(days=7)).isoformat()
    assert task.next_due == expected


def test_completed_daily_task_not_due_today():
    task = Task(name="Walk", duration=30, priority="high", recurrence="daily")
    task.mark_complete()
    assert task.is_due_today() is False


def test_as_needed_task_has_no_next_due():
    task = Task(name="Vet check", duration=60, priority="low", recurrence="as-needed")
    task.mark_complete()
    assert task.next_due is None


def test_add_task_increases_pet_task_count():
    pet = Pet(name="Biscuit", species="dog", breed="Golden Retriever", age=3)
    assert len(pet.tasks) == 0

    pet.add_task(Task(name="Feeding", duration=10, priority="high", recurrence="daily"))
    assert len(pet.tasks) == 1

    pet.add_task(Task(name="Walk", duration=30, priority="high", recurrence="daily"))
    assert len(pet.tasks) == 2
