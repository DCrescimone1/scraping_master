#!/usr/bin/env python3
"""Debug script to check if Verpackung is in unique_features.csv"""

import csv
import os
import sys
from pathlib import Path

# Get paths (go up 2 levels from test/ to project root)
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent

# Path to your CSV file (relative to project root)
csv_path = PROJECT_ROOT / "outputs" / "unique_features.csv"

print("="*80)
print("CSV DEBUG CHECKER - Verpackung Issue")
print("="*80)
print(f"📁 Script location: {SCRIPT_DIR}")
print(f"📁 Project root: {PROJECT_ROOT}")
print(f"📁 CSV path: {csv_path}")
print()

# Check if file exists
if not csv_path.exists():
    print(f"❌ ERROR: File not found: {csv_path}")
    print(f"   Current directory: {Path.cwd()}")
    print(f"   Expected location: {csv_path.absolute()}")
    print()
    print("💡 SOLUTION: Run this command to generate the CSV:")
    print(f"   cd {PROJECT_ROOT}")
    print("   python3 BMEcat_transformer/scripts/extract_features_StandAlone.py")
    exit(1)

print(f"✅ File exists: {csv_path}")
print(f"   File size: {csv_path.stat().st_size} bytes")
print()

# Read CSV and check for Verpackung
found_verpackung = False
all_features = []

try:
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        # Get header
        fieldnames = reader.fieldnames
        print(f"📋 CSV Headers: {fieldnames}")
        print()
        
        # Read all rows
        for row in reader:
            fname_de = row.get('fname_de', '')
            all_features.append(fname_de)
            
            if 'verpackung' in fname_de.lower():
                found_verpackung = True
                print(f"✅ FOUND: Verpackung in CSV!")
                print(f"   Row: {row}")
                print()
        
        print(f"📊 Total features in CSV: {len(all_features)}")
        
        if not found_verpackung:
            print()
            print("❌ ERROR: 'Verpackung' NOT FOUND in CSV!")
            print()
            print("🔍 Features containing 'pack' or similar:")
            similar = [f for f in all_features if 'pack' in f.lower() or 'box' in f.lower()]
            for feat in similar[:10]:
                print(f"   - {feat}")
            
            if not similar:
                print("   (none found)")
        
except Exception as e:
    print(f"❌ ERROR reading CSV: {e}")
    exit(1)

print()
print("="*80)
print("NORMALIZATION TEST")
print("="*80)

import re

def normalize(s: str) -> str:
    """Same normalize function as in ai_feature_matcher.py"""
    s = s.lower().strip()
    s = re.sub(r'[-\s]+', '', s)
    return s

test_names = ["Verpackung", "verpackung", "VERPACKUNG", " Verpackung "]

print("Testing normalization:")
for name in test_names:
    normalized = normalize(name)
    print(f"   '{name}' → '{normalized}'")

print()
print("Testing CSV matching:")
csv_verpackung = "Verpackung"  # From CSV
test_input = "Verpackung"      # From AI

print(f"   CSV:   '{csv_verpackung}' → '{normalize(csv_verpackung)}'")
print(f"   Input: '{test_input}' → '{normalize(test_input)}'")
print(f"   Match: {normalize(csv_verpackung) == normalize(test_input)}")

print()
print("="*80)