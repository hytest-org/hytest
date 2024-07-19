import panel as pn
from pygeohydro import NWIS
#constants and data function calls will be in this file
nwis = NWIS()
EX_STATES = ['Alaska', 'Hawaii', 'Puerto Rico', 'Commonwealth of the Northern Mariana Islands', 'United States Virgin Islands', 'America Somoa', 'Guam', 'District of Columbia', 'American Samoa']
STREAMGAGE_SUBSET = ['nldi', 'swim', 'gfv1d1', 'camels']
