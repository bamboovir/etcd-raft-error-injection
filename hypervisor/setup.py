from setuptools import setup

setup(
    name="hypervisor",
    version="0.0.1",
    url="https://github.com/bamboovir/hypervisor",
    author="Huiming Sun",
    author_email="bamboo1886@gmail.com",
    maintainer="Huiming Sun",
    maintainer_email="bamboo1886@gmail.com",
    long_description="",
    classifiers=[
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.10",
    ],
    packages=["."],
    include_package_data=True,
    python_requires=">=3.7,",
    install_requires=["docker==5.0.3", "fire==0.4.0"],
    extras_require={
        "dev": [
            "black",
        ]
    },
    entry_points={"console_scripts": ["hypervisor = hypervisor.raft_test:main"]},
)
