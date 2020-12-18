import sys
import argparse
from typing import Sequence
from .meta import load
from .about import ABOUT_TEMPLATE
try:
    from . import __about__
except ImportError:  # pragma: no cover
    __about__ = None


def _main(args: argparse.Namespace):
    regarding_name, regarding_homepage = None, None
    try:
        from . import __about__ as about_regarding
        try:
            regarding_name = about_regarding.project_name.lower()
            regarding_homepage = about_regarding.homepage
        except AttributeError:  # pragma: no cover
            # During bootstrap
            pass

    except ImportError:  # pragma: no cover
        about_regarding = argparse.Namespace()
        about_regarding.project_name = "TDB"
        about_regarding.homepage = "TDB"

    project = args.project_meta
    about_py = ABOUT_TEMPLATE.format(**locals())

    args.out_file.write(f"{about_py}\n")
    args.out_file.close()


def main(args: Sequence[str] = None):
    des = __about__.description if __about__ and hasattr(__about__, "description") else None
    ver = __about__.version if __about__ and hasattr(__about__, "version") else None

    cli = argparse.ArgumentParser(prog="regarding", description=des)
    cli.add_argument("--version", action="version", version=f"%(prog)s {ver}")
    cli.add_argument("-o", "--out-file",
                     type=argparse.FileType("w", encoding='UTF-8'), default="-",
                     help="The output file, by default is file is printed to standard out.")
    args = cli.parse_args(args=args)

    try:
        project_meta = load()
    except FileNotFoundError as not_found:
        print(str(not_found), file=sys.stderr)
        status = 2
    else:
        args.project_meta = project_meta
        status = _main(args) or 0

    sys.exit(status)


if __name__ == "__main__":  # pragma: no cover
    main()
