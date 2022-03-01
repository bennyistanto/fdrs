import FWIFunctions
import numpy as np
import math
import datetime

NODATA_VAL = -99999

def calculateFWI(temp_arr, rh_arr, wind_arr, rain_arr, ffmc_prev_arr,
                 dmc_prev_arr, dc_prev_arr, lat_arr, date_):
    ffmc = calculateFFMC(temp_arr,rh_arr,wind_arr,rain_arr,ffmc_prev_arr)
    dmc = calculateDMC(temp_arr,rh_arr,rain_arr,dmc_prev_arr, lat_arr, date_)
    dc = calculateDC(temp_arr,rain_arr,dc_prev_arr,lat_arr, date_.month)
    isi = calculateISI(wind_arr, ffmc)
    bui = calculateBUI(dmc,dc)
    fwi = __calculateFWI(isi, bui)

    return fwi, ffmc, dmc, dc, bui, isi

def calculateFFMC(temp, rh, wind, rain, ffmc_prev):
    '''Calculates today's Fine Fuel Moisture Code for grid
Parameters:
    TEMP is the 12:00 LST temperature in degrees celsius
    RH is the 12:00 LST relative humidity in %
    WIND is the 12:00 LST wind speed in kph
    RAIN is the 24-hour accumulated rainfall in mm, calculated at 12:00 LST
    FFMCPrev is the previous day's FFMC
    '''

    ffmc_mat = []
    for temp_i, rh_i, wind_i, rain_i, ffmcp_i, temp_mi in \
            zip(np.nditer(temp), np.nditer(rh), np.nditer(wind), np.nditer(rain), np.nditer(ffmc_prev),
                np.nditer(np.ma.getmask(temp))):
        if not temp_mi:
            ffmc_v = FWIFunctions.FFMC(temp_i, rh_i, wind_i, rain_i, ffmcp_i)
            ffmc_mat.append(ffmc_v)
        else:
            ffmc_mat.append(NODATA_VAL)
    ffmc = np.array(ffmc_mat)
    ffmc = np.reshape(ffmc, temp.shape)
    return ffmc

def calculateDMC(temp, rh, rain, dmc_prev, latitude, date_):
    '''Calculates today's Duff Moisture Code
Parameters:
    TEMP is the 12:00 LST temperature in degrees celsius
    RH is the 12:00 LST relative humidity in %
    RAIN is the 24-hour accumulated rainfall in mm, calculated at 12:00 LST
    DMCPrev is the prevvious day's DMC
    Lat is the latitude in decimal degrees of the location for which calculations are being made
    Month is the month of Year (1..12) for the current day's calculations.
    '''

    dmc_mat = []
    for temp_i, rh_i, rain_i, dmcp_i, lat_i, temp_mi in \
            zip(np.nditer(temp), np.nditer(rh), np.nditer(rain), np.nditer(dmc_prev), np.nditer(latitude),
                np.nditer(np.ma.getmask(temp))):
        if not temp_mi:
            # calculate day length
            day_length = __calcDayLength(lat_i, date_.year, date_.month, date_.day)
            dmc_v = __calcDMC(temp_i, rh_i, rain_i, dmcp_i, day_length)
            dmc_mat.append(dmc_v)
        else:
            dmc_mat.append(NODATA_VAL)
    dmc = np.array(dmc_mat)
    dmc = np.reshape(dmc, temp.shape)
    return dmc

def calculateDC(temp,rain,dc_prev,latitude,month):
    dc_mat = []
    for temp_i, rain_i, dcp_i, lat_i, temp_mi in \
            zip(np.nditer(temp), np.nditer(rain), np.nditer(dc_prev), np.nditer(latitude),
                np.nditer(np.ma.getmask(temp))):
        if not temp_mi:
            dc_v = FWIFunctions.DC(temp_i, rain_i, dcp_i, lat_i, month)
            dc_mat.append(dc_v)
        else:
            dc_mat.append(NODATA_VAL)
    dc = np.array(dc_mat)
    dc = np.reshape(dc, temp.shape)
    return dc

