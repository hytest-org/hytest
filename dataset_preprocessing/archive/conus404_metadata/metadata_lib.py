#!/usr/bin/env python

import json
from collections import Counter


# ============================
# wrfout variable info
# ============================
# Variables that are integrated over 60 minutes per hourly timestep
vars_60min_accum = ['ACDEWC', 'ACDRIPR', 'ACDRIPS', 'ACECAN', 'ACEDIR', 'ACETLSM', 'ACETRAN',
                    'ACEVAC', 'ACEVB', 'ACEVC', 'ACEVG', 'ACFROC', 'ACFRZC', 'ACGHB', 'ACGHFLSM',
                    'ACGHV', 'ACINTR', 'ACINTS', 'ACIRB', 'ACIRC', 'ACIRG', 'ACLHFLSM', 'ACLWDNLSM',
                    'ACLWUPLSM', 'ACMELTC', 'ACPAHB', 'ACPAHG', 'ACPAHLSM', 'ACPAHV', 'ACPONDING',
                    'ACQLAT', 'ACQRF', 'ACRAINLSM', 'ACRAINSNOW', 'ACRUNSB', 'ACRUNSF', 'ACSAGB',
                    'ACSAGV', 'ACSAV', 'ACSHB', 'ACSHC', 'ACSHFLSM', 'ACSHG', 'ACSNBOT', 'ACSNFRO',
                    'ACSNOWLSM', 'ACSNSUB', 'ACSUBC', 'ACSWDNLSM', 'ACSWUPLSM', 'ACTHROR', 'ACTHROS',
                    'ACTR', 'GRAUPEL_ACC_NC', 'PREC_ACC_C', 'PREC_ACC_NC', 'SNOW_ACC_NC']

# Variables that are accumulated from model start
vars_model_accum = ['ACGRDFLX', 'ACHFX', 'ACLHF',
                    'ACSNOM',
                    'GRAUPELNC', 'HAILNC',
                    'I_ACLWDNB', 'I_ACLWDNBC', 'I_ACLWDNT', 'I_ACLWDNTC', 'I_ACLWUPB',
                    'I_ACLWUPBC', 'I_ACLWUPT', 'I_ACLWUPTC', 'I_ACSWDNB', 'I_ACSWDNBC',
                    'I_ACSWDNT', 'I_ACSWDNTC', 'I_ACSWUPB', 'I_ACSWUPBC', 'I_ACSWUPT',
                    'I_ACSWUPTC', 'I_RAINC', 'I_RAINNC',
                    'QRFS', 'QSLAT', 'QSPRINGS',
                    'RAINSH', 'RECH', 'SNOWNC']

vars_bucket_J_accum = ['ACLWDNB', 'ACLWDNBC', 'ACLWDNT', 'ACLWDNTC', 'ACLWUPB', 'ACLWUPBC', 'ACLWUPT',
                       'ACLWUPTC', 'ACSWDNB', 'ACSWDNBC', 'ACSWDNT', 'ACSWDNTC', 'ACSWUPB', 'ACSWUPBC',
                       'ACSWUPT', 'ACSWUPTC']

vars_bucket_mm_accum = ['RAINC', 'RAINNC']


# ============================
# wrfauxhist24 info
# ============================
# # Variables that are integrated over 60 minutes per hourly timestep
vars_60min_accum = ['PREC_ACC_NC']
vars_model_accum = ['I_RAINNC']
vars_bucket_mm_accum = ['RAINNC']

# ============================
# wrfxtrm info
# ============================


def read_override_file(filename):
    # Read override file
    fhdl = open(filename, 'r', encoding='ascii')
    rawdata = fhdl.read().splitlines()
    fhdl.close()

    it = iter(rawdata)
    next(it)   # Skip header

    override_map = {}
    for row in it:
        flds = row.split('\t')
        override_map[flds[0]] = flds[1]
        # print(flds)
    return override_map


def init_wordmap(df):
    # Build dictionary of description words with counts
    word_cnt = Counter()

    for vv in list(df.keys()):
        cvar = df[vv]

        for cattr, val in cvar.attrs.items():
            if cattr == 'description':
                for ww in val.split(' '):
                    word_cnt[ww] += 1

    return dict(word_cnt)


def read_wordmap(filename):
    # Read a word map file for processing the description strings
    fhdl = open(filename, 'r', encoding='ascii')
    rawdata = fhdl.read().splitlines()
    fhdl.close()

    it = iter(rawdata)
    next(it)   # Skip header

    word_map = {}
    for row in it:
        flds = row.split('\t')
        if len(flds[2]) != 0:
            word_map[flds[0].replace('"', '')] = flds[2].replace('"', '')

    return word_map


def write_wordmap_json(filename, word_map):
    # Write a json file given a dictionary of words-to-modified-words
    with open(filename, 'w') as json_file:
        json.dump(word_map, json_file)


def read_wordmap_json(filename):
    with open(filename, 'r') as json_file:
        data = json.load(json_file)
    return data
