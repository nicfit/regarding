import setuptools
from setuptools.command.build_py import build_py as _build_py


class build_py(_build_py):
    def run(self):
        import pathlib
        # Custom build logic here
        path = pathlib.Path(__file__).parent.joinpath("hi")
        path.write_text("YO")
        print("XXX Running custom build step")
        _build_py.run(self)
        print("XXX Custom build step completed")


setuptools.setup(
    cmdclass={"build_py": build_py},
)
