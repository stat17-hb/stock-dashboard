from modules.history import TransactionHistory
import pandas as pd

try:
    history = TransactionHistory()
    df = history.get_history()
    
    print("Columns (repr):", [repr(c) for c in df.columns])
    
    # Try to find the actual column names
    name_col = next((c for c in df.columns if '종목명' in c), None)
    qty_col = next((c for c in df.columns if '수량' in c), None)
    type_col = next((c for c in df.columns if '구분' in c), None)
    
    print(f"Found Name Col: {repr(name_col)}")
    print(f"Found Qty Col: {repr(qty_col)}")
    print(f"Found Type Col: {repr(type_col)}")
    
    if name_col and qty_col and type_col:
        accounts, account_col = history.get_accounts(df)
        pension_acc = next((acc for acc in accounts if '연금저축' in str(acc)), None)
        
        if pension_acc:
            df_pension = df[df[account_col] == pension_acc]
            print(f"--- Pension Account Data ({len(df_pension)} rows) ---")
            print(df_pension[[name_col, qty_col, type_col]].to_string())
        else:
            print("Pension account not found")

except Exception as e:
    print(f"Error: {e}")
