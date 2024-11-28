from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

install_requires = [

]

setup(
    name='localcosmos_app_kit_taxonomy',
    version='0.1.5',
    description='Local Cosmos Taxonomy django app',
    long_description=long_description,
    long_description_content_type="text/markdown",
    license='The MIT License',
    platforms=['OS Independent'],
    keywords='django, localcosmos, localcosmos server, biodiversity, taxonomy',
    author='Thomas Uher',
    author_email='thomas.uher@sisol-systems.com',
    url='https://github.com/localcosmos/app-kit',
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    include_package_data=True,
    install_requires=install_requires,
)
