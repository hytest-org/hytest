import hvplot.pandas
import numpy as np
import panel as pn
import pandas as pd
pn.extension("plotly", "vega")


xs = np.linspace(0, np.pi)

freq = pn.widgets.FloatSlider(name="Frequency", start=0, end=10, value=2)
phase = pn.widgets.FloatSlider(name="Phase", start=0, end=np.pi)

def sine(freq, phase):
    return pd.DataFrame(dict(y=np.sin(xs*freq+phase)), index=xs)

def cosine(freq, phase):
    return pd.DataFrame(dict(y=np.cos(xs*freq+phase)), index=xs)

dfi_sine = hvplot.bind(sine, freq, phase).interactive()
dfi_cosine = hvplot.bind(cosine, freq, phase).interactive()

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
footer = pn.pane.Markdown("""[Hytest Repo](https://github.com/hytest-org/hytest/issues)""" ,width=500)


# Populate the main area with plots, to demonstrate the grid-like API
template.main[0:3, 0:6] = dfi_sine.hvplot(title='Sine', **plot_opts).output()
template.main[0:3, 6:12] = dfi_cosine.hvplot(title='Cosine', **plot_opts).output()
template.main[4:, 0:12] = footer # unpack footer onto template
template.servable() # use servable() rather than show() to allow CLI command `panel serve`
