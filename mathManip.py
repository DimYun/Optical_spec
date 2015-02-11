# -*- coding: utf8 -*-
from PyQt4 import QtCore
import math
import numpy as np
from math import factorial
from lmfit import Model
from lmfit.models import GaussianModel
import constGlobal


def calc_smooth_sm(p, spec, parent=None):
    # Make calculate for simple smooth
    spec.list_transform = []
    try:
        smooth = spec.list_i[0]
        for ind in spec.list_i[1:]:
            spec.list_transform.append(smooth)
            smooth = ind * p + (1 - p) * smooth
    except NameError as var:
        constGlobal.error_mes(var, 'm: mathManip, str 22')
        return None


def calc_smooth_sg(y, window_size, order, spec, parent=None, deriv=0, rate=1):
    # Make calculate for SG smooth
    y = np.array(y)
    spec.list_transform = []
    try:
        window_size = np.abs(np.int(window_size))
        order = np.abs(np.int(order))
    except ValueError as var:
        constGlobal.error_mes(var, 'm: mathManip, str 24')
        return
    if window_size % 2 != 1 or window_size < 1:
        constGlobal.error_mes('window_size size must be a positive odd number', 'm: mathManip, str 27')
        return
    if window_size < order + 2:
        constGlobal.error_mes('window_size is too small for the polynomials order', 'm: mathManip, str 30')
        return
    order_range = range(order+1)
    half_window = (window_size -1) // 2
    b = np.mat([[k**i for i in order_range] for k in xrange(-half_window, half_window+1)])
    m = np.linalg.pinv(b).A[deriv] * rate**deriv * factorial(deriv)

    firstvals = y[0] - np.abs(y[1:half_window+1][::-1] - y[0])
    lastvals = y[-1] + np.abs(y[-half_window-1:-1][::-1] - y[-1])
    y = np.concatenate((firstvals, y, lastvals))
    list_i_now = list(np.convolve(m[::-1], y))
    for i in range(len(list_i_now)):
        if list_i_now[i] < 0:
            list_i_now[i] = 0
    spec.list_transform = list_i_now[:]


def calculate_log_scale(spec, parent=None):
    # Natural log scale of I
    spec.list_transform = []
    for i in spec.list_i:
        if i > 0:
            spec.list_transform.append(math.log(i))
        else:
            spec.list_transform.append(1)


def sigma_z(spec, parent=None):
    # Calcaulate average, normal dispersion and sigma_Z
    spec.list_transform = []
    len_list = float(len(spec.list_i))

    aver_x = 0
    for i in spec.list_i:
        aver_x += i
    aver_x = float(aver_x) / len_list

    sigma_x = 0
    for i in spec.list_i:
        sigma_x += (i - aver_x) * (i - aver_x)
    sigma_x = math.sqrt(float(sigma_x) / len_list)

    for i in spec.list_i:
        spec.list_transform.append((i - aver_x) / sigma_x)


def sigma(spec, parent=None):
    # Calcaulate average and normal dispersion
    spec.list_transform = []
    len_list = len(spec.list_i)

    aver_x = 0
    for i in spec.list_i:
        aver_x += i
    aver_x = float(aver_x) / float(len_list)

    sigma_x = 0
    for i in range(len_list):
        sigma_x += (spec.list_i[i] - aver_x) * (spec.list_i[i] - aver_x)
        spec.list_transform.append(math.sqrt(float(sigma_x) / (i+1)))


def furie(spec, parent=None):
    # Calculate furie-conversion os spec
    fft_res = np.fft.fft(spec.list_i)
    # Прямое Фурье, действительная часть
    # spec.list_transform = map(lambda x: x.real, fft_res)
    filtered = map(lambda x: 0 if (x > 2+2j) else x, fft_res)
    spec.list_transform = map(lambda x: x.real, np.fft.ifft(filtered))


def deriv(spec, parent=None):
    x = spec.list_l
    y = spec.list_i
    d1 = np.diff(y)/np.diff(x)
    d2 = np.diff(d1)/np.diff(x[1:])
    d2 = np.array([0] + list(d2) + [0])
    spec.list_transform = list(d2)
    #std_d2 = 3*d2.std()
    #spec.list_transform = map(lambda x: x if abs(x) > std_d2 else 0.0, list(d2))


def approxPoly(list_x, list_y, order):
    # Calculate coef for polinom approximation
    ret = np.polyfit(list_x, list_y, order, cov=True)
    return ret


def curValuePoly(x, coef):
    # Return y for x and coef of polinom
    res = 0.0
    curXdg = 1.0
    for i in xrange(1, len(coef)+1):
        res += curXdg*coef[-i]
        curXdg *= x
    return res


