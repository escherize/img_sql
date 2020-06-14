#! /usr/bin/python3

import argparse
import os
import shutil
import sqlite3
from PIL import Image

create_db = '''
DROP TABLE if exists pixels;
CREATE TABLE pixels
    (xy string,
     x int,
     y int,
     r int,
     g int,
     b int);
create unique index xy_idx on pixels (xy);
'''


def fmt_color(n):
    return max(0, min(int(n), 255))


def read_modify_save(from_path, statement, out_path):
    input_image = Image.open(from_path)
    width, height = input_image.size
    print("image read at " + from_path + " is " +
          str(width) + " x " + str(height))

    # put image into db if not indexed:
    if not os.path.isfile(from_path + ".db"):
        print(from_path + " is not indexed. Indexing now...")
        idx_conn = sqlite3.connect(from_path + ".db")
        idx_conn.executescript(create_db)
        for x in range(width):
            for y in range(height):
                r, g, b = input_image.getpixel((x, y))
                xy = str(x)+"|"+str(y)
                insert_stmnt = f"INSERT INTO pixels VALUES('{xy}', {x}, {y}, {r}, {g}, {b})"
                # print(insert_stmnt)
                idx_conn.execute(insert_stmnt)
        idx_conn.commit()
        idx_conn.close()

    # now the from_path.db file will be moved so we can use temp db
    shutil.copyfile(from_path + ".db", "temp.db")
    conn = sqlite3.connect("temp.db")

    # modify db
    statements = statement.split(";")
    for s in statements:
        if s != '':
            s = s.strip()
            print("'" + s + "' updated " +
                  str(conn.execute(s).rowcount) + " pixels")

    # pull image out of db:
    print("rendering new image...")
    out_image = Image.new('RGB', (width, height))
    for x in range(width):
        for y in range(height):
            xy = str(x)+"|"+str(y)
            r, g, b = conn.execute(
                f"select r, g, b from pixels where xy = '{xy}'").fetchone()
            out_image.putpixel(
                (x, y), (fmt_color(r), fmt_color(g), fmt_color(b)))

    out_image.save(out_path)
    print("new image written to: " + out_path)
    conn.close()
    os.remove("temp.db")


if (__name__ == '__main__'):
    parser = argparse.ArgumentParser(usage='''
    Run sql on an image
    
    You have access to a table called pixels with the following columns:
    
    x - the x coordinate of a pixel
    y - the y coordinate of a pixel
    r - the red   component of a pixel [0, 255]
    g - the green component of a pixel [0, 255]
    b - the blue  component of a pixel [0, 255]

    examples:

img_sql -i samples/big.jpg \
            -o samples/big_out.jpg \
            -s 'update pixels set r = 255 / 5 where x > 100 and x < 200;'

    img_sql -i samples/big.jpg \
            -o samples/big_out.jpg \
            -s 'update pixels set r = x / 5 where b > 100; update pixels set g = g * (1 + b / 100) where b < 100'
    ''')
    parser.add_argument('-i', '--input', type=str,
                        help='input image file we will run your sql statment on', required=True)
    parser.add_argument('-s', '--statement', type=str,
                        help='sql statment to run on _in_', required=True)
    parser.add_argument('-o', '--output', type=str,
                        help='output file', required=True)
    args = parser.parse_args()
    if args.output and args.input and args.statement:
        read_modify_save(args.input, args.statement, args.output)
    else:
        args.print_help()
