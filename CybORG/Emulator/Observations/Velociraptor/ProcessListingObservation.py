from CybORG.Shared import Observation
from CybORG.Emulator.Observations.Velociraptor.DictToAttributes import DictToAttributes


class ProcessInfo(DictToAttributes):

    def __init__(self, process_info_dict=None):

        super().__init__(artifact_info=process_info_dict)


class ProcessListingObservation(Observation):

    def __init__(self, process_list=None, success: bool = None):

        super().__init__(success=success)

        self.artifact_info = process_list

        if process_list is None:
            process_list = []

        self.process_list = []
        for process_info_dict in process_list:
            self.process_list.append(ProcessInfo(process_info_dict=process_info_dict))

    def get_process_list(self):
        return self.process_list
