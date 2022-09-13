#!/usr/bin/env python
# coding: utf-8
# pylint: disable=fixme
"""
    Attempts to auto-configure the jupyter server for use in Pangeo-style stack
"""

import os
import sys
import json
import random
import logging
import argparse

from socket import gethostname
from notebook.auth import passwd as nb_passwd
from jupyter_core.paths import jupyter_config_dir
from OpenSSL import crypto


def self_signed_cert(      # pylint: disable=R0913,C0103
        email="invalid@usgs.gov",
        C="US",
        ST="Virginia",
        L="Reston",
        O="DOI",
        OU="USGS",
        CN="Unknown"):
    """
    The variable names are defined by the metadata standard for certificates (OpenSSL, X.509).
    The defaults supplied here are specific to USGS certificates.  When you call this function,
    you shoule *REALLY* give a proper email address and a proper 'common name' (CN). But even
    if you don't, you'll get a self-signed cert at the end.... it's just better if it is properly
    populated with meaningful values.

    Certificate-generating code adapted from:
    https://stackoverflow.com/questions/27164354/create-a-self-signed-x509-certificate-in-python
    """
    serialno=0
    validitystart_seconds=0
    validityend_seconds = 10*365*24*60*60
    k_ey = crypto.PKey()
    k_ey.generate_key(crypto.TYPE_RSA, 4096)
    # create a self-signed cert
    cert = crypto.X509()

    cert.get_subject().C = C
    cert.get_subject().ST = ST
    cert.get_subject().L = L
    cert.get_subject().O = O
    cert.get_subject().OU = OU
    cert.get_subject().CN = CN
    cert.get_subject().emailAddress = email
    cert.set_serial_number(serialno)
    cert.gmtime_adj_notBefore(validitystart_seconds)
    cert.gmtime_adj_notAfter(validityend_seconds)
    cert.set_issuer(cert.get_subject())
    cert.set_pubkey(k_ey)
    cert.sign(k_ey, 'sha512')
    return [cert, k_ey]

# Here we go...
if __name__ == "__main__":
    if os.environ.get('DEBUG', False):
        logging.basicConfig(level=logging.DEBUG)
        logging.debug("debug is on")
    else:
        logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser()
    parser.add_argument("--port",
        type=int,
        help="Configure jupyter server to listen on this port")
    parser.add_argument("--ssl",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="Configure for SSL and https (or not)")
    argv = parser.parse_args()

    # NOTE: the Jupyter config directory must exist before we try to write files there. It likely
    # doesn't if this really is the start of our user's jupyter configuration.
    j_confDir = jupyter_config_dir()
    try:
        if not os.path.exists(j_confDir):
            logging.debug("Creating config in %s", j_confDir)
            os.mkdir(j_confDir)
    except OSError:
        logging.error("Unable to set up Jupyter configuration in %s", j_confDir)
        raise
    # Where do things go?  ....
    username = os.environ.get('USER', 'root')
    hostname = gethostname()
    keyFile = os.path.join(j_confDir, f"{username}_KEY.key")
    certFile = os.path.join(j_confDir, f"{username}_CERT.pem")
    jsonFile = os.path.join(j_confDir, "jupyter_server_config.json")

    # PORT
    if not argv.port:
        logging.debug("Port is not specified... I'll pick a random port number from [8400..9400]")
        argv.port = random.choice(range(8400, 9401))
    if argv.port <= 1024:
        logging.error("You can't listen on a reserved port (port number below 1024)")
        sys.exit(0)
    logging.debug("Setting up your Jupyter server to listen on port %i ...", argv.port)

    # PASSWD HASH
    try:
        print("\nSet the access password for connecting to this Jupyter server ...")
        PW = nb_passwd()
    except ValueError:
        logging.info("Unable to get a matching pair of Passwords... Giving up.")
        sys.exit(-1)
    except KeyboardInterrupt:
        logging.debug("Keyboard Interrupt == ABORT")
        sys.exit(-1)

    ## We have enough info to fill this in now...
    master_config = {
        "ServerApp": {
            "open_browser": False,
            "password": PW,
            "certfile" : certFile,
            "keyfile" : keyFile,
            "ip": "0.0.0.0",
            "port" : argv.port,
            "allow_remote_access": True
        }
    }

    # KEY & CERT (if SSL requested)
    if argv.ssl:
        logging.debug("Generating SSL certificate for operating over https ...")
        try:
            [c, k] = self_signed_cert(email=f"{username}@{hostname}", CN="HyTEST")
            with open(certFile, "wt", encoding="utf8") as f:
                f.write(crypto.dump_certificate(crypto.FILETYPE_PEM, c).decode("utf-8"))
            with open(keyFile, "wt", encoding="utf8") as f:
                f.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, k).decode("utf-8"))
        except OSError:
            logging.info("Could not write certificate and key. SSL/https disabled.")
            # Non-fatal exception... just jemove the cert/key items from the JSON output.
            del master_config['ServerApp']['certfile']
            del master_config['ServerApp']['keyfile']
    else:
        logging.debug("Requested '--no-ssl'")
        del master_config['ServerApp']['certfile']
        del master_config['ServerApp']['keyfile']

    # WRITE JSON to ~/.jupyter/jupyter_server_config.json
    try:
        # TODO: Read existing JSON config if it already exists; The following will overwrite.
        with open(jsonFile, "wt", encoding="utf8") as f:
            f.write(json.dumps(master_config, indent=4))
    except OSError:
        # Fatal error... likely IO, but who cares?  If it doesn't work, we're done here.
        logging.error("Unable to update %s", jsonFile)
        raise

    # TODO: Don't append this to .bashrc if it is already in there.

    # bashrc = os.path.join(os.environ['HOME'], ".bashrc") #Mac
    # bashrc = os.path.join(os.environ['USERPROFILE'], ".bashrc") #WINDOWS

    # TODO: Test system agnosticness by using on Mac and Linux
    home_folder = os.path.expanduser('~')    
    bashrc = os.path.join(home_folder, ".bashrc")

    try:
        with open(bashrc, "at", encoding="utf8") as f:
            f.write("## This line added by HyTEST auto.conf.py\n")
            f.write('export DASK_DISTRIBUTED__DASHBOARD__LINK="/proxy/8787/status\n"')
    except IOError as e:
        logging.error("Unable to update ~/.bashrc")
        logging.error(e)
        sys.exit(-1)
