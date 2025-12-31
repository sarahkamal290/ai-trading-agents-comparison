"""Simple Test - Verify Everything Works"""
import sys
import os

print("="*60)
print("TESTING FRAMEWORK SETUP")
print("="*60)

# Test 1: Imports
print("\n1. Testing imports...")
try:
    from framework.simulator.lightweight_simulator import LightweightSimulator
    from framework.agents.stockagent import StockAgentTrader
    from framework.agents.tradingagents import TradingAgentsSystem
    from framework.agents.fingpt import FinGPTAgent
    print("    All imports successful")
except Exception as e:
    print(f"    Import failed: {e}")
    sys.exit(1)

# Test 2: Core packages
print("\n2. Testing core packages...")
try:
    import numpy
    import pandas
    import openai
    print("    Core packages OK")
except Exception as e:
    print(f"    Package missing: {e}")
    sys.exit(1)

# Test 3: API key
print("\n3. Checking API key...")
api_key = os.environ.get("OPENAI_API_KEY")
if api_key:
    print(f"    API key set: {api_key[:8]}...{api_key[-4:]}")
else:
    print("     API key not set (optional for testing)")

# Test 4: Create simple simulation
print("\n4. Testing simulation...")
try:
    from datetime import datetime, timedelta
    
    start = datetime.now()
    end = start + timedelta(hours=1)
    
    sim = LightweightSimulator(["STOCK"], start, end)
    
    agent = StockAgentTrader(1, "Test", 1000, "Conservative")
    sim.register_agent(1, agent)
    
    print("    Simulation setup successful")
except Exception as e:
    print(f"    Simulation failed: {e}")
    sys.exit(1)

print("\n" + "="*60)
print(" ALL TESTS PASSED!")
print("="*60)
print("\nReady to run experiments!")
print("\nNext steps:")
print("  1. Set API key: $env:OPENAI_API_KEY = 'sk-...'")
print("  2. Run comparison: python framework/experiments/run_comparison.py")
print("  3. Check results in: framework/results/")
