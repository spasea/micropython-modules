class StateSaveInterface:
    def to_string(self) -> str:
        """
        Converts state to string

        :return:
        """
        pass

    def from_string(self, string: str) -> 'StateSaveInterface':
        """
        Adds data from string to state

        :param string:
        :return:
        """
        pass
