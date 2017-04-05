#!/usr/bin/env python3
import os.path, glob, re
from collections import OrderedDict


# CONFIGURATION
## DIRECTORIES

SCC4_dir = 'scc4'
SCCSW_dir = 'sccSW'
SCCRY_dir = 'sccRY'

## EXTENSIONS
SCC4_ext = 'scc4'
SCCSW_ext = 'sccSW'
SCCRY_ext = 'sccRY'

## FILES
def getFileList(d, e):
    return glob.glob(os.path.join(d, '*.' + e))

SCC4_files = getFileList(SCC4_dir, SCC4_ext)
SCCSW_files = getFileList(SCCSW_dir, SCCSW_ext)
SCCRY_files = getFileList(SCCRY_dir, SCCRY_ext)

## SELECTED SIGNIFICANCE LEVELS
SigLevs = [0.9, 'max'] # float, 'max', 'min' or 'mean'

# MAIN ROUTINE
Table = OrderedDict()

def getSpeciesList(f4, fSW, fRY):
    f4, fSW, fRY = set(f4), set(fSW), set(fRY)
    return fRY.union(f4.union(fSW))

def cleanNames(l, e4, eSW, eRY):
    return [f.split('/')[-1].replace('.'+e4, '').replace('.'+eSW, '').replace('.'+eRY, '') for f in l]

species = getSpeciesList(cleanNames(SCC4_files, SCC4_ext, SCCSW_ext, SCCRY_ext), cleanNames(SCCSW_files, SCC4_ext, SCCSW_ext, SCCRY_ext), cleanNames(SCCRY_files, SCC4_ext, SCCSW_ext, SCCRY_ext))

for spp in species:
    Table[spp] = OrderedDict()
    for ab in '4', 'SW', 'RY':
        Table[spp][ab] = OrderedDict()
        for sl in SigLevs:
            Table[spp][ab][sl] = float('nan')

def getDataFromFile(f, t, spp, ab, SigLevs):
    data = [re.split('\s+', line.strip()) for line in open(f).readlines()]
    for sl in SigLevs:
        if all([sl != 'max', sl != 'min']):
            for line in data:
                d_sl, d_scc, d_seg = float(line[0]), float(line[1]), int(line[2])
                if d_sl == sl: t[spp][ab][sl] = d_scc
        elif sl == 'max':
            d_scc = max([float(line[1]) for line in data])
            t[spp][ab][sl] = d_scc
        elif sl == 'min':
            d_scc = min([float(line[1]) for line in data])
            t[spp][ab][sl] = d_scc

for spp in species:
    getDataFromFile(os.path.join(SCC4_dir, spp + '.' + SCC4_ext), Table, spp, '4', SigLevs)
    getDataFromFile(os.path.join(SCCSW_dir, spp + '.' + SCCSW_ext), Table, spp, 'SW', SigLevs)
    getDataFromFile(os.path.join(SCCRY_dir, spp + '.' + SCCRY_ext), Table, spp, 'RY', SigLevs)

with open('TableSCC.txt', 'wt') as handle:
    header = ['species']
    for sl in SigLevs:
        header.extend(['SCC4_' + str(sl), 'SCCSW_' + str(sl), 'SCCRY_' + str(sl)])
    header = '#' + '\t'.join(header) + '\n'
    handle.write(header)
    for spp in species:
        data = [spp]
        for sl in SigLevs:
            data.extend([str(Table[spp]['4'][sl]), str(Table[spp]['SW'][sl]), str(Table[spp]['RY'][sl])])
        data = '\t'.join(data) + '\n'
        handle.write(data)