def calculateISI(wind, ffmc):
    isi_mat = []
    for wind_i, ffmc_i, wind_mi in \
            zip(np.nditer(wind), np.nditer(ffmc), np.nditer(np.ma.getmask(wind))):
        if not wind_mi:
            isi_v = FWIFunctions.ISI(wind_i, ffmc_i)
            isi_mat.append(isi_v)
        else:
            isi_mat.append(NODATA_VAL)
    isi = np.array(isi_mat)
    isi = np.reshape(isi, wind.shape)
    return isi

def calculateBUI(dmc, dc):
    bui_mat = []
    for dmc_i, dc_i in \
            zip(np.nditer(dmc), np.nditer(dc)):
        if not dmc_i == NODATA_VAL:
            bui_v = FWIFunctions.BUI(dmc_i, dc_i)
            bui_mat.append(bui_v)
        else:
            bui_mat.append(NODATA_VAL)
    bui = np.array(bui_mat)
    bui = np.reshape(bui, dmc.shape)
    return bui

def __calculateFWI(isi, bui):
    fwi_mat = []
    for isi_i, bui_i in \
            zip(np.nditer(isi), np.nditer(bui)):
        if not isi_i == NODATA_VAL:
            fwi_v = FWIFunctions.FWI(isi_i, bui_i)
            fwi_mat.append(fwi_v)
        else:
            fwi_mat.append(NODATA_VAL)
    fwi = np.array(fwi_mat)
    fwi = np.reshape(fwi, isi.shape)
    return fwi


def __calcDMC(TEMP,RH,RAIN,DMCPrev,DAYLENGTH):
    '''Calculates today's Duff Moisture Code
Parameters:
    TEMP is the 12:00 LST temperature in degrees celsius
    RH is the 12:00 LST relative humidity in %
    RAIN is the 24-hour accumulated rainfall in mm, calculated at 12:00 LST
    DMCPrev is the prevvious day's DMC
    Lat is the latitude in decimal degrees of the location for which calculations are being made
    Month is the month of Year (1..12) for the current day's calculations.

    DMC(17,42,0,6,45.98,4) = 8.5450511359999997'''

    RH = min(100.0,RH)
    if RAIN > 1.5:
        re = 0.92 * RAIN - 1.27

        mo = 20.0 + math.exp(5.6348 - DMCPrev / 43.43)

        if DMCPrev <= 33.0:
            b = 100.0 / (0.5 + 0.3 * DMCPrev)
        else:
            if DMCPrev <= 65.0:
                b = 14.0 - 1.3 * math.log(DMCPrev)
            else:
                b = 6.2 * math.log(DMCPrev) - 17.2

        mr = mo + 1000.0 * re / (48.77 + b * re)

        pr = 244.72 - 43.43 * math.log(mr - 20.0)

        if pr > 0.0:
            DMCPrev = pr
        else:
            DMCPrev = 0.0

    if TEMP > -1.1:
        d1 = DAYLENGTH

        k = 1.894 * (TEMP + 1.1) * (100.0 - RH) * d1 * 0.000001

    else:
        k = 0.0

    return DMCPrev + 100.0 * k

def __calcDayLength(latitude, year, month, day):
#def hitungPanjangHari(Latitude, thn, bln, tgl):
    '''-------------------------------------------------------------------------
    Menghitung panjang hari
    Diadopsi dari Shierary-Weather ver 2.0 yang dikembangkan Handoko(1998)
    Panjang hari dalam jam
    '''
    dayofyear   = datetime.date(year, month, day).timetuple().tm_yday
    dekl   = -23.4 * math.cos(2 * math.pi * (dayofyear + 10) / 365.0)
    sinld  = math.sin(latitude * math.pi / 180.0) * math.sin(dekl * math.pi / 180.0)
    cosld  = math.cos(latitude * math.pi / 180.0) * math.cos(dekl * math.pi / 180.0)
    sinb   = math.sin(-0.833 * math.pi / 180.0)
    arg    = (sinb - sinld) / cosld
    arccos = 2 * math.atan(1) - math.atan(arg / math.sqrt(1 - arg * arg))
    Dlen   = 24.0 / math.pi * arccos
    return Dlen

