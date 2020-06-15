# img_sql

This code lets you run sql on images.

So, given this image as input
![](samples/matrix.jpg)

    ./img_sql.py -i samples/matrix.jpg \
    -o samples/matrix_out.jpg \
    -s 'update pixels set r = g, b = r, g = b where x > 700;
        update pixels set r = b, b = g, g = r where x < 700 and y > 200;
        update pixels set r = g, b = r, g = b where x > 1200;
        update pixels set r = g, b = r, g = b where x + y > 1100;
        update pixels set r = 250 where x > 100 and x < 400 and y * x > 50000'

----

The file created at `samples/matrix_out.jpg` is:

![](samples/matrix_out.jpg)