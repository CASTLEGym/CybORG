from CybORG.Shared import Observation


class DecoyObservation(Observation):

    def __init__(self, process_listing, success=None):
        super().__init__(success=success)

        self.process_listing = process_listing
