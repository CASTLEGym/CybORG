from CybORG.Shared import Observation


class VerifyFilesObservation(Observation):

    def __init__(self, current_verification_dict, previous_verification_dict, density_scout_dict):

        super().__init__(True)

        self.current_verification_dict = current_verification_dict
        self.previous_verification_dict = previous_verification_dict

        intersection_dict = {
            x: previous_verification_dict[x] for x in previous_verification_dict if x in current_verification_dict
        }

        previous_difference_dict = {
            x: previous_verification_dict[x] for x in previous_verification_dict if x not in current_verification_dict
        }

        current_difference_dict = {
            x: current_verification_dict[x] for x in current_verification_dict if x not in previous_verification_dict
        }

        self.different_checksum_list = []
        self.density_scout_list = []

        self.new_verification_dict = dict(intersection_dict)
        self.new_verification_dict.update(previous_difference_dict)
        self.new_verification_dict.update(current_difference_dict)

        self.files_not_present_dict = dict(previous_difference_dict)

        for x in intersection_dict:
            previous_checksum = previous_verification_dict[x]
            current_checksum = current_verification_dict[x]

            if previous_checksum != current_checksum:
                self.different_checksum_list.append(x)

        for file_name, density in density_scout_dict.items():
            if density < 0.9:
                self.density_scout_list.append(file_name)

    def get_verification_dict(self):
        return self.new_verification_dict

    def get_different_checksum_file_list(self):
        return self.different_checksum_list

    def get_density_scout_list(self):
        return self.density_scout_list

    def get_files_not_present_dict(self):
        return self.files_not_present_dict
