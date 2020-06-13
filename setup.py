from pathlib import Path

from setuptools import find_packages, setup

PACKAGE_ROOT = Path(__file__).parent
VERSION = PACKAGE_ROOT / "version.txt"


def read_requirements(name: str):
    p = PACKAGE_ROOT.joinpath(name)
    reqs = []
    for line in p.read_text().splitlines():
        if not line or line.startswith("#"):
            continue
        req = line
        req = req.split("# ")[0].strip()
        if req.startswith("file:"):
            relative = Path(req[len("file:"):])
            virtual = Path("localhost", PACKAGE_ROOT.relative_to("/"), relative)
            req = f"{relative.name} @ file://{virtual}"
        reqs.append(req)
    return reqs


setup(
    name="patray",
    version=VERSION.read_text().strip(),
    packages=find_packages(),
    url="https://github.com/pohmelie/patray",
    author="pohmelie",
    author_email="multisosnooley@gmail.com",
    long_description=Path("readme.md").read_text(),
    long_description_content_type="text/markdown",
    license="MIT",
    license_file="license.txt",
    package_data={
        "": ["*.txt", "*.template"],
    },
    install_requires=read_requirements("requirements/production.txt"),
    extras_require={
        "dev": read_requirements("requirements/dev.txt"),
    },
)
