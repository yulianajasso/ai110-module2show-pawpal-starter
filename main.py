from pawpal_system import Task, Pet, Owner, Scheduler


def print_section(title: str) -> None:
    print(f"\n{'=' * 52}")
    print(f"  {title}")
    print('=' * 52)


def main():
    # --- Build pets (tasks added out of order intentionally) ---
    biscuit = Pet(name="Biscuit", species="dog", breed="Golden Retriever", age=3)
    biscuit.add_task(Task("Enrichment toy", 15, "medium", "daily"))   # medium added first
    biscuit.add_task(Task("Grooming",       20, "low",    "weekly"))  # low added second
    biscuit.add_task(Task("Morning walk",   30, "high",   "daily"))   # high added last
    biscuit.add_task(Task("Feeding",        10, "high",   "daily"))   # high, shorter

    luna = Pet(name="Luna", species="cat", breed="Siamese", age=5)
    luna.add_task(Task("Brush coat",  15, "medium", "weekly"))        # medium first
    luna.add_task(Task("Vet check",   60, "low",    "as-needed", notes="Annual check"))
    luna.add_task(Task("Litter box",  10, "high",   "daily"))         # high last
    luna.add_task(Task("Feeding",     10, "high",   "daily"))

    # Mark one task complete to test incomplete filtering
    biscuit.tasks[3].mark_complete()  # Feeding (Biscuit) already done

    owner = Owner(name="Alex", available_time=90, start_time=480)
    owner.add_pet(biscuit)
    owner.add_pet(luna)

    scheduler = Scheduler(owner)
    scheduler.generate_plan()

    # 1 — Full sorted schedule
    print_section("Full Schedule (sorted by start time)")
    for slot in scheduler.sort_by_time():
        print(f"  {slot['start']} — {slot['end']}  {slot['task']} "
              f"({slot['pet']}, {slot['duration']} min, {slot['priority']})")

    # 2 — Filter: only Biscuit's slots
    print_section("Biscuit's Scheduled Tasks (filtered)")
    biscuit_slots = scheduler.filter_by_pet("Biscuit")
    if biscuit_slots:
        for slot in biscuit_slots:
            print(f"  {slot['start']} — {slot['end']}  {slot['task']} ({slot['duration']} min)")
    else:
        print("  No scheduled tasks for Biscuit.")

    # 3 — Filter: incomplete tasks across all pets
    print_section("Incomplete Tasks Across All Pets (filtered)")
    for pet, task in owner.get_incomplete_tasks():
        status = "due today" if task.is_due_today() else "not due"
        print(f"  [{pet.name}] {task.name} — {task.priority} priority, {status}")

    # 4 — Filter: all tasks for Luna specifically
    print_section("All of Luna's Tasks (filtered by pet)")
    for task in owner.get_tasks_for_pet("Luna"):
        due = "due" if task.is_due_today() else "not due"
        print(f"  {task.name} ({task.recurrence}, {task.priority}) — {due}")

    # 5 — Skipped tasks
    if scheduler.skipped:
        print_section("Skipped Tasks")
        for item in scheduler.skipped:
            print(f"  - {item['task']} ({item['pet']}): {item['reason']}")

    print_section(f"Summary: {len(scheduler.schedule)} scheduled, "
                  f"{len(scheduler.skipped)} skipped")

    # ----------------------------------------------------------------
    # Conflict detection demo
    # Force two tasks into overlapping time windows to trigger warnings.
    # Biscuit's "Evening walk" starts at 09:10 — overlaps with the
    # already-scheduled "Morning walk" (08:20–08:50).
    # ----------------------------------------------------------------
    print_section("Conflict Detection Demo")
    overlap_task = Task("Evening walk", 30, "high", "daily")
    scheduler.force_schedule(overlap_task, "Biscuit", "08:30")  # overlaps 08:20–08:50

    conflicts = scheduler.detect_conflicts()
    if conflicts:
        for warning in conflicts:
            print(f"  {warning}")
    else:
        print("  No conflicts detected.")


if __name__ == "__main__":
    main()
