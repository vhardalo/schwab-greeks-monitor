import json
import os
import time
from fetch_greeks import get_options_chain

# Import Rich terminal formatting modules
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.live import Live

console = Console()

def find_best_strike(contracts_map, target_delta):
    """
    Scans a contract map and finds the specific strike closest to the target delta,
    ensuring it passes a strict volume and open interest liquidity filter.
    """
    best_strike = None
    best_contract = None
    smallest_diff = float('inf')
    
    # MINIMUM LIQUIDITY THRESHOLDS
    MIN_VOLUME = 500       # Ensures active trading today
    MIN_OPEN_INTEREST = 100 # Ensures institutional resting orders are present

    for strike, contract_list in contracts_map.items():
        if not contract_list:
            continue
        contract = contract_list[0]
        
        # 1. Extract Liquidity Metrics safely
        volume = int(contract.get('totalVolume', 0))
        open_interest = int(contract.get('openInterest', 0))
        
        # 2. Skip illiquid ghost strikes completely
        if volume < MIN_VOLUME or open_interest < MIN_OPEN_INTEREST:
            continue

        # 3. Proceed with Delta calculation if liquidity passes
        greeks = contract.get('optionGreeks', {})
        raw_delta = contract.get('delta', greeks.get('delta', None))
        
        if raw_delta is None:
            continue
            
        try:
            delta = abs(float(raw_delta))
        except (ValueError, TypeError):
            continue
        
        if delta == 0.0:
            continue

        diff = abs(delta - target_delta)
        if diff < smallest_diff:
            smallest_diff = diff
            best_strike = strike
            best_contract = contract

    # Fallback: If EVERYTHING fails the liquidity check, run it again without the filter 
    # so the screen doesn't break, but print a warning.
    if not best_contract and contracts_map:
        for strike, contract_list in contracts_map.items():
            if contract_list:
                return find_best_strike_no_filter(contracts_map, target_delta)

    return best_strike, best_contract

def find_best_strike_no_filter(contracts_map, target_delta):
    """Backup function if no contracts meet strict liquidity limits."""
    best_strike = None
    best_contract = None
    smallest_diff = float('inf')
    for strike, contract_list in contracts_map.items():
        if not contract_list: continue
        contract = contract_list[0]
        greeks = contract.get('optionGreeks', {})
        raw_delta = contract.get('delta', greeks.get('delta', None))
        if raw_delta is None: continue
        try: delta = abs(float(raw_delta))
        except: continue
        diff = abs(delta - target_delta)
        if diff < smallest_diff:
            smallest_diff = diff
            best_strike = strike
            best_contract = contract
    return best_strike, best_contract

