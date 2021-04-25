import argparse

from . import analysis


def execute_from_cli():
    parser = argparse.ArgumentParser("Esat")

    parser.add_argument("embryos", nargs="*", help="Folders containing embryo images")
    parser.add_argument("-o", "--outfolder", default="esat_report")

    args = parser.parse_args()
    analysis.run(*args.embryos, outfolder=args.outfolder)
