#!/bin/bash

# Build Lambda layers for Python dependencies
# This script creates separate layers for dependencies and application code

set -e

ENVIRONMENT=${1:-dev}
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
LAYERS_DIR="$PROJECT_ROOT/layers"

echo "🏗️  Building Lambda layers for environment: $ENVIRONMENT"
echo "📁 Project root: $PROJECT_ROOT"
echo "📦 Layers directory: $LAYERS_DIR"

# Clean and create layers directory
rm -rf "$LAYERS_DIR"
mkdir -p "$LAYERS_DIR"

# Function to calculate hash of requirements.txt
calculate_requirements_hash() {
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        shasum -a 256 "$PROJECT_ROOT/requirements.txt" | cut -d' ' -f1
    else
        # Linux
        sha256sum "$PROJECT_ROOT/requirements.txt" | cut -d' ' -f1
    fi
}

# Function to build dependencies layer
build_dependencies_layer() {
    local deps_hash=$(calculate_requirements_hash)
    local layer_dir="$LAYERS_DIR/dependencies-$deps_hash"
    local layer_zip="$LAYERS_DIR/dependencies-layer-$deps_hash.zip"

    echo "📦 Dependencies hash: $deps_hash"

    # Check if layer already exists
    if [ -f "$layer_zip" ]; then
        echo "✅ Dependencies layer already exists: $layer_zip"
        echo "$deps_hash" > "$LAYERS_DIR/dependencies-hash.txt"
        return 0
    fi

    echo "🔨 Building dependencies layer..."

    # Create layer directory structure
    mkdir -p "$layer_dir/python"

    # Install dependencies to layer directory
    echo "📦 Installing Python dependencies..."
    pip install -r "$PROJECT_ROOT/requirements.txt" --target "$layer_dir/python" --upgrade --platform manylinux2014_x86_64 --implementation cp --python-version 3.11 --only-binary=:all:

    # Remove unnecessary files to reduce layer size
    echo "🧹 Cleaning up unnecessary files..."
    find "$layer_dir/python" -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
    find "$layer_dir/python" -name "*.pyc" -delete 2>/dev/null || true
    find "$layer_dir/python" -name "*.pyo" -delete 2>/dev/null || true
    find "$layer_dir/python" -name "*.dist-info" -type d -exec rm -rf {} + 2>/dev/null || true
    find "$layer_dir/python" -name "*.egg-info" -type d -exec rm -rf {} + 2>/dev/null || true
    find "$layer_dir/python" -name "tests" -type d -exec rm -rf {} + 2>/dev/null || true
    find "$layer_dir/python" -name "test" -type d -exec rm -rf {} + 2>/dev/null || true

    # Create zip file
    echo "📦 Creating dependencies layer zip..."
    (cd "$layer_dir" && zip -r9 "$layer_zip" python/ -x "*.pyc" "*.pyo" "*/__pycache__/*")

    # Store hash for deployment
    echo "$deps_hash" > "$LAYERS_DIR/dependencies-hash.txt"

    # Clean up temporary directory
    rm -rf "$layer_dir"

    local layer_size=$(du -h "$layer_zip" | cut -f1)
    echo "✅ Dependencies layer created: $layer_zip ($layer_size)"
}

# Function to build application layer
build_application_layer() {
    local layer_dir="$LAYERS_DIR/application"
    local layer_zip="$LAYERS_DIR/application-layer.zip"

    echo "🔨 Building application layer..."

    # Clean previous application layer
    rm -rf "$layer_dir" "$layer_zip"
    mkdir -p "$layer_dir/python"

    # Copy application source code
    echo "📄 Copying application source code..."
    cp -r "$PROJECT_ROOT/src" "$layer_dir/python/"
    cp "$PROJECT_ROOT/lambda_handler.py" "$layer_dir/python/"

    # Clean up Python cache files
    find "$layer_dir/python" -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
    find "$layer_dir/python" -name "*.pyc" -delete 2>/dev/null || true
    find "$layer_dir/python" -name "*.pyo" -delete 2>/dev/null || true

    # Create zip file
    echo "📦 Creating application layer zip..."
    (cd "$layer_dir" && zip -r9 "$layer_zip" python/)

    # Clean up temporary directory
    rm -rf "$layer_dir"

    local layer_size=$(du -h "$layer_zip" | cut -f1)
    echo "✅ Application layer created: $layer_zip ($layer_size)"
}

# Function to show layer information
show_layer_info() {
    echo ""
    echo "📊 Layer Summary:"
    echo "=================="

    if [ -f "$LAYERS_DIR/dependencies-hash.txt" ]; then
        local deps_hash=$(cat "$LAYERS_DIR/dependencies-hash.txt")
        local deps_layer="$LAYERS_DIR/dependencies-layer-$deps_hash.zip"
        if [ -f "$deps_layer" ]; then
            local deps_size=$(du -h "$deps_layer" | cut -f1)
            echo "📦 Dependencies layer: dependencies-layer-$deps_hash.zip ($deps_size)"
        fi
    fi

    if [ -f "$LAYERS_DIR/application-layer.zip" ]; then
        local app_size=$(du -h "$LAYERS_DIR/application-layer.zip" | cut -f1)
        echo "📄 Application layer: application-layer.zip ($app_size)"
    fi

    echo ""
    echo "💡 Layer benefits:"
    echo "   - Dependencies only rebuild when requirements.txt changes"
    echo "   - Application layer rebuilds on every deploy (smaller, faster)"
    echo "   - Significant deployment time savings for code-only changes"
    echo ""
}

# Main execution
main() {
    # Check if we're in the right directory
    if [ ! -f "$PROJECT_ROOT/requirements.txt" ]; then
        echo "❌ requirements.txt not found in project root: $PROJECT_ROOT"
        exit 1
    fi

    # Build layers
    build_dependencies_layer
    build_application_layer
    show_layer_info

    echo "✅ Lambda layers build completed!"
}

# Run main function
main "$@"