from mtdata.retry import retry


class FauxResult:
    def __init__(self, value: bool):
        self.value = value

    @property
    def success(self) -> bool:
        return self.value


class FauxOperation:
    def __init__(self):
        self.results = [
            FauxResult(False),
            FauxResult(True),
        ]

    def __call__(self):
        return self.results.pop(0)


def test_retry():
    op = FauxOperation()
    result = retry(op, attempt_delta=1)
    assert result.success
    assert op.results == []

    op = FauxOperation()
    op.results.insert(0, FauxResult(False))
    result = retry(op, attempt_delta=1, max_attempts=2)
    assert not result.success
    assert len(op.results) == 1
    assert op.results[0].success
