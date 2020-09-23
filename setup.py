import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="style_transfer_snip", # Replace with your own username
    version="1.0.0",
    author="Conor Kirby",
    author_email="conorkirby1@gmail.com",
    description="GUI for applying Style Transfer models on screenshots",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ckirby19/style-transfer-snipping-tool",
    packages=setuptools.find_packages(),
    install_requires=[
        "dataclasses==0.6",
        "imutils==0.5.3",
        "numpy==1.19.2",
        "opencv-python==4.4.0.44",
        "Pillow==7.2.0",
        "PyQt5==5.15.1",
        "PyQt5-sip==12.8.1",
        "screeninfo==0.6.5",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)