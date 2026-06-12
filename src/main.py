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


def run_welcome_notifications(vault_data):
    """Parses database states to issue dynamic variety and low-stock alerts on login."""
    inventory = vault_data.get("inventory", {})
    settings = vault_data.get("settings", {})

    min_variety = settings.get("min_variety_expected", 2)
    low_stock_limit = settings.get("low_stock_threshold_g", 100)

    unique_varieties = len(inventory)
    low_stock_alerts = []

    # Analyze each item in the inventory dictionary
    for bean_name, profile in inventory.items():
        weight = profile.get("weight_g", 0)
        if weight <= low_stock_limit:
            low_stock_alerts.append(f"-> {bean_name} is running low ({weight}g left!)")

    print("\n🔔 SYSTEM NOTIFICATIONS & ALERTS:")
    print("-" * 55)

    # 1. Check for bean stock diversity
    if unique_varieties == 0:
        print("⚠️  CRITICAL: Inventory is completely empty! Add beans to start.")
    elif unique_varieties < min_variety:
        print(
            f"⚠️  ALERT: Low Stock Diversity! You only have {unique_varieties} bean varieties (Expected: {min_variety}+)."
        )
    else:
        print("✅ Stock Diversity: Optimal. Roastery profiles are balanced.")

    # 2. Check for individual bean low weights
    if low_stock_alerts:
        for alert in low_stock_alerts:
            print(alert)
    else:
        if unique_varieties > 0:
            print("✅ Stock: Sufficient coffee weight across all active profiles.")
    print("-" * 55)


def manage_bean_stock(vault_data):
    """Screen [2]: Allows user to write new bean profiles or modify existing weights."""
    while True:
        clear_terminal()
        print("=" * 55)
        print("        📝 MANAGE COFFEE BEAN STOCK (WRITE/MODIFY)       ")
        print("=" * 55)

        # Display current stock simple list for user reference
        inventory = vault_data.get("inventory", {})
        if not inventory:
            print("\n[Status] Current inventory is empty.")
        else:
            print("\nActive Bean Profiles in Vault:")
            for name, profile in inventory.items():
                print(
                    f" -> {name} ({profile['roast_level'].title()} Roast) | Stock: {profile['weight_g']}g"
                )

        print("\n[1] Add / Update a Bean Profile")
        print("[2] Back to Main Menu")
        print("-" * 55)

        choice = input("Select sub-operation [1-2]: ").strip()

        if choice == "1":
            print("\n--- ☕ ENTER BEAN DETAILS ---")
            name = input("Bean Name / Origin (e.g., Ethiopia Yirgacheffe): ").strip()
            if not name:
                input("[Error] Name cannot be blank. Press Enter...")
                continue

            roast = input("Roast Level (Light / Medium / Dark): ").strip().lower()

            # Numeric validation loop for weight input
            while True:
                weight_input = input("Current Weight in Grams (e.g., 250): ").strip()
                try:
                    weight = int(weight_input)
                    if weight < 0:
                        print("[Error] Weight cannot be negative.")
                        continue
                    break
                except ValueError:
                    print("[Error] Please enter a valid whole number for weight.")

            # Write/Modify the dictionary entry
            inventory[name] = {
                "roast_level": (
                    roast if roast in ["light", "medium", "dark"] else "medium"
                ),
                "weight_g": weight,
            }

            # Instantly commit change to our state structure and file
            vault_data["inventory"] = inventory
            save_vault(vault_data)
            input(
                f"\n✅ Successfully updated {name}! Vault synchronized. Press Enter..."
            )

        elif choice == "2":
            break
        else:
            input("\n[WARN] Invalid choice. Press Enter...")


def main():
    # Fetch real data array state from JSON right at startup
    vault_data = load_vault()

    while True:
        clear_terminal()
        print("=" * 65)
        print(
            " ____                       _                              _    ___   _ "
        )
        print(
            "| == ) _ __ _____      __  | | ___  _   _ _ __ _ __   __ _| |  / _ \ / |"
        )
        print(
            "|  _ \| '__/ _ \ \ /\ / /  | |/ _ \| | | | '__| '_ \ / _` | | | | | || |"
        )
        print(
            "| |_) | | |  __/\ V  V //|_| | (_) | |_| | |  | | | | (_| | | | |_| || |"
        )
        print(
            "|____/|_|  \___| \_/\_/ \___/ \___/ \__,_|_|  |_| |_|\__,_|_|  \___(_)_|"
        )
        print("\n          ☕ SPECIALTY COFFEE BREW LEDGER SYSTEM ☕          ")
        print("=" * 65)

        # Injects your screen notification brain logic
        run_welcome_notifications(vault_data)

        print("[1] View Bean Inventory & Formulas (Read)")
        print("[2] Manage Coffee Bean Stock (Write/Modify)")
        print("[3] Manage Preparation Formulas (Write/Modify)")
        print("[4] Update Notification Settings")
        print("[5] Sync Database & Shutdown System")
        print("=" * 55)

        choice = input("Select operation index vector [1-5]: ").strip()

        if choice == "1":
            input(
                "\n[INFO] Screen 1: Exploration ledger reading protocols coming next. Press Enter..."
            )
        elif choice == "2":
            # Fire off the bean inventory configuration panel
            manage_bean_stock(vault_data)
        elif choice == "3":
            input(
                "\n[INFO] Screen 3: Recipe ratio calculations coming next. Press Enter..."
            )
        elif choice == "4":
            input(
                "\n[INFO] Screen 4: Threshold value configuration interface coming next. Press Enter..."
            )
        elif choice == "5":
            print("\nFlushing tracking cache matrices to disk... Data synced!")
            save_vault(vault_data)
            print("Shutdown operation clean. Goodbye!\n")
            sys.exit(0)
        else:
            input("\n[WARN] Invalid index selected. Press Enter to clear buffer...")


if __name__ == "__main__":
    main()
