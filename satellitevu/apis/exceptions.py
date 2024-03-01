class ContractAccessError(Exception):
    def __init__(self, status_code: int, detail: str) -> None:
        self.message = f"Contracts Access Error - {status_code} : {detail}"
        super().__init__(self.message)


class OTMError(Exception):
    def __init__(self, status_code: int, detail: str) -> None:
        self.message = f"OTM API Error - {status_code} : {detail}"
        super().__init__(self.message)


class OTMOrderError(OTMError):
    pass


class OTMOrderCancellationError(OTMError):
    pass


class OTMFeasibilityError(OTMError):
    pass
