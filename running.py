_is_run = True


class Running:
    @staticmethod
    def stop():
        global _is_run
        _is_run = False

    @staticmethod
    def is_run():
        return _is_run
