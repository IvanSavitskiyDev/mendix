from setuptools import setup, find_packages


REQUIRES = ["asyncworker", "aiohttp", "aiohttp-devtools", "boto3"]

TESTS_REQUIRE = ["pytest", "pytest-asyncio"]

setup(
    name="webapp",
    version="1.0",
    description="webapp",
    classifiers=["Programming Language :: Python", "Framework :: AsyncIO"],
    author="",
    author_email="",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    extras_require={"test": TESTS_REQUIRE},
    install_requires=REQUIRES,
)
