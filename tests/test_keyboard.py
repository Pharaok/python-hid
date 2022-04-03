import hid.keyboard as kb


def test_modifiers():
    assert kb.Modifiers['A'] is kb.Modifiers.LEFT_SHIFT
    assert kb.Modifiers['a'] is kb.Modifiers.NULL


def test_key_codes():
    assert kb.KeyCodes['NULL'] == 0x00
    assert kb.KeyCodes['1'] == 0x1E
    assert kb.KeyCodes.numpad('1') == 0x59


def test_keyboard_report():
    kbr = kb.KeyboardReport(mods=[kb.Modifiers.RIGHT_SHIFT])
    assert (kbr.mods, kbr.keys) == (kb.Modifiers.RIGHT_SHIFT, [0] * 6)

    kbr.press_key(4, 5, 6)
    assert kbr.keys == [4, 5, 6, 0, 0, 0]

    kbr.press_mod(kb.Modifiers.LEFT_CONTROL)
    assert kbr.mods == kb.Modifiers.RIGHT_SHIFT | kb.Modifiers.LEFT_CONTROL

    kbr.release_key(4, 5)
    assert kbr.keys == [6, 0, 0, 0, 0, 0]

    kbr.release_mod(kb.Modifiers.RIGHT_SHIFT)
    assert kbr.mods == kb.Modifiers.LEFT_CONTROL
