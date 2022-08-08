class KeyNotPresentError(ValueError):
    def __init__(self, label : str, key : str):
        super().__init__(f"{label} must contain a key named {key}")


class UndefinedKeyError(ValueError):
    def __init__(self, key : str, set : list):
        super().__init__(f"{key} is not one of {set}")


class DateBadFormatError(ValueError):
    def __init__(self, label : str = "date"):
        super().__init__(f"{label} must have format YYYY-mm-dd")


class DateBeforeError(ValueError):
    def __init__(self, label_before : str, label_after : str):
        super().__init__(f"{label_before} is before {label_after}")


class ForestNotFoundError(FileNotFoundError):
    def __init__(self, name : str):
        super().__init__(f"forest {name}"
                         " does not correspond with an existing directory")
