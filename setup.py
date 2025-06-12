"""
Setup script for Art-Net LED Controller Library.
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "Art-Net LED Controller Library"

setup(
    name="artnet-led-controller",
    version="1.0.0",
    author="Art-Net LED Controller Library",
    author_email="your-email@example.com",
    description="A Python library for controlling LED fixtures using Art-Net protocol over Ethernet networks",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/artnet-led-controller",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Multimedia :: Sound/Audio",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.7",
    install_requires=[
        # No external dependencies - uses only standard library
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.800",
        ],
    },
    entry_points={
        "console_scripts": [
            "artnet-led-controller=artnet_led_controller.cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords="artnet, led, lighting, controller, wled, ethernet, network",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/artnet-led-controller/issues",
        "Source": "https://github.com/yourusername/artnet-led-controller",
        "Documentation": "https://github.com/yourusername/artnet-led-controller#readme",
    },
) 