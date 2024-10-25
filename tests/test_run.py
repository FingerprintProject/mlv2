import tests.task.S01_create_vectorizer as S01
import tests.task.S02_create_le_zone as S02
import tests.task.S03_vectorize as S03


def test_S01():
    S01.createVectorizer()
    assert True


def test_S02():
    S02.createLeZone()
    assert True


def test_S03():
    S03.vectorize()
    assert True
