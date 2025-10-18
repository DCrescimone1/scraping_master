#!/usr/bin/env python3
"""Test if AIFeatureMatcher correctly loads and checks Verpackung"""

import sys
from pathlib import Path

# Add project root to path (go up 2 levels from test/ to project root)
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Also add the BMEcat_transformer package directory so 'utils' absolute import resolves
BMECAT_DIR = PROJECT_ROOT / "BMEcat_transformer"
if str(BMECAT_DIR) not in sys.path:
    sys.path.insert(0, str(BMECAT_DIR))

print("="*80)
print("AI FEATURE MATCHER DEBUG TEST")
print("="*80)
print(f"📁 Script location: {SCRIPT_DIR}")
print(f"📁 Project root: {PROJECT_ROOT}")
print()

# Import the matcher
try:
    from BMEcat_transformer.processors.ai_feature_matcher import AIFeatureMatcher
    print("✅ Successfully imported AIFeatureMatcher")
except ImportError as e:
    print(f"❌ Failed to import AIFeatureMatcher: {e}")
    print(f"\nDEBUG INFO:")
    print(f"   sys.path: {sys.path[:3]}")
    print(f"   Current dir: {Path.cwd()}")
    exit(1)

# Setup paths (relative to project root)
csv_path = PROJECT_ROOT / "outputs" / "unique_features.csv"
prompt_path = PROJECT_ROOT / "BMEcat_transformer" / "prompts" / "xml_specs_mapping.yaml"
ai_features_path = PROJECT_ROOT / "outputs" / "ai_generated_features.json"

print(f"\n📁 Checking paths:")
print(f"   CSV path: {csv_path} - {'✅ exists' if csv_path.exists() else '❌ NOT FOUND'}")
print(f"   Prompt path: {prompt_path} - {'✅ exists' if prompt_path.exists() else '❌ NOT FOUND'}")
print(f"   AI features: {ai_features_path} - {'✅ exists' if ai_features_path.exists() else '⚠️  will be created'}")

if not csv_path.exists():
    print("\n❌ ERROR: CSV file not found!")
    print("   You need to run extract_features.py first to generate unique_features.csv")
    exit(1)

# Create matcher instance (without API key since we're just testing CSV loading)
print("\n🔧 Initializing AIFeatureMatcher...")
matcher = AIFeatureMatcher(
    api_key="test_key",
    model="test_model",
    base_url="test_url",
    confidence_threshold=0.7,
    prompt_path=str(prompt_path),
    csv_path=str(csv_path),
    ai_features_path=str(ai_features_path)
)

# Load references
print("\n📥 Loading CSV references...")
success = matcher.load_references()

if not success:
    print("❌ Failed to load references!")
    exit(1)

print(f"✅ Loaded {len(matcher.allowed_features)} features from CSV")

# Test if Verpackung is found
print("\n"+"="*80)
print("TESTING: _is_feature_in_csv('Verpackung')")
print("="*80)

test_features = [
    "Verpackung",
    "verpackung",
    "VERPACKUNG",
    " Verpackung ",
    "Akku",
    "Spannung",
    "NotInCSV"
]

print("\nTesting various feature names:")
for feat in test_features:
    result = matcher._is_feature_in_csv(feat)
    status = "✅ FOUND" if result else "❌ NOT FOUND"
    print(f"   {status}: '{feat}'")

# Show first 20 features from CSV for reference
print("\n"+"="*80)
print("FIRST 20 FEATURES IN LOADED CSV:")
print("="*80)
for i, row in enumerate(matcher.allowed_features[:20]):
    fname = row.get('fname_de', 'N/A')
    fvalue = row.get('fvalue_de', 'N/A')
    print(f"{i+1:2d}. {fname:30s} = {fvalue}")

# Search for Verpackung manually in loaded data
print("\n"+"="*80)
print("MANUAL SEARCH: Looking for 'Verpackung' in loaded CSV data")
print("="*80)

found = False
for i, row in enumerate(matcher.allowed_features):
    fname = row.get('fname_de', '')
    if 'verpackung' in fname.lower():
        found = True
        print(f"✅ FOUND at row {i+1}:")
        print(f"   fname_de: {fname}")
        print(f"   fname_fr: {row.get('fname_fr', 'N/A')}")
        print(f"   fname_it: {row.get('fname_it', 'N/A')}")

if not found:
    print("❌ 'Verpackung' NOT FOUND in loaded CSV data!")
    print("\n🔍 Features containing 'pack', 'box', or 'emball':")
    similar = [row for row in matcher.allowed_features 
               if any(word in row.get('fname_de', '').lower() 
                     for word in ['pack', 'box', 'emball'])]
    for row in similar[:10]:
        print(f"   - {row.get('fname_de', 'N/A')}")

print("\n"+"="*80)
print("TEST COMPLETE")
print("="*80)