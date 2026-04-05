from setuptools import setup, find_packages

setup(
    name="task-manager",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        line.strip()
        for line in open("requirements.txt").readlines()
        if line.strip() and not line.startswith("#")
    ],
    author="Task Manager Team",
    description="Full Stack Task Management System",
    python_requires=">=3.8",
)