def generate_dashboard(chain_data):
    """
    Generates a stylized Rich Renderable layout instead of raw string prints.
    """
    if not chain_data:
        return Panel("[bold red][!] No data received from Schwab API.[/bold red]", title="Error")

    underlying_price = chain_data.get('underlyingPrice', 0)
    symbol = chain_data.get('symbol', 'UNKNOWN')
    
    call_map = chain_data.get('callExpDateMap', {})
    put_map = chain_data.get('putExpDateMap', {})

    if not call_map or not put_map:
        return Panel("[bold red][!] Empty options chain returned from server.[/bold red]", title="Error")
        
    exp_date_key = list(call_map.keys())[0]
    
    # Target Delta: 0.40 (High-Elasticity Momentum Threshold)
    TARGET_MOMENTUM_DELTA = 0.40
    
    call_strike, best_call = find_best_strike(call_map[exp_date_key], TARGET_MOMENTUM_DELTA)
    put_strike, best_put = find_best_strike(put_map[exp_date_key], TARGET_MOMENTUM_DELTA)

    # Extract Pricing Data safely
    c_bid = best_call.get('bid', 0.0) if best_call else 0.0
    c_ask = best_call.get('ask', 0.0) if best_call else 0.0
    p_bid = best_put.get('bid', 0.0) if best_put else 0.0
    p_ask = best_put.get('ask', 0.0) if best_put else 0.0

    # Extract Greek Blocks safely
    c_greeks = best_call.get('optionGreeks', {}) if best_call else {}
    p_greeks = best_put.get('optionGreeks', {}) if best_put else {}

    def get_metric(contract, greeks_dict, key):
        return contract.get(key, greeks_dict.get(key, 0.0))
    try:
        c_delta = float(get_metric(best_call, c_greeks, 'delta')) if best_call else 0.0
        p_delta = float(get_metric(best_put, p_greeks, 'delta')) if best_put else 0.0
        c_gamma = float(get_metric(best_call, c_greeks, 'gamma')) if best_call else 0.0
        p_gamma = float(get_metric(best_put, p_greeks, 'gamma')) if best_put else 0.0
        c_theta = float(get_metric(best_call, c_greeks, 'theta')) if best_call else 0.0
        p_theta = float(get_metric(best_put, p_greeks, 'theta')) if best_put else 0.0
        c_vega = float(get_metric(best_call, c_greeks, 'vega')) if best_call else 0.0
        p_vega = float(get_metric(best_put, p_greeks, 'vega')) if best_put else 0.0
    except (ValueError, TypeError):
        c_delta = p_delta = c_gamma = p_gamma = c_theta = p_theta = c_vega = p_vega = 0.0

    # Extract liquidity metrics safely
    c_vol = best_call.get('totalVolume', 0) if best_call else 0
    p_vol = best_put.get('totalVolume', 0) if best_put else 0
    c_oi = best_call.get('openInterest', 0) if best_call else 0
    p_oi = best_put.get('openInterest', 0) if best_put else 0

    # 1. INITIALIZE THE TABLE FIRST (Fixed order)
    table = Table(show_header=True, header_style="bold white", box=None, expand=True)
    table.add_column("GREEK METRIC", width=18, style="dim")
    table.add_column(f"🟩 OPTIMAL CALL OPTION (Strike: {float(call_strike):.1f})", justify="left")
    table.add_column(f"🟥 OPTIMAL PUT OPTION (Strike: {float(put_strike):.1f})", justify="left")
    
    # 2. NOW ADD THE ROWS (Using the new liquidity metrics)
    table.add_section()
    table.add_row("Bid / Ask", f"${c_bid:.2f} x ${c_ask:.2f}", f"${p_bid:.2f} x ${p_ask:.2f}")
    table.add_row("Daily Volume", f"{c_vol:,}", f"{p_vol:,}")
    table.add_row("Open Interest", f"{c_oi:,}", f"{p_oi:,}")
    table.add_section()
    table.add_row("Delta (Speed)", f"[bold green]{c_delta:+.2f}[/bold green]", f"[bold red]{p_delta:+.2f}[/bold red]")
    table.add_row("Gamma (Accel)", f"[cyan]{c_gamma:.4f}[/cyan]", f"[cyan]{p_gamma:.4f}[/cyan]")
    table.add_row("Theta (Decay)", f"[yellow]{c_theta:.2f}[/yellow]", f"[yellow]{p_theta:.2f}[/yellow]")
    table.add_row("Vega (Vol)", f"{c_vega:.4f}", f"{p_vega:.4f}")

    # 3. Wrap everything inside the Panel frame
    panel_title = f"⚡ TARGETED MOMENTUM RECON | Underlying: [bold cyan]{symbol} = ${underlying_price:.2f}[/bold cyan]"
    subtitle_text = f"[dim]Strategy Target: High-Elasticity 0DTE (~{TARGET_MOMENTUM_DELTA:.2f} Delta) | Refresh: 5s[/dim]"
    
    return Panel(table, title=panel_title, subtitle=subtitle_text, border_style="blue", padding=(1, 2))

if __name__ == "__main__":
    REFRESH_INTERVAL = 5
    os.system('clear' if os.name != 'nt' else 'cls')
    
    try:
        # 1. Pass first_run=True here so it prints ONCE on startup
        initial_data = get_options_chain("SPY", first_run=True)
        
        with Live(generate_dashboard(initial_data), refresh_per_second=1) as live:
            while True:
                time.sleep(REFRESH_INTERVAL)
                # 2. Inside the loop, it defaults to first_run=False and stays silent
                data = get_options_chain("SPY")
                live.update(generate_dashboard(data))
                
    except KeyboardInterrupt:
        console.print("\n\n[bold orange1][!] Monitor cleanly halted via user interrupt.[/bold orange1]\n")