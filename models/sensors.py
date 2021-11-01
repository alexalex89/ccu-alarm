from models.status import AlarmStatus


class HMIPBase(object):

    def __init__(self, xml):
        self.ise_id = xml.get("ise_id")
        self.name = xml.get("name")

    def check(self, status: AlarmStatus):
        raise NotImplementedError()


class HMIPSMI(HMIPBase):

    def __init__(self, xml):
        super().__init__(xml)
        self._alarm = xml.xpath("./channel/datapoint[@type='MOTION']")[0].get("value") == "true"

    def check(self, status: AlarmStatus):
        if status == AlarmStatus.VOLLSCHUTZ and self._alarm:
            return True
        return False


class HMIPSWDO(HMIPBase):

    def __init__(self, xml):
        super().__init__(xml)
        # CLOSED = 0 ; OPEN = 1
        self._alarm = int(xml.xpath("./channel/datapoint[@type='STATE']")[0].get("value")) == 1

    def check(self, status: AlarmStatus):
        if status in (AlarmStatus.HUELLSCHUTZ, AlarmStatus.VOLLSCHUTZ) and self._alarm:
            return True
        return False