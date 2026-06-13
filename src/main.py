"""
BrewJournal - High-Performance CLI Coffee Ledger
Stanford Code in Place - Phase 1 Operational Shell
"""

import os
import sys
import json 

# Absolute/Relative pathway config to target the JSON database file
VAULT_PATH = os.path.join("data", "vault.json")


def clear_terminal():
    """Clears the terminal screen for clean user experience layout transitions."""
    os.system("clear" if os.name != "nt" else "cls")


def load_vault():
    """Reads the JSON file and returns the master state dictionary."""
    try:
        with open(VAULT_PATH, "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        # Fallback dictionary matching your specific settings & features requirements
        return {
            "settings": {"min_variety_expected": 2, "low_stock_threshold_g": 100},
            "inventory": {},
            "recipes": {},
        }


def save_vault(data):
    """Serializes and writes the active program state dictionary back onto disk storage."""
    try:
        with open(VAULT_PATH, "w") as file:
            json.dump(data, file, indent=4)
    except IOError:
        print("\n[ERROR] CRITICAL: Failed to write to database storage matrix.")


from datetime import datetime, date

def run_welcome_notifications(vault_data):
    """Parses database states to issue dynamic variety, weight, and freshness alerts on login."""
    inventory = vault_data.get("inventory", {})
    settings = vault_data.get("settings", {})
    
    min_variety = settings.get("min_variety_expected", 2)
    low_stock_limit = settings.get("low_stock_threshold_g", 100)
    
    unique_varieties = len(inventory)
    low_stock_alerts = []
    staleness_alerts = []
    
    # Get today's local date object
    today = date.today()
    
    for bean_name, profile in inventory.items():
        # 1. Evaluate Weight Metrics
        weight = profile.get("weight_g", 0)
        if weight <= low_stock_limit:
            low_stock_alerts.append(f"-> {bean_name} is running low ({weight}g left!)")
            
        # 2. Evaluate Freshness Metrics (New Field Check)
        purchase_date_str = profile.get("purchase_date", "")
        if purchase_date_str:
            try:
                # Convert the stored string date format back into a Python date object
                purchase_date = datetime.strptime(purchase_date_str, "%Y-%m-%d").date()
                days_old = (today - purchase_date).days
                
                # Check stale limits
                if days_old > 90:
                    staleness_alerts.append(f"🚨 CRITICAL STALE: {bean_name} is over 90 days old! ({days_old} days)")
                elif days_old > 60:
                    staleness_alerts.append(f"⚠️  STALE WARNING: {bean_name} is over 60 days old! ({days_old} days)")
            except ValueError:
                # Safe-guard if a date string gets corrupted or hand-typed incorrectly
                pass
                
    print("\n🔔 SYSTEM NOTIFICATIONS & ALERTS:")
    print("-" * 65)
    
    # Render Diversity Metrics
    if unique_varieties == 0:
        print("⚠️  CRITICAL: Inventory is completely empty! Add beans to start.")
    elif unique_varieties < min_variety:
        print(f"⚠️  ALERT: Low Stock Diversity! You only have {unique_varieties} varieties (Expected: {min_variety}+).")
    else:
        print("✅ Stock Diversity: Optimal. Roastery profiles are balanced.")
        
    # Render Weight Alerts
    if low_stock_alerts:
        for alert in low_stock_alerts:
            print(alert)
            
    # Render Freshness Alerts (New Dash Module)
    if staleness_alerts:
        for alert in staleness_alerts:
            print(alert)
    elif unique_varieties > 0:
        print("✅ Freshness Status: All coffee lots are currently within optimal extraction windows.")
        
    print("-" * 65)

def manage_bean_stock(vault_data):
    """Screen [2]: Allows user to write new bean profiles, modify weights, or drop records."""
    inventory = vault_data.get("inventory", {})
    
    while True:
        clear_terminal()
        print("=" * 65)
        print("        📝 MANAGE COFFEE BEAN STOCK (WRITE/MODIFY)       ")
        print("=" * 65)
        
        if not inventory:
            print("\n[Status] Current inventory is empty.")
        else:
            print("\nActive Bean Profiles in Vault:")
            for name, profile in inventory.items():
                print(f" -> {name} ({profile['roast_level'].title()} Roast)")
                print(f"    Taste: {profile.get('tasting_notes')} | Stock: {profile['weight_g']}g | Purchased: {profile.get('purchase_date')}")
                print("-" * 45)
        
        print("\n[1] Add / Update a Bean Profile")
        print("[2] Delete an Existing Bean Profile")
        print("[3] Back to Main Menu")
        print("-" * 65)
        
        choice = input("Select sub-operation [1-3]: ").strip()
        
        if choice == "1":
            print("\n--- ☕ ENTER BEAN DETAILS ---")
            name = input("Bean Name / Origin (e.g., Ethiopia Yirgacheffe): ").strip()
            if not name:
                input("[Error] Name cannot be blank. Press Enter...")
                continue
                
            roast = input("Roast Level (Light / Medium / Dark): ").strip().lower()
            tasting_notes = input("Tasting Notes (e.g., Jasmine, Blueberry): ").strip()
            
            today_str = date.today().strftime("%Y-%m-%d")
            print(f"Date of Purchase (YYYY-MM-DD) [Leave blank for Today: {today_str}]:")
            purchase_date_input = input("-> ").strip()
            purchase_date = purchase_date_input if purchase_date_input else today_str
            
            while True:
                try:
                    weight = int(input("Current Weight in Grams (e.g., 250): ").strip())
                    if weight >= 0: break
                    print("[Error] Weight cannot be negative.")
                except ValueError:
                    print("[Error] Please enter a valid whole number.")
            
            inventory[name] = {
                "roast_level": roast if roast in ["light", "medium", "dark"] else "medium",
                "tasting_notes": tasting_notes if tasting_notes else "Balanced profile",
                "purchase_date": purchase_date,
                "weight_g": weight
            }
            
            vault_data["inventory"] = inventory
            save_vault(vault_data)
            input(f"\n✅ Successfully updated {name}! Press Enter...")
            
        elif choice == "2":
            if not inventory:
                input("\n[Error] No beans in stock to delete. Press Enter...")
                continue
            print("\n--- 🪓 BEAN TRUNCATION MATRIX ---")
            del_target = input("Enter exact name of bean to delete: ").strip()
            if del_target in inventory:
                del inventory[del_target]
                vault_data["inventory"] = inventory
                save_vault(vault_data)
                input(f"\n✅ Profile '{del_target}' dropped from database storage. Press Enter...")
            else:
                input(f"\n[Error] Profile '{del_target}' not found. Press Enter...")
                
        elif choice == "3":
            break


def manage_formulas(vault_data):
    """Screen [3]: Advanced extraction recipes with automated math calculation engines."""
    inventory = vault_data.get("inventory", {})
    recipes = vault_data.get("recipes", {})
    
    while True:
        clear_terminal()
        print("=" * 65)
        print("         ☕ PREPARATION FORMULAS & EXTRACTION RECIPES        ")
        print("=" * 65)
        
        if not recipes:
            print("\n[Status] No preparation formulas compiled in vault storage matrix.")
        else:
            print("\nActive Extraction Records:")
            for formula_name, details in recipes.items():
                linked_bean = details.get("bean_name", "Unknown Bean")
                
                print(f" 📂 Formula: {formula_name} [{details.get('brew_method', 'V60').upper()}]")
                print(f"    ├─ Relational Bean Key : {linked_bean}")
                
                if linked_bean in inventory:
                    notes = inventory[linked_bean].get("tasting_notes", "No notes recorded")
                    print(f"    ├─ Derived Taste Profile: {notes}")
                
                print(f"    ├─ Parameters: 1:{details.get('ratio')} Ratio | {details.get('coffee_g')}g coffee ➡️ {details.get('water_ml')}ml water (Auto-Calculated)")
                print(f"    ├─ Extraction: Grind: {details.get('grind_setting')} | Temp: {details.get('water_temp_c')}°C")
                print(f"    ├─ Timing    : Bloom: {details.get('bloom_time_s')}s | Total Target Time: {details.get('target_time')}")
                print(f"    └─ Comments  : {details.get('notes')}")
                print("-" * 65)
                
        print("\nOPERATIONAL VECTORS:")
        print(" [1] Write / Modify an Extraction Formula")
        print(" [2] Delete an Existing Formula")
        print(" [3] Return to Main Menu Router")
        print("-" * 65)
        
        choice = input("Select sub-operation vector [1-3]: ").strip()
        
        if choice == "1":
            print("\n--- 🛠️ CONFIGURING FORMULA ENTRY ---")
            formula_name = input("Formula Designation Name (e.g., Daily V60): ").strip()
            if not formula_name: continue
            
            if not inventory:
                input("\n⚠️  [ALERT] Inventory is completely empty! Seed a bean first. Press Enter...")
                continue
                
            print("\nSelect Active Inventory Vector Target:")
            bean_keys = list(inventory.keys())
            for idx, b_name in enumerate(bean_keys, start=1):
                print(f"  [{idx}] {b_name}")
                
            try:
                bean_idx = int(input(f"Select index token [1-{len(bean_keys)}]: ").strip()) - 1
                selected_bean = bean_keys[bean_idx]
            except (ValueError, IndexError):
                input("[Error] Invalid selection vector. Press Enter...")
                continue
                
            method = input("Extraction Device (e.g., V60, Espresso): ").strip()
            grind = input("Grind Setting (e.g., 24 Clicks): ").strip()
            
            # --- CALCULATED FIELD INPUT LOGIC ---
            # User inputs decimal ratio and coffee mass; system automates total water calculation
            while True:
                try:
                    ratio = float(input("Target Brew Ratio (e.g., 16.5 for 1:16.5): ").strip())
                    if ratio > 0: break
                    print("[Error] Ratio must be greater than zero.")
                except ValueError:
                    print("[Error] Please enter a valid decimal number.")
                    
            while True:
                try:
                    coffee_g = int(input("Dry Coffee Mass Dose in Grams (e.g., 15): ").strip())
                    if coffee_g > 0: break
                    print("[Error] Mass must be greater than zero.")
                except ValueError:
                    print("[Error] Please enter a valid whole integer.")
            
            # Automated Extraction Formula Execution
            water_ml = int(round(coffee_g * ratio))
            print(f"⚡ Extraction Engine Calculation: Total target water volume automated at -> {water_ml}ml")
            
            while True:
                try:
                    temp_c = int(input("Water Temperature in Celsius (e.g., 93): ").strip())
                    break
                except ValueError: print("[Error] Enter a whole integer.")
                
            while True:
                try:
                    bloom_s = int(input("Bloom Phase Time in Seconds (e.g., 45): ").strip())
                    break
                except ValueError: print("[Error] Enter a whole integer.")
            
            target_time = input("Ideal Total Brew Time Format MM:SS (e.g., 03:15): ").strip()
            comments = input("Instructions / Comments: ").strip()
            
            recipes[formula_name] = {
                "bean_name": selected_bean,
                "brew_method": method if method else "V60",
                "ratio": ratio,
                "coffee_g": coffee_g,
                "water_ml": water_ml, # Saved directly as a calculated state variable
                "grind_setting": grind if grind else "Medium",
                "water_temp_c": temp_c,
                "bloom_time_s": bloom_s,
                "target_time": target_time if target_time else "03:00",
                "notes": comments if comments else "Standard extraction profile."
            }
            
            vault_data["recipes"] = recipes
            save_vault(vault_data)
            input(f"\n✅ Formula '{formula_name}' successfully calculated and saved! Press Enter...")
            
        elif choice == "2":
            if not recipes: continue
            del_target = input("Enter exact name of formula to delete: ").strip()
            if del_target in recipes:
                del recipes[del_target]
                vault_data["recipes"] = recipes
                save_vault(vault_data)
                input(f"\n✅ Record '{del_target}' dropped from storage. Press Enter...")
                
        elif choice == "3":
            break

def main():
    # Load your persistent storage matrix once at program initialization
    vault_data = load_vault()
    
    while True:
        clear_terminal()
        
        # --- FIX: Move banner and notifications inside the loop matrix ---
        print("=" * 65)
        print("  ____  ____  _____        _ ___  _   _ ____  _   _  _     ")
        print(" | __ )|  _ \| ____|_      | / _ \| | | |  _ \| \ | |/ \    ")
        print(" |  _ \| |_) |  _| \ \ /\ / / | | | | | | | |_) |  \| / _ \   ")
        print(" | |_) |  _ <| |___ \ V  V /| |_| | |_| |  _ <| |\  / ___ \  ")
        print(" |____/|_| \_\_____| \_/\_/  \__\_\\___/|_| \_\_| \_/_/   \_\ ")
        print("\n          ☕ SPECIALTY COFFEE BREW LEDGER SYSTEM ☕          ")
        print("=" * 65)
        
        # This will now dynamically evaluate your states every single time you return home!
        run_welcome_notifications(vault_data)
        
        # Display Core Navigation Vector Routes
        print("\nMAIN MENU OPERATIONAL VECTORS:")
        print(" [1] Read Exploration Ledger (Review Logs)")
        print(" [2] Manage Coffee Bean Stock (Write/Modify Inventory)")
        print(" [3] Manage Preparation Formulas (Recipes)")
        print(" [4] Edit System Notification Configurations")
        print(" [5] Sync Database & Shutdown System")
        print("-" * 65)
        
        choice = input("Select operation vector [1-5]: ").strip()
        
        if choice == "1":
            input("\n[INFO] Screen 1 processing logic coming next. Press Enter...")
        elif choice == "2":
            manage_bean_stock(vault_data)
        elif choice == "3":
            manage_formulas(vault_data)
        elif choice == "4":
            input("\n[INFO] Screen 4 configuration logic coming next. Press Enter...")
        elif choice == "5":
            save_vault(vault_data)
            print("\n💾 State machine flushed to disk storage safely. Terminal footprint clear.")
            print("Goodbye!\n")
            break
        else:
            input("\n[WARN] Invalid choice token vector. Press Enter to clear buffer...")


if __name__ == "__main__":
    main()
