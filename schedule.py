import datetime as dt
from task import Task
from timeslot import TimeSlot


optimal_example_timeslot = TimeSlot(start=dt.time(hour=9, minute=30), end=dt.time(hour=11, minute=30))


def priority_order(tasks:list[Task]):
    priorities: dict[Task, float] = {}
    static_tasks: dict[Task, None] = {}

    for task in tasks:
        if task.ultimate_prio is None:
            #static_tasks = {task: task.ultimate_prio}
            continue
        else:
            priorities[task] = task.ultimate_prio

    sorted_prios = dict(
        sorted(priorities.items(), key=lambda x: x[1], reverse=True)
    )
    return {**static_tasks, **sorted_prios}


def scheduler(tasks:list[Task], optimal_timeslot:TimeSlot = optimal_example_timeslot):
    prio_order = priority_order(tasks)
    for task in prio_order:
        print(task, optimal_timeslot)
        if not task.flexibility:
            pass #Here it should schedule each task at the time that they are "due".
        else:
            pass #This is where the splitting up of tasks into smaller 30 minute segments and scheduling them across multiple days should happen.


task1 = Task(
    name="task1",
    description="idk",
    due_date=dt.datetime(2026, 5, 20, 14, 17),
    duration=dt.timedelta(minutes=30),
    priority=1,
    flexibility=True,
    difficulty=2,
)
task2 = Task(
    name="task2",
    description="idk",
    due_date=dt.datetime(2026, 6, 3, 9, 42),
    duration=dt.timedelta(hours=1),
    priority=2,
    flexibility=True,
    difficulty=3,
)
task3 = Task(
    name="task3",
    description="idk",
    due_date=dt.datetime(2026, 5, 27, 11, 5),
    duration=dt.timedelta(minutes=90),
    priority=3,
    flexibility=True,
    difficulty=4,
)
task4 = Task(
    name="task4",
    description="idk",
    due_date=dt.datetime(2026, 7, 1, 18, 30),
    duration=dt.timedelta(hours=2),
    priority=4,
    flexibility=True,
    difficulty=5,
)
task5 = Task(
    name="task5",
    description="idk",
    due_date=dt.datetime(2026, 6, 14, 8, 13),
    duration=dt.timedelta(hours=3),
    priority=5,
    flexibility=True,
    difficulty=1,
)
task6 = Task(
    name="task6",
    description="idk",
    due_date=dt.datetime(2026, 6, 21, 23, 59),
    duration=dt.timedelta(minutes=45),
    priority=0,
    flexibility=True,
    difficulty=6,
)
task7 = Task(
    name="task7",
    description="idk",
    due_date=dt.datetime(2026, 6, 21, 23, 59),
    duration=dt.timedelta(minutes=45),
    priority=0,
    flexibility=False,
    difficulty=6,
)
scheduler([task1, task2, task3, task4, task5, task6, task7])
#print(priority_order([task1, task2, task3, task4, task5, task6, task7]))
