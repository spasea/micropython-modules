class StateSaveInterface:
    def to_string(self) -> str:
        """
        Converts state to string

        :return:
        """
        pass

    def from_string(self, string: str, last_loaded_time: tuple) -> 'StateSaveInterface':
        """
        Adds data from string to state

        :param last_loaded_time:
        :param string:
        :return:
        """
        pass
