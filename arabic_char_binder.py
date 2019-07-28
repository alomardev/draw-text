from bidi.algorithm import get_display
import os
import argparse


_BOUND_CHARS_PN = ('\0', 'ﺒ', 'ﺘ', 'ﺜ', 'ﺠ', 'ﺤ', 'ﺨ', '\0', '\0', '\0', '\0', 'ﺴ', 'ﺸ', 'ﺼ', 'ﻀ', 'ﻄ', 'ﻈ', 'ﻌ', 'ﻐ',
                   'ﻔ', 'ﻘ', 'ﻜ', 'ﻠ', 'ﻤ', 'ﻨ', 'ﻬ', '\0', 'ﻴ', 'ﯩ', '\0', '\0', '\0', 'ﺌ', '\0', '\0', '\0', '\0',
                   '\0', '\0', '\0')

_BOUND_CHARS_P = ('ﺎ', 'ﺐ', 'ﺖ', 'ﺚ', 'ﺞ', 'ﺢ', 'ﺦ', 'ﺪ', 'ﺬ', 'ﺮ', 'ﺰ', 'ﺲ', 'ﺶ', 'ﺺ', 'ﺾ', 'ﻂ', 'ﻆ', 'ﻊ', 'ﻎ', 'ﻒ',
                  'ﻖ', 'ﻚ', 'ﻞ', 'ﻢ', 'ﻦ', 'ﻪ', 'ﻮ', 'ﻲ', 'ﻰ', 'ﺄ', 'ﺈ', 'ﺆ', 'ﺊ', 'ﺂ', 'ﻼ', 'ﻸ', 'ﻺ', 'ﻶ', 'ﺔ', '\0')

_BOUND_CHARS_N = ('\0', 'ﺑ', 'ﺗ', 'ﺛ', 'ﺟ', 'ﺣ', 'ﺧ', '\0', '\0', '\0', '\0', 'ﺳ', 'ﺷ', 'ﺻ', 'ﺿ', 'ﻃ', 'ﻇ', 'ﻋ', 'ﻏ',
                  'ﻓ', 'ﻗ', 'ﻛ', 'ﻟ', 'ﻣ', 'ﻧ', 'ﻫ', '\0', 'ﻳ', 'ﯨ', '\0', '\0', '\0', 'ﺋ', '\0', '\0', '\0', '\0',
                  '\0', '\0', '\0')

_CONNECTORS = ('ب', 'ت', 'ث', 'ج', 'ح', 'خ', 'س', 'ش', 'ص', 'ض', 'ط', 'ظ', 'ع', 'غ', 'ف', 'ق', 'ك', 'ل', 'م', 'ن', 'ه',
               'ي', 'ى', 'ئ', 'ـ')

_INDEX = ('ا', 'ب', 'ت', 'ث', 'ج', 'ح', 'خ', 'د', 'ذ', 'ر', 'ز', 'س', 'ش', 'ص', 'ض', 'ط', 'ظ', 'ع', 'غ', 'ف', 'ق', 'ك',
          'ل', 'م', 'ن', 'ه', 'و', 'ي', 'ى', 'أ', 'إ', 'ؤ', 'ئ', 'آ', 'ﻻ', 'ﻹ', 'ﻷ', 'ﻵ', 'ة', 'ـ')


def _get_arabic_index(c):
    try:
        return _INDEX.index(c)
    except ValueError:
        return -1


def _is_connector(c):
    return c in _CONNECTORS


def _is_isolator(c):
    return _get_arabic_index(c) > -1 and not _is_connector(c)


def _convert_to_hindi_digits(c):
    if c == '0':
        return '٠'
    elif c == '1':
        return '١'
    elif c == '2':
        return '٢'
    elif c == '3':
        return '٣'
    elif c == '4':
        return '٤'
    elif c == '5':
        return '٥'
    elif c == '6':
        return '٦'
    elif c == '7':
        return '٧'
    elif c == '8':
        return '٨'
    elif c == '9':
        return '٩'
    else:
        return c


def bind(original_text, hindi=False):
    output = []

    lines = original_text.split('\n')
    first_line = True
    for line in lines:
        if not first_line:
            output.append('\n')

        line_output = []

        l = len(line)
        i = 0
        while i < l:
            p = line[i - 1] if i > 0 else '\0'
            c = line[i]
            n = line[i + 1] if i < l - 1 else '\0'

            if c == 'ل':
                if n == 'ا':
                    i += 1
                    c = 'ﻻ'
                elif n == 'أ':
                    i += 1
                    c = 'ﻷ'
                elif n == 'إ':
                    i += 1
                    c = 'ﻹ'
                elif n == 'آ':
                    i += 1
                    c = 'ﻵ'

            connect_p = _is_connector(p)
            connect_n = _get_arabic_index(n) > -1 and not _is_isolator(c)

            new_char = '\0'
            index = _get_arabic_index(c)
            if index > -1:
                if connect_p and connect_n:
                    new_char = _BOUND_CHARS_PN[index]
                elif connect_p:
                    new_char = _BOUND_CHARS_P[index]
                elif connect_n:
                    new_char = _BOUND_CHARS_N[index]
            elif hindi:
                new_char = _convert_to_hindi_digits(c)

            new_char = c if new_char == '\0' else new_char
            line_output.append(new_char)

            i += 1

        output = output + line_output

    return get_display(''.join(output))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Convert Arabic text to its\' final shape based on characters position',
        prog='arabic-char-binder',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument('text', nargs='+', help='Text to be converted')
    parser.add_argument('--hindi', dest='hindi', action='store_true', help='Convert Arabic digits to Hindi digits')

    args = parser.parse_args()

    print(bind(' '.join(args.text), args.hindi))
