import datetime as dt


dummy_date = dt.date(year=2026, month=6, day=1)

class TimeSlot:
    def __init__(self, start: dt.time, end: dt.time):
        if start < end:
            self.start: dt.datetime = dt.datetime.combine(dummy_date, start)
            self.end: dt.datetime = dt.datetime.combine(dummy_date, end)

            self.duration: dt.timedelta = self.end - self.start

        else:
            raise ValueError("Start time must be smaller than end time")

    def compare(self, *others: TimeSlot) -> dict[TimeSlot, dt.timedelta]:
        how_overlapping: dict[TimeSlot, dt.timedelta] = dict()

        """
        I am unsure if would be better to do this for all of the TimeSlot objects like the current implementation
        does or if it is better to return as soon as it finds one object that overlaps. Obviously the current
        implementation is more versatile, but when it comes to scheduling I do just want to find if one of the other
        timeslots overlaps and just ignore the rest.
        """

        for other in others:
            if (
                other.start <= self.end
                and other.start >= self.start
                or (other.end <= self.end and other.end >= self.start)
            ):
                overlap = min(self.end, other.end) - max(self.start, other.start)

            else:
                overlap = dt.timedelta(0)

            how_overlapping[other] = overlap

        return how_overlapping
