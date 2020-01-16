#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import logging
import pprint
import requests
import sys
import xmltodict

# Set up the logger
logger = logging.getLogger()
handler = logging.StreamHandler(stream=sys.stdout)
formatter_debug = logging.Formatter(
    '%(asctime)s [%(levelname)8s](%(funcName)s:%(lineno)d): %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S')
formatter = logging.Formatter(
    '%(asctime)s  %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# Used for large debug output
pp = pprint.PrettyPrinter(compact=True)


def init():
  parser = argparse.ArgumentParser(description="NPA Lookup")

  parser.add_argument("NPA", help="NPA to lookup")
  parser.add_argument("NXX", help="NXX to lookup")

  parser.add_argument("-d", "--debug", action="store_true",
                      help="Enable debug info")
  args = parser.parse_args()

  if args.debug:
    logger.setLevel(logging.DEBUG)
    handler.setFormatter(formatter_debug)
    logger.debug("Enabling DEBUG output")

  main(args)


def main(args):
  logger.debug("Arguments: {}".format(args))

  print(f"\nLooking up NPA: {args.NPA}  NXX: {args.NXX}\n")

  localprefixes = []

  lpdata = requests.get(f"https://localcallingguide.com/xmllocalprefix.php?npa={args.NPA}&nxx={args.NXX}")
  lpdict = xmltodict.parse(lpdata.content)

  error = lpdict['root']['lca-data'].get('error')
  if error:
    logger.debug(pp.pformat(lpdict))
    print(f"Error: {error}")

  prefixes = lpdict['root']['lca-data'].get('prefix')
  if prefixes:
    for prefix in prefixes:
      if prefix['npa'] not in localprefixes:
        localprefixes.append(prefix['npa'])

  if localprefixes:
    localprefixes.sort()
    # Remove NPA
    localprefixes.remove(args.NPA)
    # Move to beginning so we can copy into CUCDM directly
    localprefixes.insert(0, args.NPA)
    logger.debug("localprefixes is {}".format(pp.pformat(localprefixes)))
    print("Local NPAs: {}".format(",".join(localprefixes)))

  # Only check if we didn't get an error from above
  if not error:
    dpdata = requests.get(f"https://localcallingguide.com/xmldialplan.php?npa={args.NPA}")
    dpdict = xmltodict.parse(dpdata.content)
    dialplan = dpdict['root'].get('dpdata')
    if dialplan:
      print("\nDial Plan:")
      print("  Local (HNPA): {}".format(dialplan['std_hnpa_local']))
      print("  Local (FNPA): {}".format(dialplan['std_fnpa_local']))
      print("   Toll (HNPA): {}".format(dialplan['std_hnpa_toll']))
      print("   Toll (FNPA): {}".format(dialplan['std_fnpa_toll']))
      print("   Oper Assist: {}\n".format(dialplan['std_oper_assis']))


if __name__ == "__main__":
  init()
