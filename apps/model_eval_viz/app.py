import geopandas as gpd
import hvplot.pandas
import numpy as np
import pandas as pd
import panel as pn

# Initialize setup for below functions
pn.extension("plotly", "vega")
xs = np.linspace(0, np.pi)
freq = pn.widgets.FloatSlider(name="Frequency", start=0, end=10, value=2)
phase = pn.widgets.FloatSlider(name="Phase", start=0, end=np.pi)
path = 'data/steamflow_gages_v1_n5390.csv'

# Read in the dataframe 

def _get_data(_filepath:str)->gpd.dataframe:
    '''
    Reads streamflow data from a .csv and filters it based on the 'gagesII_class==ref'.
    Args:
        _filepath (str): Path to the .csv file 
    Returns:
        gpd.dataframe: the filtered geopandas data file
    '''
    read_data = geopandas.read_file(_filepath)
    filtered_data = read_data[read_data['gagesII_class'] == 'Ref']
    return filtered_data


# def sine(freq, phase):
#     return pd.DataFrame(dict(y=np.sin(xs*freq+phase)), index=xs)

# def cosine(freq, phase):
#     return pd.DataFrame(dict(y=np.cos(xs*freq+phase)), index=xs)
# dfi_sine = hvplot.bind(sine, freq, phase).interactive()
# dfi_cosine = hvplot.bind(cosine, freq, phase).interactive()

# Plotting configurations
plot_opts = dict(
    responsive=True, min_height=400,
    # Align the curves' color with the template's color
    color=pn.template.FastGridTemplate.accent_base_color
)

# Instantiate the template with widgets displayed in the sidebar
template = pn.template.FastGridTemplate(
    title="HyTEST Model Evaluation",
    sidebar=[freq, phase],
    
)
footer = pn.pane.Markdown("""For questions about this application, please visit the [Hytest Repo](https://github.com/hytest-org/hytest/issues)""" ,width=500)


# Populate the main area with plots, to demonstrate the grid-like API
template.main[0:3, 0:6] = dfi_sine.hvplot(title='Sine', **plot_opts).output()
template.main[0:3, 6:12] = dfi_cosine.hvplot(title='Cosine', **plot_opts).output()
template.main[4:, 0:12] = footer # unpack footer onto template
template.servable() 
