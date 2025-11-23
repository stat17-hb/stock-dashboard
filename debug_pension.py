from modules.history import TransactionHistory
import pandas as pd

try:
    history = TransactionHistory()
    df = history.get_history()
    
    print("Columns:", df.columns.tolist())
    
    if not df.empty:
        accounts, account_col = history.get_accounts(df)
        print(f"Account Column: {account_col}")
        print("Unique Accounts:", accounts)
        
        # Check for '연금저축'
        pension_acc = None
        for acc in accounts:
            if '연금저축' in str(acc):
                pension_acc = acc
                break
        print(f"Pension Account Found: {pension_acc}")
        
        if pension_acc:
            df_pension = df[df[account_col] == pension_acc]
            print(f"Rows for {pension_acc}: {len(df_pension)}")
            if not df_pension.empty:
                print("Sample rows:")
                print(df_pension.head())
                
                # Check column names for logic
                for col in df_pension.columns:
                    if '종목' in col: print(f"Name Col: {col}")
                    if '수량' in col: print(f"Qty Col: {col}")
                    if '구분' in col: print(f"Type Col: {col}")

except Exception as e:
    print(f"Error: {e}")
