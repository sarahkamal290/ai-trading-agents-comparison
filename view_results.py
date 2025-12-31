"""
Simple Results Viewer
View your analysis results without Excel
"""

import pandas as pd
import json
from pathlib import Path

def view_results():
    """Display results in console"""
    
    print("=" * 80)
    print("TRADING AGENT RESULTS VIEWER")
    print("=" * 80)
    
    # Check if results exist
    results_dir = Path("results")
    if not results_dir.exists():
        print("\n✗ No results directory found!")
        print("  Run the simulation first: python run_your_agents.py")
        return
    
    # ========================================================================
    # VIEW JSON RESULTS
    # ========================================================================
    
    print("\n" + "=" * 80)
    print("JSON RESULTS (Trade Details)")
    print("=" * 80)
    
    for agent_name in ['stockagent', 'tradingagents', 'fingpt']:
        filepath = results_dir / f"{agent_name}_results.json"
        
        if filepath.exists():
            print(f"\n{agent_name.upper()}:")
            print("-" * 80)
            
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            # Show summary
            summary = data.get('summary', {})
            print(f"  Total Trades: {summary.get('total_trades', 0)}")
            print(f"  Final Cash: ${summary.get('final_cash', 0):.2f}")
            print(f"  Total Profit: ${summary.get('total_profit', 0):.2f}")
            
            # Show first few trades
            trades = data.get('trades', [])
            if trades:
                print(f"\n  Sample Trades (showing first 3):")
                for trade in trades[:3]:
                    profit = trade.get('profit', 0)
                    symbol = "✓" if profit > 0 else "✗"
                    print(f"    {symbol} {trade.get('symbol', 'N/A')}: "
                          f"${trade.get('entry_price', 0):.2f} → "
                          f"${trade.get('exit_price', 0):.2f} = "
                          f"${profit:.2f}")
    
    # ========================================================================
    # VIEW CSV COMPARISON
    # ========================================================================
    
    csv_file = results_dir / "comparison_metrics.csv"
    
    if csv_file.exists():
        print("\n" + "=" * 80)
        print("PERFORMANCE COMPARISON")
        print("=" * 80)
        
        df = pd.read_csv(csv_file)
        
        # Show key metrics
        print("\nKey Metrics:")
        print("-" * 80)
        
        # Format for display
        display_cols = ['agent', 'total_trades', 'win_rate', 'total_profit', 
                       'average_profit', 'sharpe_ratio', 'profit_factor']
        
        # Check which columns exist
        available_cols = [col for col in display_cols if col in df.columns]
        
        if available_cols:
            display_df = df[available_cols].copy()
            
            # Format numbers
            if 'win_rate' in display_df.columns:
                display_df['win_rate'] = display_df['win_rate'].apply(lambda x: f"{x:.1f}%")
            if 'total_profit' in display_df.columns:
                display_df['total_profit'] = display_df['total_profit'].apply(lambda x: f"${x:.2f}")
            if 'average_profit' in display_df.columns:
                display_df['average_profit'] = display_df['average_profit'].apply(lambda x: f"${x:.2f}")
            if 'sharpe_ratio' in display_df.columns:
                display_df['sharpe_ratio'] = display_df['sharpe_ratio'].apply(lambda x: f"{x:.3f}")
            if 'profit_factor' in display_df.columns:
                display_df['profit_factor'] = display_df['profit_factor'].apply(lambda x: f"{x:.2f}")
            
            print(display_df.to_string(index=False))
    
    # ========================================================================
    # VIEW RANKINGS
    # ========================================================================
    
    rankings_file = results_dir / "agent_rankings.csv"
    
    if rankings_file.exists():
        print("\n" + "=" * 80)
        print("AGENT RANKINGS")
        print("=" * 80)
        
        rankings = pd.read_csv(rankings_file)
        rankings = rankings.sort_values('overall_rank')
        
        print("\nRanking by Overall Performance:")
        print("-" * 80)
        
        for idx, row in rankings.iterrows():
            rank = int(row['overall_rank'])
            agent = row['agent']
            medal = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉" if rank == 3 else "  "
            print(f"{medal} {rank}. {agent} (Score: {row['overall_rank']:.2f})")
    
    # ========================================================================
    # CHECK VISUALIZATIONS
    # ========================================================================
    
    viz_dir = Path("visualizations")
    
    if viz_dir.exists():
        charts = list(viz_dir.glob("*.png"))
        
        if charts:
            print("\n" + "=" * 80)
            print("VISUALIZATIONS AVAILABLE")
            print("=" * 80)
            
            print("\nGenerated Charts:")
            for chart in charts:
                print(f"  ✓ {chart.name}")
            
            print("\nTo view charts:")
            print("  Windows: start visualizations\\")
            print("  Mac: open visualizations/")
    
    # ========================================================================
    # SUMMARY
    # ========================================================================
    
    print("\n" + "=" * 80)
    print("FILES AVAILABLE")
    print("=" * 80)
    
    print("\nYou can open these in Excel or any spreadsheet app:")
    print("  - results/comparison_metrics.csv")
    print("  - results/agent_rankings.csv")
    
    print("\nView charts:")
    print("  - visualizations/*.png (6 charts)")
    
    print("\nRaw data:")
    print("  - results/stockagent_results.json")
    print("  - results/tradingagents_results.json")
    print("  - results/fingpt_results.json")


def open_csv_in_excel():
    """Open comparison CSV in Excel"""
    import platform
    import subprocess
    
    csv_file = Path("results/comparison_metrics.csv")
    
    if not csv_file.exists():
        print("✗ No CSV file found")
        return
    
    system = platform.system()
    
    try:
        if system == "Windows":
            subprocess.run(['start', str(csv_file)], shell=True)
        elif system == "Darwin":  # Mac
            subprocess.run(['open', str(csv_file)])
        else:  # Linux
            subprocess.run(['xdg-open', str(csv_file)])
        
        print(f"✓ Opened {csv_file} in default application")
    except Exception as e:
        print(f"Could not open file: {e}")
        print(f"Please manually open: {csv_file}")


def open_visualizations():
    """Open visualizations folder"""
    import platform
    import subprocess
    
    viz_dir = Path("visualizations")
    
    if not viz_dir.exists():
        print("✗ No visualizations directory found")
        return
    
    system = platform.system()
    
    try:
        if system == "Windows":
            subprocess.run(['explorer', str(viz_dir)])
        elif system == "Darwin":  # Mac
            subprocess.run(['open', str(viz_dir)])
        else:  # Linux
            subprocess.run(['xdg-open', str(viz_dir)])
        
        print(f"✓ Opened {viz_dir}")
    except Exception as e:
        print(f"Could not open folder: {e}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "csv":
            open_csv_in_excel()
        elif command == "charts":
            open_visualizations()
        else:
            print("Usage:")
            print("  python view_results.py       - Show results in console")
            print("  python view_results.py csv   - Open CSV in Excel")
            print("  python view_results.py charts - Open visualizations folder")
    else:
        view_results()
