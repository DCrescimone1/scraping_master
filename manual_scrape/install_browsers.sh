#!/bin/bash
echo "🚀 Installing Playwright browsers..."
playwright install
playwright install chromium firefox
echo "✅ Both Chromium and Firefox installed successfully!"
