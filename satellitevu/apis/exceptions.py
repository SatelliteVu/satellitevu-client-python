class ContractAccessError(Exception):
    def __init__(self, status_code: int, detail: str) -> None:
        self.message = f"Contracts Access Error - {status_code} : {detail}"
        super().__init__(self.message)


class OrdersAPIError:
    def __init__(self, status_code: int, detail: str) -> None:
        self.message = f"Orders API Error - {status_code} : {detail}"
        super().__init__(self.message)


class OTMAPIError(Exception):
    def __init__(self, status_code: int, detail: str) -> None:
        self.message = f"OTM API Error - {status_code} : {detail}"
        super().__init__(self.message)


class OTMOrderError(OTMAPIError):
    pass


class OTMOrderCancellationError(OTMAPIError):
    pass


class OTMFeasibilityError(OTMAPIError):
    pass


class OTMParametersError(Exception):
    pass


class IDAPIError(Exception):
    def __init__(self, status_code: int, detail: str) -> None:
        self.message = f"ID API Error - {status_code} : {detail}"
        super().__init__(self.message)
