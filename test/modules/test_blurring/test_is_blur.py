from modules.blurring.is_blur import decide_if_blur


def test_decide_if_blur():
    assert decide_if_blur(100, 100, 0, [500, 1000, 1500]) == 0
    assert decide_if_blur(90, 80, 50, [500, 1000, 1500]) == -1
    assert decide_if_blur(90, 60, 50, [500, 1000, 1500]) == 0
    assert decide_if_blur(90, 35, 40, [500, 1000, 1500]) == 1
    assert decide_if_blur(90, 30, 30, [500, 1000, 1500]) == 2
