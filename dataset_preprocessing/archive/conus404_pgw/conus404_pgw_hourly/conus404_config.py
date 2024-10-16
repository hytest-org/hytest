#!/usr/bin/env python3

#      Author: Parker Norton (pnorton@usgs.gov)
#        Date: 2024-05-08
# Description: Configuration class for conus404-pgw processing
#              YAML is used for the backend

import ruamel.yaml
from typing import Dict, List, Optional, Union, Any

ConfigElem = Union[int, float, str, List[Any], Dict[Any, Any]]

default_values: Dict[str, ConfigElem] = dict(wrf_dir='',
                                             wrf_file_pat='',
                                             target_dir='',
                                             target_pat='',
                                             temp_dir='',
                                             constants_file='',
                                             metadata_file='',
                                             vars_file='',
                                             dst_zarr='',
                                             account='',
                                             queue='',
                                             memory_per_job='',
                                             walltime='00:15:00',
                                             interface='ib0',
                                             cores_per_job=2,
                                             processes=2,
                                             max_jobs=6,
                                             num_chunks_per_job=1,
                                             base_date='1979-10-01',
                                             end_date='1979-10-01',
                                             num_days=6,
                                             chunk_plan={})


class Cfg(object):
    """Configuration class for the NHM utilities."""

    def __init__(self, filename: str,
                 cmdline: Optional[str] = None):
        """Init method for Cfg class.

        :param filename: Configuration filename
        :param cmdline: Currently unused.
        """

        # yaml.add_representer(OrderedDict, dict_representer)
        # yaml.add_constructor(_mapping_tag, dict_constructor)
        self.yaml = ruamel.yaml.YAML()

        self.__cfgdict: Dict[str, ConfigElem] = {}
        self.__cmdline = cmdline
        self.load(filename)

    def __str__(self) -> str:
        """Pretty-print the configuration items

        :returns: String of configuration parameters and values
        """

        outstr = ''

        for (kk, vv) in self.__cfgdict.items():
            outstr += f'{kk}: '

            if isinstance(vv, list):
                for ll in vv:
                    outstr += f'{ll}, '
                outstr = outstr.strip(', ') + '\n'
            else:
                outstr += f'{vv}\n'
        return outstr

    def __getattr__(self, item: str) -> ConfigElem:
        """Get value for a configuration item.

        :returns: Configuration parameter value
        """
        # Undefined attributes will look up the given configuration item
        return self.get_value(item)

    def exists(self, name: str) -> bool:
        """Tests if configuration parameter exists

        :param name: Name of configuration parameter to check
        :returns: True if parameter exists
        """
        return name in self.__cfgdict or name in default_values

    def is_empty(self, name: str) -> bool:
        """Check if list or string parameter values are empty

        :param name: Name of configuration parameter to check
        :returns: True is values is an empty list or string
        """
        cval = self.get_value(name)

        if isinstance(cval, list):
            return len(cval) == 0
        if isinstance(cval, str):
            return len(cval) == 0
        if isinstance(cval, bool):
            return False
        return True

    def get_value(self, name: str) -> ConfigElem:
        """Return the value for a given config variable.

        :param name: Name of configuration parameter
        :returns: Value(s) for the configuration parameter
        """
        try:
            return self.__cfgdict.get(name, default_values[name])
            # return self.__cfgdict[varname]
        except KeyError:
            raise KeyError(f'Configuration variable, {name}, does not exist') from None
            # return None

    def load(self, filename: str):
        """Load the YAML-format configuration file.

        :param filename: Name of YAML configuration file.
        """
        tmp = self.yaml.load(open(filename, 'r'))
        self.__cfgdict = tmp

    def update_value(self, name: str, newval: Union[List, str]):
        """Update an existing configuration variable with a new value

        :param name: Name of configuration parameter
        :param newval: New value for parameter
        """
        # print(f'update: {name}: {newval}')
        if name in self.__cfgdict:
            if isinstance(self.__cfgdict[name], list):
                if isinstance(newval, list):
                    self.__cfgdict[name] = newval
                else:
                    self.__cfgdict[name] = self.yaml_seq(newval)
            else:
                self.__cfgdict[name] = newval
        else:
            raise KeyError(f'Configuration variable, {name}, does not exist')

    def write(self, filename: str):
        """Write the current configuration out to a file.

        :param filename: Name of file to write configuration to
        """

        outfile = open(filename, 'w')
        self.yaml.dump(self.__cfgdict, outfile)

    @staticmethod
    def yaml_seq(*somelist):
        """Lists with existing flow style"""

        # Based off of: https://stackoverflow.com/questions/56937691/making-yaml-ruamel-yaml-always-dump-lists-inline
        ret = ruamel.yaml.comments.CommentedSeq(somelist)
        ret.fa.set_flow_style()
        return ret