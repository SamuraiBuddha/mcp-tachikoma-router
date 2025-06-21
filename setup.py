from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="mcp-tachikoma-router",
    version="0.1.0",
    author="Jordan Ehrig",
    author_email="jordan@ebicinc.com",
    description="MCP server for router management - Ghost in the Shell themed",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/SamuraiBuddha/mcp-tachikoma-router",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "mcp",
        "requests>=2.31.0",
        "urllib3>=2.0.0",
    ],
    entry_points={
        "console_scripts": [
            "mcp-tachikoma-router=src.server:main",
        ],
    },
)
