import datetime as dt

from task import Task, ultimate_prio

test = Task(
    name="testname",
    description="test",
    due_date=dt.datetime(year=2026, month=5, day=19),
    duration=dt.timedelta(hours=5),
    priority=5,
    difficulty=10,
)


print(test.difficulty, test.priority, ultimate_prio(test))

test.duration = dt.timedelta(hours=1, minutes=30)
