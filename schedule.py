import datetime as dt
from task import Task


class Schedule:
    def __init__(self, tasks: list[Task]):
        self.tasks = tasks

    @property
    def priority_order(self):
        priorities: dict[Task, float] = {}
        static_tasks: dict[Task, None] = {}

        for task in self.tasks:
            if task.ultimate_prio is None:
                static_tasks = {task: task.ultimate_prio}
            else:
                priorities[task] = task.ultimate_prio

        sorted_prios = dict(
            sorted(priorities.items(), key=lambda x: x[1], reverse=True)
        )
        return {**static_tasks, **sorted_prios}

    """def schedule_tasks(self):
        order = list(self.priority_order.items())
        for task, _ in order:
            pass"""


task1 = Task(
    name="task1",
    description="idk",
    due_date=dt.datetime(2026, 5, 20, 14, 17),
    work_window=None,
    duration=dt.timedelta(minutes=30),
    priority="1",
    flexibility=True,
    difficulty="2",
)
task2 = Task(
    name="task2",
    description="idk",
    due_date=dt.datetime(2026, 6, 3, 9, 42),
    work_window=None,
    duration=dt.timedelta(hours=1),
    priority="2",
    flexibility=True,
    difficulty="3",
)
task3 = Task(
    name="task3",
    description="idk",
    due_date=dt.datetime(2026, 5, 27, 11, 5),
    work_window=None,
    duration=dt.timedelta(minutes=90),
    priority="3",
    flexibility=True,
    difficulty="4",
)
task4 = Task(
    name="task4",
    description="idk",
    due_date=dt.datetime(2026, 7, 1, 18, 30),
    work_window=None,
    duration=dt.timedelta(hours=2),
    priority="4",
    flexibility=True,
    difficulty="5",
)
task5 = Task(
    name="task5",
    description="idk",
    due_date=dt.datetime(2026, 6, 14, 8, 13),
    work_window=None,
    duration=dt.timedelta(hours=3),
    priority="5",
    flexibility=True,
    difficulty="1",
)
task6 = Task(
    name="task6",
    description="idk",
    due_date=dt.datetime(2026, 6, 21, 23, 59),
    work_window=None,
    duration=dt.timedelta(minutes=45),
    priority="0",
    flexibility=True,
    difficulty="6",
)
task7 = Task(
    name="task7",
    description="idk",
    due_date=dt.datetime(2026, 6, 21, 23, 59),
    work_window=None,
    duration=dt.timedelta(minutes=45),
    priority="0",
    flexibility=False,
    difficulty="6",
)

schedule = Schedule(tasks=[task1, task2, task3, task4, task5, task6, task7])
# schedule.schedule_tasks()
print(schedule.priority_order)

print(type(dt.datetime(2026, 5, 20, 14, 17).time()))
