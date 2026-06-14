"""
BrewJournal - High-Performance CLI Coffee Ledger
Stanford Code in Place - Phase 1 Operational Shell
"""

import os
import sys
import json
from datetime import datetime
from datetime import date 

# Absolute/Relative pathway config to target the JSON database file
VAULT_PATH = os.path.join("data", "vault.json")

def clear_terminal():
    """Clears the terminal screen for clean user experience layout transitions."""
    os.system("clear" if os.name != "nt" else "cls")

def load_vault():
    """Initializes and reads persistent JSON storage matrix with safe MVP defaults."""
    # If file doesn't exist, bootstrap a clean default database layout structure
    if not os.path.exists("data/vault.json"):
        return {
            "settings": {
                "low_stock_threshold_g": 100,
                "min_variety_expected": 2
            },
            "inventory": {},
            "recipes": {}
        }
        
    try:
        with open("data/vault.json", "r") as file:
            data = json.load(file)
            # Failsafe: Ensure critical sub-keys always exist in memory map
            if "settings" not in data:
                data["settings"] = {"low_stock_threshold_g": 100, "min_variety_expected": 2}
            if "inventory" not in data: data["inventory"] = {}
            if "recipes" not in data: data["recipes"] = {}
            return data
    except (json.JSONDecodeError, FileNotFoundError):
        # Fallback return state if file data is corrupted
        return {
            "settings": {"low_stock_threshold_g": 100, "min_variety_expected": 2},
            "inventory": {},
            "recipes": {}
        }

def save_vault(data):
    """Serializes and writes the active program state dictionary back onto disk storage."""
    try:
        with open(VAULT_PATH, "w") as file:
            json.dump(data, file, indent=4)
    except IOError:
        print("\n[ERROR] CRITICAL: Failed to write to database storage matrix.")

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
    """Screen [3]: Advanced extraction recipes with automated math and timestamps."""
    inventory = vault_data.get("inventory", {})
    recipes = vault_data.get("recipes", {})
    
    while True:
        clear_terminal()
        print("=" * 75)
        print("         ☕ PREPARATION FORMULAS & EXTRACTION RECIPES        ")
        print("=" * 75)
        
        if not recipes:
            print("\n[Status] No preparation formulas compiled in vault storage matrix.")
        else:
            print("\nActive Extraction Records:")
            for formula_name, details in recipes.items():
                linked_bean = details.get("bean_name", "Unknown Bean")
                
                print(f" 📂 Formula: {formula_name} [{details.get('brew_method', 'V60').upper()}]")
                print(f"    ├─ Logged Timestamp   : {details.get('created_at', 'N/A')}")
                
                # --- FIXED RELATIONAL ERROR SAFEGUARD ---
                if linked_bean in inventory:
                    notes = inventory[linked_bean].get("tasting_notes", "No notes recorded")
                    print(f"    ├─ Derived Taste Profile: {notes}")
                else:
                    print(f"    ├─ Derived Taste Profile: ⚠️  Relational Linkage Broken: Bean missing from inventory matrix.")
                
                print(f"    ├─ Parameters: 1:{details.get('ratio')} Ratio | {details.get('coffee_g')}g coffee ➡️ {details.get('water_ml')}ml water")
                print(f"    ├─ Extraction: Grind: {details.get('grind_setting')} | Temp: {details.get('water_temp_c')}°C")
                print(f"    ├─ Timing    : Bloom: {details.get('bloom_time_s')}s | Total Target Time: {details.get('target_time')}")
                print(f"    └─ Comments  : {details.get('notes')}")
                print("-" * 75)
                
        print("\nOPERATIONAL VECTORS:")
        print(" [1] Write / Modify an Extraction Formula")
        print(" [2] Delete an Existing Formula")
        print(" [3] Return to Main Menu Router")
        print("-" * 75)
        
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
            
            while True:
                try:
                    ratio = float(input("Target Brew Ratio (e.g., 16.5): ").strip())
                    if ratio > 0: break
                except ValueError: print("[Error] Enter a decimal number.")
                    
            while True:
                try:
                    coffee_g = int(input("Coffee Mass in Grams (e.g., 15): ").strip())
                    if coffee_g > 0: break
                except ValueError: print("[Error] Enter a whole integer.")
            
            water_ml = int(round(coffee_g * ratio))
            print(f"⚡ Calculated target water volume: {water_ml}ml")
            
            while True:
                try:
                    temp_c = int(input("Water Temperature in Celsius: ").strip())
                    break
                except ValueError: print("[Error] Enter an integer.")
                
            while True:
                try:
                    bloom_s = int(input("Bloom Time in Seconds: ").strip())
                    break
                except ValueError: print("[Error] Enter an integer.")
            
            target_time = input("Ideal Total Brew Time (MM:SS): ").strip()
            comments = input("Instructions / Comments: ").strip()
            
            # --- AUTOMATED TIMESTAMP GENERATION ---
            timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M")
            
            recipes[formula_name] = {
                "bean_name": selected_bean,
                "brew_method": method if method else "V60",
                "ratio": ratio,
                "coffee_g": coffee_g,
                "water_ml": water_ml,
                "grind_setting": grind if grind else "Medium",
                "water_temp_c": temp_c,
                "bloom_time_s": bloom_s,
                "target_time": target_time if target_time else "03:00",
                "notes": comments if comments else "Standard extraction profile.",
                "created_at": timestamp_str # Inject structural timestamp metadata
            }
            
            vault_data["recipes"] = recipes
            save_vault(vault_data)
            input(f"\n✅ Formula '{formula_name}' saved with timestamp! Press Enter...")
            
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

