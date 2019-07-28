import copy
import glob
import csv
import os
import argparse
from PIL import Image, ImageFont, ImageDraw

import arabic_char_binder as acb

_CONFIG_ITEMS = 'items'
_CONFIG_COLUMNS_SIZE = 'column size'

_CONFIG_FONT_PATH = 'font path'
_CONFIG_FONT_SIZE = 'font size'
_CONFIG_COLOR = 'color'
_CONFIG_VERTICAL_ALIGNMENT = 'vertical alignment'
_CONFIG_HORIZONTAL_ALIGNMENT = 'horizontal alignment'
_CONFIG_X = 'x'
_CONFIG_Y = 'y'

_TEXT_CONFIGS = {_CONFIG_FONT_PATH: 'serif',
                 _CONFIG_FONT_SIZE: 18,
                 _CONFIG_COLOR: '#000000',
                 _CONFIG_VERTICAL_ALIGNMENT: 'middle',
                 _CONFIG_HORIZONTAL_ALIGNMENT: 'left',
                 _CONFIG_X: '0px',
                 _CONFIG_Y: '0px'}

_DEFAULT_CONFIG_FILE_NAME = 'text_configs.csv'

_OUTPUT_DIR = 'output'


def draw_text(image_path=None, text_configs=None, output_dir_path=os.path.join('.', 'output')):
    # Cleaning output directory
    try:
        if not os.path.exists(_OUTPUT_DIR):
            os.makedirs(_OUTPUT_DIR)
        elif os.listdir(_OUTPUT_DIR):
            confirmation = input('The content of ' + output_dir_path + ' will be overridden, continue? (yes) ')
            if confirmation in ['y', 'yes', '']:
                for f in glob.glob(os.path.join(output_dir_path, '*')):
                    os.remove(f)
            else:
                print('Aborted.')
                exit()
    finally:
        pass

    output_filename = os.path.splitext(os.path.split(image_path)[-1])

    base_image = Image.open(image_path)
    image_width, image_height = base_image.size

    def column_configs(index):
        flattened_configs = {}
        for k, v in text_configs.items():
            if k not in (_CONFIG_COLUMNS_SIZE,):
                flattened_configs[k] = v[index]
        return flattened_configs

    columns_size = text_configs[_CONFIG_COLUMNS_SIZE]
    drawing_properties = []
    max_rows = 0
    for col_index in range(columns_size):
        configs = column_configs(col_index)

        try:
            font = ImageFont.truetype(configs[_CONFIG_FONT_PATH], int(configs[_CONFIG_FONT_SIZE]))
        except IOError:
            print("Couldn't open the the provided font '{0}'".format(configs[_CONFIG_FONT_PATH]))
            continue

        color_number = int(configs[_CONFIG_COLOR][1:] if configs[_CONFIG_COLOR][0] == '#' else configs[_CONFIG_COLOR],
                           16)

        # TODO: Parse (red, green, blue) as well
        fill = ((color_number & 0xff0000) >> 16, (color_number & 0x00ff00) >> 8, color_number & 0x0000ff)

        is_percentage_x = configs[_CONFIG_X][-1] == '%'
        is_percentage_y = configs[_CONFIG_Y][-1] == '%'

        x = image_width * float(configs[_CONFIG_X][:-1]) / 100.0 if is_percentage_x else int(configs[_CONFIG_X])
        y = image_height * float(configs[_CONFIG_Y][:-1]) / 100.0 if is_percentage_y else int(configs[_CONFIG_Y])

        drawing_properties.append({'fill': fill, 'font': font, 'align_v': configs[_CONFIG_VERTICAL_ALIGNMENT],
                                   'align_h': configs[_CONFIG_HORIZONTAL_ALIGNMENT], 'x': x, 'y': y})

        current_row_size = len(configs[_CONFIG_ITEMS])
        max_rows = max_rows if current_row_size < max_rows else current_row_size

    for row_index in range(max_rows):
        im = copy.copy(base_image)
        draw = ImageDraw.Draw(im)
        print('\r', end='')
        print('{0}/{1}...'.format(row_index + 1, max_rows), end='')

        for col_index in range(columns_size):
            text = acb.bind(text_configs[_CONFIG_ITEMS][col_index][row_index])
            fill = drawing_properties[col_index]['fill']
            font = drawing_properties[col_index]['font']
            x = drawing_properties[col_index]['x']
            y = drawing_properties[col_index]['y']

            text_width, text_height = font.getsize(text)
            if drawing_properties[col_index]['align_v'] == 'middle':
                y -= text_height / 2
            elif drawing_properties[col_index]['align_v'] == 'bottom':
                y -= text_height
            if drawing_properties[col_index]['align_h'] == 'center':
                x -= text_width / 2
            elif drawing_properties[col_index]['align_h'] == 'right':
                x -= text_width
            draw.text((x, y), text, fill, font)

        im.save(os.path.join(_OUTPUT_DIR, '{0} ({1}){2}'.format(output_filename[0], row_index + 1,
                                                                   output_filename[1])))

    print('\rCompleted.')


def _parse_configs(file_path=os.path.join('.', 'text_configs.csv')):
    # TODO: Add validation
    with open(file_path) as text_config_file:
        reader = csv.reader(text_config_file, delimiter=',')

        defaults = _TEXT_CONFIGS.copy()
        configs = {k: None for k in list(_TEXT_CONFIGS.keys()) + [_CONFIG_ITEMS, _CONFIG_COLUMNS_SIZE]}

        for row in reader:
            size = len(row) - 1
            key = row[0].lower()

            if configs[_CONFIG_COLUMNS_SIZE] is None or size > configs[_CONFIG_COLUMNS_SIZE]:
                configs[_CONFIG_COLUMNS_SIZE] = size

            if key in _TEXT_CONFIGS:
                if configs[key] is None:
                    configs[key] = [defaults[key]] * size
            elif not bool(key.strip()):
                if configs[_CONFIG_ITEMS] is None:
                    configs[_CONFIG_ITEMS] = [list() for i in range(size)]
            else:
                raise ValueError('Invalid configuration property', 'fss')

            for index, cell in enumerate(row[1:]):
                if key in _TEXT_CONFIGS:
                    stripped_cell = cell.strip()
                    configs[key][index] = stripped_cell if bool(stripped_cell) else defaults[key]
                elif not bool(row[0].strip()):
                    configs[_CONFIG_ITEMS][index].append(cell)

        return configs


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Draw text on images by providing tabular configuration, each row generates an image.',
        prog='draw-text',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument('input', help='image path')
    parser.add_argument('output', help='output directory')
    parser.add_argument('configuration', help='configuration file path (.csv)')

    args = parser.parse_args()

    draw_text(args.input, _parse_configs(args.configuration), args.output)

