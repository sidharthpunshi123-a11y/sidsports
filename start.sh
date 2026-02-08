#!/bin/bash

# Sports Betting Backend - Quick Start Script

echo "🎯 Sports Betting Backend - Quick Start"
echo "========================================"
echo ""

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.9 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "✓ Python version: $PYTHON_VERSION"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚙️  Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env and add your ODDS_API_KEY"
    echo "   Get a free key at: https://the-odds-api.com"
    echo ""
fi

# Check PostgreSQL
if ! command -v psql &> /dev/null; then
    echo "⚠️  PostgreSQL not found. Options:"
    echo "   1. Install PostgreSQL locally"
    echo "   2. Use Docker: docker-compose up -d db"
    echo "   3. Use a cloud database (ElephantSQL, Railway, etc.)"
    echo ""
else
    echo "✓ PostgreSQL found"
fi

# Initialize database
echo "🗄️  Initializing database..."
python3 -c "from app.database import init_db; init_db()" 2>/dev/null && echo "✓ Database initialized" || echo "⚠️  Database initialization failed (check if PostgreSQL is running)"

echo ""
echo "✨ Setup complete!"
echo ""
echo "📋 Next steps:"
echo "   1. Edit .env and add your ODDS_API_KEY"
echo "   2. Ensure PostgreSQL is running"
echo "   3. Run: python3 -m uvicorn app.main:app --reload"
echo "   4. Visit: http://localhost:8000/docs"
echo ""
echo "🐳 Alternative: Use Docker"
echo "   docker-compose up"
echo ""
