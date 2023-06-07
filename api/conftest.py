# pylint: disable=unused-variable
import pytest 

from api import app


@pytest.fixture()
def test_client():
    test_client = app.test_client()

    yield test_client