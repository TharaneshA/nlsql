from setuptools import setup, find_packages

setup(
    name="nlsql",
    version="0.1.0",
    description="Natural Language to SQL CLI Tool",
    author="Your Name",
    author_email="your.email@example.com",
    packages=find_packages(),
    install_requires=[
        "mysql-connector-python>=8.0.0",
        "pandas>=1.0.0",
        "requests>=2.0.0"
    ],
    entry_points={
        "console_scripts": [
            "nlsql=cli:app"
        ]
    },

    py_modules=["cli"],
    python_requires=">=3.7",
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: MIT License"
    ],
)