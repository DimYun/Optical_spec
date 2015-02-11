#!/usr/bin/env python
# -*- coding: utf-8 -*-

import png
import sys
from PyQt4.Qwt5.qplt import *

reload(sys)
sys.setdefaultencoding('utf8')

r = png.Reader(filename=u'Химия.png')

read_res = r.read()
myiter = read_res[2]
a = myiter.next()

pixels = []
pixels += a
try:
    while a:
        a = myiter.next()
        if a:
            pixels += a
except StopIteration:
    pass

vals = []

i = 0
chan = 0
if read_res[-1]['alpha']:
    chan = 4
else: chan = 3

while i < read_res[0]*read_res[1]*chan:
    vals.append({'R': pixels[i], 'G': pixels[i+1], 'B': pixels[i+2]})
    i += 4
print len(vals)
lines = []
i = 0
while i < read_res[0]:
    j = 0
    cur_sum = 0
    while j < read_res[1]:
        cur_sum += sum(vals[j*read_res[0]+i].values())
        j += 1
    lines.append(cur_sum)
    i += 1
print len(lines)
#qwtPlot = Plot()
#qwtPlot.plot(qplt.Curve(spec.listE, lines,
#                qplt.Pen(spec.colorSpec), spec.specName))