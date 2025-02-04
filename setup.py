from setuptools import setup, find_packages

setup(
    name="password-manager-analyzer",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        'pandas>=1.5.0',
        'rich>=13.0.0',
        'ttkthemes>=3.2.2',
        'openpyxl>=3.1.0'
    ],
    entry_points={
        'console_scripts': [
            'password-analyzer=password_analyzer_cli:main',
            'password-analyzer-gui=password_analyzer_gui:main'
        ],
    },
    author="Your Name",
    description="A tool to analyze password manager exports",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    keywords="password manager, security, analysis",
    python_requires='>=3.7',
) 