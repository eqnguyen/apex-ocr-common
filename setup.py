import pathlib
from typing import List

from setuptools import find_packages, setup

from apex_ocr import __version__

# Get the directory of this file
HERE = pathlib.Path(__file__).parent


def parse_requirements(
    req_path: str = "requirements.txt", pin_mode: str = "loose"
) -> List:
    """Parse requirements file to return a list of requirements.

    Args:
        req_path (str, optional): Path to requirements file. Defaults to 'requirements.txt'.
        pin_mode (str, optional): Mode to use for pinning packackages. Defaults to 'loose'.
            "free": Remove all constraints
            "loose": Set the versions as package lower bounds
            "strict": Replace all bounds with equals

    Raises:
        KeyError: If pin_mode is not in ["free", "loose", "strict"]

    Returns:
        list: List of requirements with updated package pins.
    """

    from pip._internal.network.session import PipSession
    from pip._internal.req import parse_requirements

    requirements = []

    for req in parse_requirements(req_path, session=PipSession()):
        if pin_mode == "free":
            requirements.append(req.requirement.split(" ")[0])
        elif pin_mode == "loose":
            requirements.append(req.requirement.replace("==", ">="))
        elif pin_mode == "strict":
            requirements.append(req.requirement.replace(">=", "=="))
        else:
            raise KeyError(pin_mode)

    return requirements


REQUIREMENTS = parse_requirements("requirements.txt")

setup(
    name="apex_ocr",
    version=__version__,
    description="OCR for Apex Legends",
    long_description=(HERE / "README.md").read_text(),
    long_description_content_type="text/markdown",
    author="Eric Nguyen",
    license="MIT",
    python_requires=">=3.8",
    packages=find_packages(),
    include_package_data=True,
    install_requires=REQUIREMENTS,
)
