from pawpal_system import Task, Pet, Owner, Scheduler


def main():
    # --- Build pets ---
    biscuit = Pet(name="Biscuit", species="dog", breed="Golden Retriever", age=3)
    biscuit.add_task(Task("Morning walk",   30, "high",   "daily"))
    biscuit.add_task(Task("Feeding",        10, "high",   "daily"))
    biscuit.add_task(Task("Enrichment toy", 15, "medium", "daily"))
    biscuit.add_task(Task("Grooming",       20, "low",    "weekly"))

    luna = Pet(name="Luna", species="cat", breed="Siamese", age=5)
    luna.add_task(Task("Feeding",         10, "high",   "daily"))
    luna.add_task(Task("Litter box",      10, "high",   "daily"))
    luna.add_task(Task("Brush coat",      15, "medium", "weekly"))
    luna.add_task(Task("Vet check",       60, "low",    "as-needed",
                       notes="Annual check — schedule if overdue"))

    # --- Build owner ---
    owner = Owner(name="Alex", available_time=90, start_time=480)
    owner.add_pet(biscuit)
    owner.add_pet(luna)

    # --- Run scheduler ---
    scheduler = Scheduler(owner)
    scheduler.generate_plan()

    # --- Print schedule ---
    print("=" * 52)
    print(f"  PawPal+ — Daily Schedule for {owner.name}")
    print("=" * 52)
    print(scheduler.explain_plan())
    print("=" * 52)
    print(f"  Time used:      {90 - owner.available_time + sum(s['duration'] for s in scheduler.schedule)} / {90} min")
    print(f"  Tasks scheduled: {len(scheduler.schedule)}")
    print(f"  Tasks skipped:   {len(scheduler.skipped)}")
    print("=" * 52)


if __name__ == "__main__":
    main()
