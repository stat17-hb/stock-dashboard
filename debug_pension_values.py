from modules.history import TransactionHistory
import pandas as pd

try:
    history = TransactionHistory()
    df = history.get_history()
    
    accounts, account_col = history.get_accounts(df)
    pension_acc = next((acc for acc in accounts if '연금저축' in str(acc)), None)
    
    if pension_acc:
        df_pension = df[df[account_col] == pension_acc]
        print(f"--- Pension Account Data ({len(df_pension)} rows) ---")
        print(df_pension[['종목명', '수량', '구분']].to_string())
    else:
        print("Pension account not found")

except Exception as e:
    print(f"Error: {e}")
