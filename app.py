import streamlit as st
from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")
st.caption("Your daily pet care planner.")

# ---------------------------------------------------------------------------
# Session state bootstrap
# st.session_state persists data across reruns so objects aren't reset on
# every button click.
# ---------------------------------------------------------------------------
if "owner" not in st.session_state:
    st.session_state.owner = None

# ---------------------------------------------------------------------------
# Section 1 — Owner Setup
# ---------------------------------------------------------------------------
st.header("1. Owner Profile")

with st.form("owner_form"):
    col1, col2, col3 = st.columns(3)
    with col1:
        owner_name = st.text_input("Your name", value="Alex")
    with col2:
        available_time = st.number_input("Free time today (minutes)", min_value=10, max_value=480, value=90)
    with col3:
        start_hour = st.number_input("Day start (hour, 24h)", min_value=0, max_value=23, value=8)

    submitted = st.form_submit_button("Save owner profile")
    if submitted:
        if st.session_state.owner is None:
            st.session_state.owner = Owner(
                name=owner_name,
                available_time=int(available_time),
                start_time=int(start_hour) * 60,
            )
            st.success(f"Profile created for {owner_name}.")
        else:
            st.session_state.owner.name = owner_name
            st.session_state.owner.set_availability(int(available_time))
            st.session_state.owner.start_time = int(start_hour) * 60
            st.success("Profile updated.")

if st.session_state.owner is None:
    st.info("Save an owner profile above to get started.")
    st.stop()

owner: Owner = st.session_state.owner

# ---------------------------------------------------------------------------
# Section 2 — Pets
# ---------------------------------------------------------------------------
st.divider()
st.header("2. Pets")

if owner.pets:
    for pet in owner.pets:
        st.markdown(f"**{pet.get_profile()}** — {len(pet.tasks)} task(s)")

with st.expander("Add a new pet"):
    with st.form("pet_form"):
        col1, col2 = st.columns(2)
        with col1:
            pet_name = st.text_input("Pet name", value="Biscuit")
            species = st.selectbox("Species", ["dog", "cat", "bird", "rabbit", "other"])
        with col2:
            breed = st.text_input("Breed", value="Golden Retriever")
            age = st.number_input("Age (years)", min_value=0, max_value=30, value=3)

        add_pet = st.form_submit_button("Add pet")
        if add_pet:
            new_pet = Pet(name=pet_name, species=species, breed=breed, age=int(age))
            owner.add_pet(new_pet)
            st.success(f"{pet_name} added!")
            st.rerun()

if not owner.pets:
    st.info("Add at least one pet above.")
    st.stop()

# ---------------------------------------------------------------------------
# Section 3 — Tasks
# ---------------------------------------------------------------------------
st.divider()
st.header("3. Tasks")

pet_names = [p.name for p in owner.pets]
selected_pet_name = st.selectbox("View / add tasks for:", pet_names)
selected_pet: Pet = next(p for p in owner.pets if p.name == selected_pet_name)

if selected_pet.tasks:
    task_data = [t.to_dict() for t in selected_pet.tasks]
    st.dataframe(
        [{
            "Task": t["name"],
            "Duration (min)": t["duration"],
            "Priority": t["priority"],
            "Recurrence": t["recurrence"],
            "Done today": t["completed_today"],
        } for t in task_data],
        use_container_width=True,
    )
else:
    st.info(f"No tasks for {selected_pet_name} yet.")

with st.expander("Add a task"):
    with st.form("task_form"):
        col1, col2, col3 = st.columns(3)
        with col1:
            task_name = st.text_input("Task name", value="Morning walk")
            recurrence = st.selectbox("Recurrence", ["daily", "weekly", "as-needed"])
        with col2:
            duration = st.number_input("Duration (min)", min_value=1, max_value=240, value=30)
        with col3:
            priority = st.selectbox("Priority", ["high", "medium", "low"])
        notes = st.text_input("Notes (optional)", value="")

        add_task = st.form_submit_button("Add task")
        if add_task:
            selected_pet.add_task(Task(
                name=task_name,
                duration=int(duration),
                priority=priority,
                recurrence=recurrence,
                notes=notes,
            ))
            st.success(f"'{task_name}' added to {selected_pet_name}.")
            st.rerun()

# ---------------------------------------------------------------------------
# Section 4 — Generate Schedule
# ---------------------------------------------------------------------------
st.divider()
st.header("4. Today's Schedule")

if st.button("Generate schedule", type="primary"):
    scheduler = Scheduler(owner)
    scheduler.generate_plan()
    st.session_state.schedule = scheduler.schedule
    st.session_state.skipped = scheduler.skipped
    st.session_state.plan_text = scheduler.explain_plan()

if "schedule" in st.session_state and st.session_state.schedule:
    st.success(f"Scheduled {len(st.session_state.schedule)} task(s), "
               f"skipped {len(st.session_state.skipped)}.")

    st.subheader("Planned tasks")
    st.dataframe(
        [{
            "Time": f"{s['start']} – {s['end']}",
            "Task": s["task"],
            "Pet": s["pet"],
            "Duration (min)": s["duration"],
            "Priority": s["priority"],
        } for s in st.session_state.schedule],
        use_container_width=True,
    )

    if st.session_state.skipped:
        st.subheader("Skipped tasks")
        st.dataframe(
            [{
                "Task": s["task"],
                "Pet": s["pet"],
                "Reason": s["reason"],
            } for s in st.session_state.skipped],
            use_container_width=True,
        )

    with st.expander("Full plan explanation"):
        st.text(st.session_state.plan_text)

elif "schedule" in st.session_state and not st.session_state.schedule:
    st.warning("No tasks were due today or none fit in the available time.")
