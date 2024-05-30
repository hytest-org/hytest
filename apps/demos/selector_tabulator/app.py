from bokeh.models.widgets.tables import NumberFormatter, StringFormatter
import intake
import pandas as pd
import panel as pn
import truststore # needed on DOI internal network

truststore.inject_into_ssl()
pn.extension("tabulator")

url = "https://raw.githubusercontent.com/hytest-org/hytest/main/dataset_catalog/hytest_intake_catalog.yml"
cat = intake.open_catalog(url)

# access tutorial catalog
conus404_drb_cat = cat["conus404-drb-eval-tutorial-catalog"]

# get list of datasets for descriptive statistics
datasets = [dataset for dataset in list(conus404_drb_cat) if "desc" in dataset]

dataset_select = pn.widgets.Select(
    description = "Select a Dataset",
    name="Dataset",
    options=datasets
)

@pn.cache(per_session=True)
def _get_data(_dataset: str, _catalog: intake.Catalog = conus404_drb_cat) -> pd.DataFrame:
    """Reaches and caches data from intake catalog."""

    return _catalog[_dataset].read()


def _get_description(_dataset: str, _catalog:intake.Catalog = conus404_drb_cat) -> str:
    """Returns description of dataset."""

    _description = _catalog[_dataset].description

    return _description

def create_bokeh_formatters(column_dict: dict) -> dict:
    """Create a dynamic list of formatted columns."""

    formatters = {}

    for column, dtype in column_dict.items():
        if dtype == "float":
            formatters[column] = NumberFormatter(format="0.00")
        if dtype == "str":
            formatters[column] = StringFormatter()

    return formatters

@pn.depends(dataset_select)
def construct_tabulator(dataset: str, catalog:intake.Catalog = conus404_drb_cat) -> pn.Column:
    """Create tabulator object based on changes to selected dataset."""

    # create dataframe
    _df = _get_data(dataset)

    # create column formatters
    _column_formatters = create_bokeh_formatters(_df.dtypes.to_dict())

    _df_tabulator = pn.widgets.Tabulator(_df, 
                                  name="Tabulator",
                                  hidden_columns=["index"],
                                  disabled=True,
                                  theme="modern",
                                  formatters=_column_formatters
                                  )
    
    # get description for each dataset and render as html h2
    _df_description = _get_description(dataset)

    _description_display = pn.pane.Markdown(f"## {_df_description}")

    # create a column
    _df_display = pn.Column(_description_display, _df_tabulator)
    
    return _df_display


pn.Column(dataset_select,
        construct_tabulator
          ).servable()