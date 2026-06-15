import datetime as dt
from task import Task, StaticTask, ultimate_prio
# from dataclasses import dataclass, field
import bisect
from copy import deepcopy
from pydantic.dataclasses import dataclass
from pydantic import Field


@dataclass
class Schedule:
    max_daily_tasks: int = 7
    schedule: list[StaticTask] = Field(default_factory=list)
    static: list[StaticTask] = Field(default_factory=list)
    flexible: list[Task] = Field(default_factory=list)


def insert(task: Task | StaticTask, schedule: Schedule | None) -> Schedule:
    if schedule is None:
        if isinstance(task, Task):
            schedule = Schedule(flexible=[task])
            schedule_fn(schedule)
            return schedule
        else:
            schedule = Schedule(static=[task])
            schedule_fn(schedule)
            return schedule

    elif isinstance(task, StaticTask):
        index = check_overlap(task.interval, schedule.static)
        if isinstance(index, StaticTask):
            raise ValueError
        schedule.static.insert(index, task)
        schedule_fn(schedule)

    else:
        schedule.flexible.append(task)
        schedule_fn(schedule)

    return schedule


def schedule_fn(schedule: Schedule):
    # This line assumes that schedule.static is already sorted and that there are no overlaps in it
    schedule.schedule = schedule.static.copy()

    tasks = deepcopy(schedule.flexible)
    task_map = {id(task_copy): og for task_copy, og in zip(tasks, schedule.flexible)}

    tasks = sorted(tasks, key=ultimate_prio, reverse=True)


    day = dt.datetime.now().date()
    days_iterated = 0

    while any(task.duration > dt.timedelta(minutes=0) for task in tasks) and days_iterated < 30:
        max_tasks = schedule.max_daily_tasks
        tasks = sorted(tasks, key=ultimate_prio, reverse=True)

        for task in tasks:
            if max_tasks <= 0:
                break
            if task.duration <= dt.timedelta(minutes=0):
                continue

            index, interval = find_open_time(task, schedule.schedule, day)
            if index is None or interval is None:
                continue

            new_static_task = StaticTask(
                name=task.name,
                description=task.description,
                interval=interval,
                parent_task=task_map[id(task)],
            )  # task_map[id(task) is required since tasks gets shuffled around

            schedule.schedule.insert(index, new_static_task)

            task.duration += -task.work_length
            max_tasks += -1

        day += dt.timedelta(days=1)
        days_iterated += 1


def find_open_time(task: Task, static_tasks: list[StaticTask], day: dt.date):
    day_end = dt.datetime.combine(day, task.work_window[1])
    start = dt.datetime.combine(day, task.work_window[0])
    end = start + min(task.duration, task.work_length)
    interval = (start, end)

    while end <= day_end:
        index = check_overlap(interval, static_tasks)

        if isinstance(index, int):
            return index, interval

        start = index.interval[1]
        end = start + min(task.duration, task.work_length)
        interval = (start, end)

    return None, None


def check_overlap(
    interval: tuple[dt.datetime, dt.datetime], task_list: list[StaticTask]
):
    index = bisect.bisect_right(task_list, interval[0], key=lambda x: x.interval[0])

    # Check to the right
    if index < len(task_list):
        if (
            task_list[index].interval[0] < interval[1]
            and interval[0] < task_list[index].interval[1]
        ):
            return task_list[index]

    # Check to the left
    if index > 0:
        if (
            task_list[index - 1].interval[0] < interval[1]
            and interval[0] < task_list[index - 1].interval[1]
        ):
            return task_list[index - 1]

    return index


task1 = Task(
    name="task1",
    description="idk",
    due_date=dt.datetime(2026, 5, 20, 14, 17),
    duration=dt.timedelta(minutes=30),
    priority=2,
    difficulty=2,
)
task2 = Task(
    name="task2",
    description="idk",
    due_date=dt.datetime(2026, 6, 3, 9, 42),
    duration=dt.timedelta(hours=1),
    priority=4,
    difficulty=3,
)
task3 = Task(
    name="task3",
    description="idk",
    due_date=dt.datetime(2026, 5, 27, 11, 5),
    duration=dt.timedelta(minutes=90),
    priority=6,
    difficulty=4,
)
task4 = Task(
    name="task4",
    description="idk",
    due_date=dt.datetime(2026, 7, 1, 18, 30),
    duration=dt.timedelta(hours=2),
    priority=8,
    difficulty=5,
)
task5 = Task(
    name="task5",
    description="idk",
    due_date=dt.datetime(2026, 6, 14, 8, 13),
    duration=dt.timedelta(hours=3),
    priority=10,
    difficulty=1,
)
task6 = Task(
    name="task6",
    description="idk",
    due_date=dt.datetime(2026, 6, 21, 23, 59),
    duration=dt.timedelta(minutes=45),
    priority=1,
    difficulty=6,
)
task7 = Task(
    name="task7",
    description="idk",
    due_date=dt.datetime(2026, 6, 21, 23, 59),
    duration=dt.timedelta(minutes=45),
    priority=0,
    difficulty=6,
)
lunch = StaticTask(
        name='lunch',
        interval=(dt.datetime(year=2026, month=6, day=15, hour=12), dt.datetime(year=2026, month=6, day=15, hour=12, minute=30)),
)
'''tasks = [task1, task2, task3, task4, task5, task6, task7, lunch]
schedule = None
for task in tasks:
    schedule = insert(task, schedule)

for t in schedule.schedule:
    print(t.interval[0].date(), t.interval[0].time(), t.interval[1].time(), t.name)
'''
