import warnings
import pytest
import tests.unit.N01_db as N01


def test_N01():
    N01.test_db_read()
    assert True


def test_N02():
    N01.test_db_write()
    assert True


def test_N03():
    with pytest.raises(Exception) as e_info:
        N01.test_db_write_incorrect()
    warnings.warn(UserWarning(e_info))
