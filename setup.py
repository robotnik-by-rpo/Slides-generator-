from setuptools import setup, find_packages

setup(
    name="slide-deck-generator",
    version="0.1.0",
    description="Slide generator from plan of lesson",
    author="robotnik-by-rpo",
    author_email="chikindin99@inbox.com",
    
    packages=find_packages(where="src"),
    package_dir={"": "src"},    
    
    entry_points={
        "console_scripts": [
            "slide-deck-generator = src.__main__:main",
            "slider = src.__main__:main"
        ],
    },
    
    
    install_requires=[
        "requests>=2.28",
        "pyyaml",
        "pyncclient",
        "pytest",
    ],) 