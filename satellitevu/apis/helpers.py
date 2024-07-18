from io import BytesIO

from satellitevu.http.base import ResponseWrapper


def raw_response_to_bytes(response: ResponseWrapper) -> BytesIO:
    """
    Converts the raw response data from a request into a bytes object.
    """
    raw_response = response.raw

    if isinstance(raw_response, bytes):
        data = BytesIO(raw_response)
    elif hasattr(raw_response, "read"):
        data = BytesIO(raw_response.read())
    elif hasattr(raw_response, "iter_content"):
        data = BytesIO()
        for chunk in raw_response.iter_content():
            data.write(chunk)
        data.seek(0)
    else:
        raise Exception(
            (
                "Cannot convert response object with raw type"
                f"{type(raw_response)} into byte stream."
            )
        )

    return data


def bytes_to_file(data: BytesIO, destfile: str) -> str:
    """
    Converts bytes into a file object at the specified location.
    """
    with open(destfile, "wb+") as f:
        f.write(data.getbuffer())

    return destfile
