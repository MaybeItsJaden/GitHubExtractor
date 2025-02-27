from setuptools import setup, find_packages

setup(
    name="github-extractor",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "requests>=2.25.0",
        "PyQt6>=6.0.0",
    ],
    entry_points={
        "console_scripts": [
            "github-extractor=github_extractor:main",
        ],
    },
    author="Your Name",
    author_email="your.email@example.com",
    description="A tool to extract and analyze GitHub repositories",
    keywords="github, repository, extraction",
    url="https://github.com/yourusername/github-extractor",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.8",
) 