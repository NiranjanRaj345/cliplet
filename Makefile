# Cliplet - Production Makefile

.PHONY: install uninstall test clean build package help

# Installation
install:
	@echo "Installing Cliplet..."
	./scripts/install.sh

uninstall:
	@echo "Uninstalling Cliplet..."
	./scripts/uninstall.sh

# Development
test:
	@echo "Running tests..."
	python3 -m pytest tests/ -v

test-coverage:
	@echo "Running tests with coverage..."
	python3 -m pytest tests/ --cov=src/cliplet --cov-report=html

lint:
	@echo "Running linting..."
	python3 -m flake8 src/ tests/
	python3 -m mypy src/

format:
	@echo "Formatting code..."
	python3 -m black src/ tests/

# Build and package
build:
	@echo "Building application..."
	python3 setup.py build

package-rpm:
	@echo "Building RPM package..."
	cd packaging/rpm && rpmbuild -ba cliplet.spec

package-deb:
	@echo "Building DEB package..."
	cd packaging/deb && dpkg-buildpackage -us -uc

clean:
	@echo "Cleaning build artifacts..."
	rm -rf build/ dist/ *.egg-info/
	find . -type d -name __pycache__ -delete
	find . -type f -name "*.pyc" -delete

# Help
help:
	@echo "Available targets:"
	@echo "  install      - Install the application"
	@echo "  uninstall    - Uninstall the application"
	@echo "  test         - Run tests"
	@echo "  test-coverage - Run tests with coverage report"
	@echo "  lint         - Run code linting"
	@echo "  format       - Format code with black"
	@echo "  build        - Build the application"
	@echo "  package-rpm  - Build RPM package"
	@echo "  package-deb  - Build DEB package"
	@echo "  clean        - Clean build artifacts"
	@echo "  help         - Show this help message"
