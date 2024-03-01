class OTMError(Exception):
    def __init__(self, status_code: int, detail: str) -> None:
        self.message = f"OTM API Error - {status_code} : {detail}"
        super().__init__(self.message)


class OTMOrderCancellationError(OTMError):
    pass


class OTMFeasibilityError(OTMError):
    pass
