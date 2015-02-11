#!/usr/bin/env python
# -*- coding: utf-8 -*-

import constGlobal

class Spectrum(object):
    # Need convert to wawelenght
    list_transform = []

    def __init__(self, list_l, list_i, name):
        self.file_name = 'Undefined'
        self.spec_name = name
        self.spec_color = constGlobal.list_color[constGlobal.ind_color]

        self.list_i = list_i
        self.list_l = list_l
        self.peaks = []
        constGlobal.ind_color += 1
        constGlobal.list_spec[constGlobal.ind_spec].append(self)


def save_spec(tab_index, string_save):
    for spec in constGlobal.list_spec[tab_index]:
        file_save = open(string_save + '/' + spec.spec_name + '.spe', 'w')
        file_save.write(str(spec.list_l[0]) + '\n')
        file_save.write(str(spec.list_l[-1]) + '\n')
        for a in spec.list_i:
            file_save.write(str(a) + '\n')
        file_save.close()