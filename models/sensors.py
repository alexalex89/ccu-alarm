from models.status import AlarmStatus


class HMIPBase(object):

    def __init__(self, xml):
        self.ise_id = xml.get("ise_id")
        self.name = xml.get("name")

    def check(self, status: AlarmStatus):
        raise NotImplementedError()

    def sabotage(self, status: AlarmStatus):
        raise NotImplementedError()


class HMIPSMI(HMIPBase):

    def __init__(self, xml):
        super().__init__(xml)
        self._sabotage = xml.xpath("./channel/datapoint[@type='SABOTAGE']")[0].get("value") == "true"
        self._alarm = xml.xpath("./channel/datapoint[@type='MOTION']")[0].get("value") == "true"

    def check(self, status: AlarmStatus):
        return status == AlarmStatus.VOLLSCHUTZ and self._alarm

    def sabotage(self, status: AlarmStatus):
        return status == AlarmStatus.VOLLSCHUTZ and self._sabotage


class HMIPSWDO(HMIPBase):

    def __init__(self, xml):
        super().__init__(xml)
        self._sabotage = xml.xpath("./channel/datapoint[@type='SABOTAGE']")[0].get("value") == "true"
        # CLOSED = 0 ; OPEN = 1
        self._alarm = int(xml.xpath("./channel/datapoint[@type='STATE']")[0].get("value")) == 1

    def check(self, status: AlarmStatus):
        return status in (AlarmStatus.HUELLSCHUTZ, AlarmStatus.VOLLSCHUTZ) and self._alarm

    def sabotage(self, status: AlarmStatus):
        return status in (AlarmStatus.HUELLSCHUTZ, AlarmStatus.VOLLSCHUTZ) and self._sabotage
