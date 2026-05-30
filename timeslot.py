import datetime as dt


class TimeSlot:
    def __init__(self, start: dt.datetime, end: dt.datetime):
        self.start = start
        self.end = end

    def compare(self, *others: TimeSlot) -> dict[TimeSlot, dt.timedelta]:
        how_overlapping: dict[TimeSlot, dt.timedelta] = dict()
        overlap = dt.timedelta()

        """
        I am unsure if would be better to do this for all of the TimeSlot objects like the current implementation
        does or if it is better to return as soon as it finds one object that overlaps. Obviously the current
        implementation is mre versatile, but when it comes to scheduling I do just want to find if one of the other
        timeslots overlaps and just ignore the rest.
        """

        for other in others:
            if self.start.date() != other.start.date():
                overlap = dt.timedelta(0)
            elif (
                other.start <= self.end
                and other.start >= self.start
                or (other.end <= self.end and other.end >= self.start)
            ):
                overlap = min(self.end, other.end) - max(self.start, other.start)
            else:
                overlap = dt.timedelta(0)

            how_overlapping[other] = overlap

        return how_overlapping
