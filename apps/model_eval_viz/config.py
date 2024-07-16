import panel as pn
EX_STATES = ['Alaska', 'Hawaii', 'Puerto Rico', 'Commonwealth of the Northern Mariana Islands','United States Virgin Islands','America Somoa','Guam','District of Columbia','American Samoa']
entered_points = pn.widgets.TextInput(
    name='Streamgage Site ID', 
    placeholder='Streamgage Site ID #',
    description='Enter a column delimited list e.g. 01022500, 01022502',
    
    )
