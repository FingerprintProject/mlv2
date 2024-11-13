import tests.task.S01_create_vectorizer as S01
import tests.task.S02_create_le_zone as S02
import tests.task.S03_vectorize_supervised as S03
import tests.task.S04_vectorize_unsupervised as S04
import tests.task.S05_augment as S05
import tests.task.S06_prepare_training_data as S06
import tests.task.S07_train as S07


# def test_S01():
#     S01.createVectorizer()
#     assert True


def test_S02():
    S02.createLeZone()
    assert True


def test_S03():
    S03.vectorize_sup()
    assert True


def test_S04():
    S04.vectorize_unsup()
    assert True


def test_S05():
    S05.augment()
    assert True


def test_S06():
    S06.prepare_training_data()
    assert True


def test_S07():
    S07.training()
    assert True
