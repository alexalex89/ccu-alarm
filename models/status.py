import enum


class AlarmStatus(enum.Enum):

    UNSCHARF = 0
    HUELLSCHUTZ = 1
    VOLLSCHUTZ = 2

    @staticmethod
    def from_id(code):
        if code == 0:
            return AlarmStatus.UNSCHARF
        elif code == 1:
            return AlarmStatus.HUELLSCHUTZ
        elif code == 2:
            return AlarmStatus.VOLLSCHUTZ
        else:
            raise NotImplementedError()
