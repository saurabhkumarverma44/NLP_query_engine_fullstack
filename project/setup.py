"""
Universal NLP Query Engine Setup Script
Installs and configures the Universal NLP Query Engine system
"""

from setuptools import setup, find_packages
import os
import sys
from pathlib import Path

# Read version from version file
def get_version():
    version_file = Path(__file__).parent / "VERSION"
    if version_file.exists():
        return version_file.read_text().strip()
    return "2.0.0"

# Read long description from README
def get_long_description():
    readme_file = Path(__file__).parent / "README.md"
    if readme_file.exists():
        return readme_file.read_text(encoding="utf-8")
    return "Universal NLP Query Engine - AI-powered natural language query system for any database"

# Read requirements from requirements.txt
def get_requirements():
    requirements_file = Path(__file__).parent / "backend" / "requirements.txt"
    if requirements_file.exists():
        with open(requirements_file) as f:
            return [line.strip() for line in f if line.strip() and not line.startswith("#")]
    return []

# Development requirements
dev_requirements = [
    "pytest>=7.4.0",
    "pytest-asyncio>=0.21.0",
    "pytest-cov>=4.1.0",
    "black>=23.7.0",
    "flake8>=6.0.0",
    "mypy>=1.5.0",
    "pre-commit>=3.4.0",
    "bandit>=1.7.5",
    "safety>=2.3.0",
    "isort>=5.12.0",
]

# Documentation requirements
docs_requirements = [
    "mkdocs>=1.5.0",
    "mkdocs-material>=9.2.0",
    "mkdocstrings>=0.22.0",
    "mkdocs-gen-files>=0.5.0",
    "mkdocs-literate-nav>=0.6.0",
]

# Performance testing requirements
perf_requirements = [
    "locust>=2.16.0",
    "memory-profiler>=0.61.0",
    "py-spy>=0.3.14",
]

# All extra requirements
all_requirements = dev_requirements + docs_requirements + perf_requirements

setup(
    name="universal-nlp-query-engine",
    version=get_version(),
    description="AI-powered natural language query system for any database",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    author="Universal NLP Query Engine Team",
    author_email="support@universal-nlp-engine.com",
    url="https://github.com/universal-nlp-engine/universal-nlp-query-engine",
    project_urls={
        "Documentation": "https://docs.universal-nlp-engine.com",
        "Source Code": "https://github.com/universal-nlp-engine/universal-nlp-query-engine",
        "Issue Tracker": "https://github.com/universal-nlp-engine/universal-nlp-query-engine/issues",
    },
    
    # Package configuration
    packages=find_packages(where="backend", exclude=["tests*", "*.tests", "*.tests.*"]),
    package_dir={"": "backend"},
    
    # Python version requirement
    python_requires=">=3.8",
    
    # Dependencies
    install_requires=get_requirements(),
    extras_require={
        "dev": dev_requirements,
        "docs": docs_requirements,
        "perf": perf_requirements,
        "all": all_requirements,
    },
    
    # Package data
    include_package_data=True,
    package_data={
        "": ["*.yaml", "*.yml", "*.json", "*.toml", "*.cfg", "*.ini"],
    },
    
    # Entry points for CLI commands
    entry_points={
        "console_scripts": [
            "universal-nlp=backend.cli:main",
            "nlp-query=backend.cli:query_command",
            "nlp-server=backend.cli:server_command",
            "nlp-setup=backend.cli:setup_command",
        ],
    },
    
    # Classification
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Database",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: Linguistic",
        "Framework :: FastAPI",
        "Environment :: Web Environment",
    ],
    
    # Keywords
    keywords="nlp natural-language-processing database query sql mongodb postgresql mysql ai machine-learning",
    
    # License
    license="MIT",
    
    # Zip safe
    zip_safe=False,
    
    # Custom commands
    cmdclass={},
    
    # Minimum versions for critical dependencies
    setup_requires=[
        "wheel>=0.40.0",
        "setuptools>=65.0.0",
    ],
)

# Post-installation setup
def post_install():
    """Run post-installation setup tasks"""
    print("\n" + "="*60)
    print("🚀 Universal NLP Query Engine Installation Complete!")
    print("="*60)
    
    print("\n📋 Next Steps:")
    print("1. Set up your environment variables:")
    print("   cp .env.example .env")
    print("   # Edit .env with your database connections")
    
    print("\n2. Initialize the database:")
    print("   universal-nlp setup --init-db")
    
    print("\n3. Start the development server:")
    print("   universal-nlp server --dev")
    
    print("\n4. Open your browser to:")
    print("   http://localhost:3000 (Frontend)")
    print("   http://localhost:8000/docs (API Documentation)")
    
    print("\n📚 Documentation:")
    print("   https://docs.universal-nlp-engine.com")
    
    print("\n🔧 Configuration:")
    print("   Edit config/settings.py for advanced configuration")
    
    print("\n💡 Quick Start:")
    print("   1. Connect to a database (PostgreSQL, MySQL, MongoDB, or upload CSV)")
    print("   2. Ask natural language questions like:")
    print("      - 'How many employees do we have?'")
    print("      - 'Show me sales by month'")
    print("      - 'What are the top products?'")
    
    print("\n🛠️  Supported Data Sources:")
    print("   ✅ PostgreSQL  ✅ MySQL     ✅ SQLite")
    print("   ✅ MongoDB     ✅ CSV Files ✅ JSON Files")
    print("   ✅ Excel       ✅ Word Docs ✅ PDF Files")
    
    print("\n🎯 Features:")
    print("   ✨ Natural Language Queries")
    print("   🧠 AI-Powered Schema Discovery")  
    print("   📊 Smart Data Visualizations")
    print("   🔗 Universal Database Support")
    print("   ⚡ Intelligent Caching")
    print("   📱 Responsive Web Interface")
    
    print("\n" + "="*60)
    print("Happy querying! 🎉")
    print("="*60 + "\n")

if __name__ == "__main__":
    # Check if this is being run for installation
    if "install" in sys.argv or "develop" in sys.argv:
        # Run the setup
        setup()
        
        # Run post-installation tasks if not in CI/automated environment
        if not os.getenv("CI") and not os.getenv("AUTOMATED_INSTALL"):
            post_install()
    else:
        # Just run setup for other commands (like sdist, bdist_wheel)
        setup()