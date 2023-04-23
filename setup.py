import pathlib
from setuptools import setup, find_packages

from apex_ocr import __version__

# Get the directory of this file
HERE = pathlib.Path(__file__).parent

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
    install_requires=[
        "alembic",
        "black",
        "click",
        "cycler",
        "kiwisolver",
        "matplotlib",
        "numpy",
        "opencv-python",
        "paddlepaddle-gpu",
        "paddleocr",
        "Pillow",
        "psycopg2",
        "pyparsing",
        "pytesseract",
        "python-dateutil",
        "regex",
        "rich",
        "six",
        "sqlalchemy",
    ],
)
