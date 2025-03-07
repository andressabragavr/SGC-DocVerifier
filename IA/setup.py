from setuptools import setup, find_packages

setup(
    name = "IA_package",
    version = "0.1",
    packages = find_packages(where="src"),
    package_dir = {"": "src"},
    install_requires = [
        "numpy",
        "scikit-learn",
        "faiss-cpu",
        "torch",
        "torchvision",
        "torchtext",
        "langchain",
        "langchain-ollama",
        "pdf2image",
        "pytesseract",
        "flask"
    ]
)