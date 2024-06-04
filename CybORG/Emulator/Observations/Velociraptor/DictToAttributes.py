class DictToAttributes:

    def __init__(self, artifact_info=None):

        self.artifact_info = artifact_info

        if artifact_info is not None:
            self.__dict__.update(artifact_info)
