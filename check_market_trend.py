"""
Quick Market Trend Checker
Shows if prices went up or down during simulation
"""

import json
from pathlib import Path

def check_market_trend():
    """Check if market went up or down"""
    
    print("=" * 80)
    print("MARKET TREND ANALYSIS")
    print("=" * 80)
    
    # Load StockAgent results (has all trades)
    filepath = Path("results/stockagent_results.json")
    
    if not filepath.exists():
        print("\n❌ No results file found!")
        print("   Run simulation first: python run_azure_simulation.py")
        return
    
    with open(filepath, 'r') as f:
        data = json.load(f)
    
    trades = data.get('trades', [])
    
    if not trades:
        print("\n❌ No trades found!")
        return
    
    # Get first and last prices
    first_trade = trades[0]
    last_trade = trades[-1]
    
    start_price = first_trade.get('entry_price', 0)
    end_price = last_trade.get('exit_price', 0)
    
    # Calculate change
    price_change = end_price - start_price
    price_change_pct = ((end_price / start_price) - 1) * 100 if start_price > 0 else 0
    
    print(f"\nSimulation Period:")
    print(f"  First Trade Entry:  ${start_price:.2f}")
    print(f"  Last Trade Exit:    ${end_price:.2f}")
    print(f"  Price Change:       ${price_change:.2f} ({price_change_pct:+.2f}%)")
    
    print("\nMarket Trend:")
    if price_change_pct > 5:
        print("  📈 STRONG UPTREND - Market went UP significantly")
        print("     → Agents should have made money (buying low, selling high)")
        print("     → Losses indicate poor timing or bad strategy")
    elif price_change_pct > 0:
        print("  📈 SLIGHT UPTREND - Market went up a bit")
        print("     → Small profits expected")
        print("     → Losses indicate trading costs or bad timing")
    elif price_change_pct > -5:
        print("  📉 SLIGHT DOWNTREND - Market went down a bit")
        print("     → Small losses expected")
        print("     → This explains some of the losses")
    else:
        print("  📉 STRONG DOWNTREND - Market went DOWN significantly")
        print("     → Large losses expected (bought high, sold low)")
        print("     → Losses are mostly due to bad market, not bad strategy")
    
    # Additional statistics
    print(f"\nTotal Trades Analyzed: {len(trades)}")
    
    # Calculate average trade performance
    profits = [t.get('profit', 0) for t in trades]
    avg_profit = sum(profits) / len(profits) if profits else 0
    
    print(f"Average Profit Per Trade: ${avg_profit:.2f}")
    
    if avg_profit < 0:
        print("  ⚠️ Negative average = agents are losing on most trades")
    else:
        print("  ✅ Positive average = agents are winning on most trades")
    
    print("\n" + "=" * 80)
    print("INTERPRETATION")
    print("=" * 80)
    
    if price_change_pct < -5 and avg_profit < 0:
        print("\n✅ NORMAL: Market went down + agents lost money")
        print("   → The losses are mostly due to bad market conditions")
        print("   → Agents are behaving reasonably given the downtrend")
        print("\n💡 Try another run - market might go up!")
    
    elif price_change_pct > 5 and avg_profit < 0:
        print("\n⚠️ PROBLEM: Market went up BUT agents still lost money!")
        print("   → Agents have poor timing or bad strategies")
        print("   → Need to adjust:")
        print("      1. Make agents more conservative")
        print("      2. Improve entry/exit logic")
        print("      3. Reduce trading frequency")
    
    elif price_change_pct > 5 and avg_profit > 0:
        print("\n✅ EXCELLENT: Market went up AND agents made money!")
        print("   → Strategies are working well")
        print("   → This is the ideal scenario")
    
    else:
        print("\n📊 MIXED RESULTS: Market was relatively flat")
        print("   → Losses/gains are mostly from trading decisions")
        print("   → This tests strategy quality, not market luck")
    
    print("\n" + "=" * 80)


if __name__ == "__main__":
    check_market_trend()