def peakIntegr(name_peak, x_left, x_right, type_int, spec_index):
    # Calculate intensity and area of peaks

    list_data = []

    for spec in constGlobal.list_spec[spec_index]:
        i = 0
        while spec.list_l[i] < x_left:
            i += 1
        index_left = i

        while spec.list_l[i] <= x_right:
            i += 1
        index_right = i

        noise_left_x = []
        noise_left_y = []
        if index_left - 25 > 0:
            noise_left_x = spec.list_l[index_left-25:index_left]
            noise_left_y = spec.list_i[index_left-25:index_left]
        else:
            noise_left_x = spec.list_l[:index_left]
            noise_left_y = spec.list_i[:index_left]

        noise_right_x = []
        noise_right_y = []
        if index_right - (len(spec.list_l) - 25) > 0:
            noise_right_x = spec.list_l[index_right:index_right+25]
            noise_right_y = spec.list_i[index_right:index_right+25]
        else:
            noise_right_x = spec.list_l[index_right:]
            noise_right_y = spec.list_i[index_right:]

        if len(noise_left_y) > 5 and \
                        math.fabs((noise_left_y[-1] - sum(noise_left_y)/len(noise_left_y))/noise_left_y[-1]) > 0.1:
            noise_left_y = noise_left_y[-5:]
            noise_left_x = noise_left_x[-5:]
            noise_right_y = noise_right_y[0:5]
            noise_right_x = noise_right_x[0:5]

        if len(noise_right_y) > 5 and \
                        math.fabs((noise_right_y[0] - sum(noise_right_y)/len(noise_right_y))/noise_right_y[0]) > 0.1:
            noise_left_y = noise_left_y[-5:]
            noise_left_x = noise_left_x[-5:]
            noise_right_y = noise_right_y[0:5]
            noise_right_x = noise_right_x[0:5]

        if len(noise_left_x) != len(noise_left_y):
            min_len = min(len(noise_left_x), len(noise_left_y))
            noise_left_x = noise_left_x[:min_len]
            noise_left_y = noise_left_y[:min_len]
        if len(noise_right_x) != len(noise_right_y):
            min_len = min(len(noise_right_x), len(noise_right_y))
            noise_right_x = noise_right_x[:min_len]
            noise_right_y = noise_right_y[:min_len]
        noise_x_all = noise_left_x + noise_right_x
        noise_y_all = noise_left_y + noise_right_y

        noise_deg = 3
        noise_coeffs = approxPoly(noise_left_x + noise_right_x, noise_left_y + noise_right_y, noise_deg)
        noise_coeffs = noise_coeffs[0]

        max_val_intens = max(spec.list_i[index_left:index_right])
        ind_max_val = index_left + spec.list_i[index_left:index_right].index(max_val_intens)
        max_pure_intens = max(0.0, max_val_intens - curValuePoly(spec.list_l[ind_max_val], noise_coeffs))
        max_pure_intens = round(max_pure_intens, 3)

        # Think to faster code
        list_i_pure = spec.list_i[:]
        for i in range(index_left, index_right):
            signal = spec.list_i[i] - curValuePoly(spec.list_l[i], noise_coeffs)
            list_i_pure[i] = signal

        area_peak = 0.0
        index_left_dirty = index_left
        if type_int == 0:
            while index_left_dirty <= index_right:
                step_now = spec.list_l[index_left+1]-spec.list_l[index_left]
                delta_now = list_i_pure[index_left+1] - list_i_pure[index_left]
                area_peak += step_now * list_i_pure[index_left] + (delta_now * step_now / 2.0)
                index_left_dirty += 1
            area_peak = round(area_peak, 3)
        elif type_int == 1:
            index_left_dirty += 2
            while index_left_dirty <= index_right:
                area_peak += (spec.list_l[index_left]-spec.list_l[index_left-2]) * \
                (list_i_pure[index_left-2] +
                4.0 * (list_i_pure[index_left-1]) +
                list_i_pure[index_left])
                index_left_dirty += 1
            area_peak /= 12.0
            area_peak = round(area_peak, 3)
        elif type_int == 2:
            # This is a true way
            gmod = GaussianModel()
            pars = gmod.guess(np.array(list_i_pure[index_left:index_right]),
                              x=np.array(range(len(spec.list_l[index_left:index_right]))))
            result = gmod.fit(list_i_pure[index_left:index_right], pars,
                              x=range(len(spec.list_l[index_left:index_right])))
            fit_res = result.best_fit
            count = 0
            for i in range(index_left, index_right):
                signal = fit_res[count] + curValuePoly(spec.list_l[i], noise_coeffs)
                list_i_pure[i] = signal
                count += 1
            spec.list_transform = list_i_pure[:]

            maxy, miny = max(fit_res), min(fit_res)
            amp = maxy - miny
            halfmax_vals = []
            count = 0
            for i in range(index_left, index_right):
                if fit_res[count] > amp / 2.0:
                    halfmax_vals.append(fit_res[count])
                count += 1
            # halfmax_vals = np.where(fit_res > amp / 2.0)[0]
            sig = (halfmax_vals[-1] - halfmax_vals[0]) / 2.35

            area_peak = round(amp*(2.0*math.pi)**0.5*sig, 3)

        spec.peaks.append({'name': name_peak,
                           'data_i': max_pure_intens,
                           'data_S': area_peak})
        list_data.append(spec.peaks)
    return list_data

