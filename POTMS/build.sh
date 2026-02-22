#!/bin/bash

echo "🚀 Starting build process..."
python --version

echo "📂 Current directory content:"
ls -la

echo "🎨 Collecting static files..."
python manage.py collectstatic --no-input || { echo "❌ Collectstatic failed"; exit 1; }

echo "🗄️ Running migrations..."
python manage.py migrate || { echo "❌ Migrations failed"; exit 1; }

echo "✅ Build completed successfully."