def view_exploration_ledger(vault_data):
    """Screen [1]: Reads, sorts chronologically, and summarizes all archived recipes."""
    recipes = vault_data.get("recipes", {})
    inventory = vault_data.get("inventory", {})
    
    clear_terminal()
    print("=" * 75)
    print("        📖 EXPLORATION LEDGER & EXTRACTION ARCHIVES (CHRONO)          ")
    print("=" * 75)
    
    if not recipes:
        print("\n[Status] No execution records logged in the archive matrix yet.")
    else:
        print(f"Total Logged Sessions: {len(recipes)}\n")
        
        # --- CHRONOLOGICAL SORTING MATRIX ---
        # Sort recipes by their internal 'created_at' timestamp string, newest first
        sorted_recipes = sorted(
            recipes.items(),
            key=lambda item: item[1].get("created_at", ""),
            reverse=True
        )
        
        for name, details in sorted_recipes:
            linked_bean = details.get("bean_name", "Unknown Bean")
            timestamp = details.get("created_at", "N/A")
            
            print(f" 📅 [{timestamp}] - Formula: {name} ({details.get('brew_method', 'V60').upper()})")
            print(f"    ├─ Target Math : 1:{details.get('ratio')} Ratio | {details.get('coffee_g')}g ➡️ {details.get('water_ml')}ml")
            
            # Relational Integrity Check
            if linked_bean in inventory:
                print(f"    ├─ Coffee Batch: {linked_bean}")
            else:
                print(f"    ├─ Coffee Batch: ⚠️  Relational Linkage Broken: Bean missing from inventory matrix.")
                
            print(f"    └─ Directions  : {details.get('notes')}")
            print("-" * 75)
            
    print("=" * 75)
    input("\n[Navigation] Exploration ledger vector scan complete. Press Enter...")

