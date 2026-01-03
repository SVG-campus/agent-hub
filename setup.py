from setuptools import setup, find_packages

with open("README_LANGCHAIN_PACKAGE.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="langchain-agent-hub",
    version="1.0.0",
    author="Hour.IT Team",
    author_email="your-email@example.com",
    description="LangChain tool for Hour.IT Agent Hub - Crypto-native AI services",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/SVG-campus/agent-hub",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.9",
    install_requires=[
        "langchain>=0.1.0",
        "requests>=2.31.0",
        "pydantic>=2.0.0",
    ],
    keywords="langchain ai crypto payments usdc base blockchain agent",
)