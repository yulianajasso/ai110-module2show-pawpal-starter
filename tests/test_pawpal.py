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


def test_add_task_increases_pet_task_count():
    pet = Pet(name="Biscuit", species="dog", breed="Golden Retriever", age=3)
    assert len(pet.tasks) == 0

    pet.add_task(Task(name="Feeding", duration=10, priority="high", recurrence="daily"))
    assert len(pet.tasks) == 1

    pet.add_task(Task(name="Walk", duration=30, priority="high", recurrence="daily"))
    assert len(pet.tasks) == 2