def manage_settings(vault_data):
    """Screen [4]: Allows interactive updates to threshold system alerts."""
    settings = vault_data.get("settings", {})
    
    while True:
        clear_terminal()
        print("=" * 65)
        print("        ⚙️ SYSTEM NOTIFICATION & CONFIGURATION MATRIX        ")
        print("=" * 65)
        print(f" Current Configurations:")
        print(f"  ├─ [1] Low Weight Stock Threshold: {settings.get('low_stock_threshold_g', 100)}g")
        print(f"  └─ [2] Minimum Variety Expected  : {settings.get('min_variety_expected', 2)} varieties")
        print("-" * 65)
        print(" [3] Return to Main Menu Router")
        print("-" * 65)
        
        choice = input("Select configuration adjustments [1-3]: ").strip()
        
        if choice == "1":
            try:
                new_weight = int(input("\nEnter new low-weight threshold limit in grams: ").strip())
                if new_weight >= 0:
                    settings["low_stock_threshold_g"] = new_weight
                    vault_data["settings"] = settings
                    save_vault(vault_data)
                    print("✅ Low-stock threshold state synced to memory!")
                else:
                    print("[Error] Threshold cannot be negative.")
            except ValueError:
                print("[Error] Invalid whole integer.")
            input("Press Enter...")
            
        elif choice == "2":
            try:
                new_variety = int(input("\nEnter new minimum variety count limit: ").strip())
                if new_variety >= 0:
                    settings["min_variety_expected"] = new_variety
                    vault_data["settings"] = settings
                    save_vault(vault_data)
                    print("✅ Variety count expectation state synced to memory!")
                else:
                    print("[Error] Limit cannot be negative.")
            except ValueError:
                print("[Error] Invalid whole integer.")
            input("Press Enter...")
            
        elif choice == "3":
            break

def main():
    # Load your persistent storage matrix once at program initialization
    vault_data = load_vault()
    
    while True:
        clear_terminal()
        
        # --- FIX: Move banner and notifications inside the loop matrix ---
        print("=" * 65)
# --- FIXED RECTIFIED ASCII ART BANNER VECTOR ---
        print(r" ____                      ___                               _  _   ___")
        print(r"| == ) _ __ _____      __  | | ___  _   _ _ __ _ __   __ _ _| |/ | / _ \ ")
        print(r"|  _ \| '__/ _ \ \ /\ / /  | |/ _ \| | | | '__| '_ \ / _` | | || || | | |")
        print(r"| |_) | | |  __/\ V  V //|_| | (_) | |_| | |  | | | | (_| | | || || |_| |")
        print(r"|____/|_|  \___| \_/\_/ \____/\___/\___,_|_|  |_| |_|\__,_|_|_||_(_)___/ ")
        print("\n          ☕ SPECIALTY COFFEE BREW LEDGER SYSTEM ☕          ")
        print("=" * 65)
        
        # This will now dynamically evaluate your states every single time you return home!
        run_welcome_notifications(vault_data)
        
        # Display Core Navigation Vector Routes
        print("\nMAIN MENU OPERATIONAL VECTORS:")
        print(" [1] Read Exploration Ledger (Review Logs)")
        print(" [2] Manage Coffee Bean Stock (Write/Modify Inventory)")
        print(" [3] Manage Preparation Formulas & cup logs (Write/Modify)")
        print(" [4] Edit System Notification Configurations")
        print(" [5] Sync Database & Shutdown System")
        print("-" * 65)
        
        choice = input("Select operation vector [1-5]: ").strip()
        
        if choice == "1":
            # Fire Screen 1 Exploration Ledger
            view_exploration_ledger(vault_data)
        elif choice == "2":
            manage_bean_stock(vault_data)
        elif choice == "3":
            manage_formulas(vault_data)
        elif choice == "4":
            # Fire Screen 4 Configuration Matrix
            manage_settings(vault_data)            
        elif choice == "5":
            save_vault(vault_data)
            print("\n💾 State machine flushed to disk storage safely. Terminal footprint clear.")
            print("Goodbye!\n")
            break
        else:
            input("\n[WARN] Invalid choice token vector. Press Enter to clear buffer...")



if __name__ == "__main__":
    main()
