import os
import subprocess
import sys

# --------------------
# Default agent name has been removed
# --------------------

def print_banner():
    """Prints a cool ASCII art banner."""
    os.system('clear') # Clears the screen
    banner = r"""
  ░██████  ░██████     ░███          ░████████              ░██    
 ░██   ░██░██   ░██   ░██░██         ░██    ░██             ░██    
░██      ░██         ░██  ░██        ░██    ░██  ░███████░████████ 
░██       ░████████ ░█████████░██████░████████  ░██    ░██  ░██    
░██              ░██░██    ░██       ░██     ░██░██    ░██  ░██    
 ░██   ░██░██   ░██ ░██    ░██       ░██     ░██░██    ░██  ░██    
  ░██████  ░██████  ░██    ░██       ░█████████  ░███████    ░████ 
    ---------------------------------------------------------------------
              Wazuh SCA AI Analyst - by Hazem Mohamed
    ---------------------------------------------------------------------
    """
    print(banner)

def get_failed_checks(agent_name):
    """Displays a list of all failed checks for the agent."""
    print(f"\n...Fetching all FAILED checks for agent: {agent_name}\n")
    try:
        # We will use the debug_sca.py script we created earlier for this task
        command = [
            sys.executable, "debug_sca.py", 
            "--agent-name", agent_name
        ]
        subprocess.run(command, check=True)
    except FileNotFoundError:
        print("Error: 'debug_sca.py' not found. Make sure it's in the same directory.")
    except subprocess.CalledProcessError:
        print("An error occurred while fetching the failed checks.")
    input("\nPress Enter to return to the main menu...")

def generate_report(agent_name, lang, format):
    """Generates a report for a single check ID."""
    try:
        check_id = input(f"\nPlease enter the Check ID to analyze for agent '{agent_name}': ")
        if not check_id.isdigit():
            print("\nInvalid input. Please enter a numeric ID.")
            input("\nPress Enter to return to the main menu...")
            return
            
        print(f"\n...Generating {format.upper()} report for Check ID {check_id} in '{lang.upper()}'\n")
        
        command = [
            sys.executable, "CSA_generator.py",
            "--agent-name", agent_name,
            "--check", check_id,
            "--lang", lang,
            "--format", format
        ]
        subprocess.run(command, check=True)

    except FileNotFoundError:
        print("Error: 'CSA_generator.py' not found. Make sure it's in the same directory.")
    except subprocess.CalledProcessError:
        print("An error occurred while generating the report.")
    input("\nPress Enter to return to the main menu...")


def main_menu():
    """Displays the main menu and handles user input."""
    while True:
        print_banner()
        # Default agent name line has been removed
        print("Please choose an option:")
        print("  [1] Generate Text Report (Arabic)")
        print("  [2] Generate Text Report (English)")
        print("  ------------------------------------")
        print("  [3] Generate PDF Report (Arabic)")
        print("  [4] Generate PDF Report (English)")
        print("  ------------------------------------")
        print("  [5] List All FAILED Check IDs")
        print("  [0] Exit")
        
        choice = input("\nEnter your choice: ")
        
        # --- Modified Section ---
        # Options that require an agent name
        if choice in ['1', '2', '3', '4', '5']:
            agent_name = input("\nPlease enter the Agent Name to analyze: ")
            if not agent_name:
                print("\nNo name entered. Returning to the main menu.")
                input("\nPress Enter to continue...")
                continue # Returns to the start of the loop

            if choice == '1':
                generate_report(agent_name, 'ar', 'text')
            elif choice == '2':
                generate_report(agent_name, 'en', 'text')
            elif choice == '3':
                generate_report(agent_name, 'ar', 'pdf')
            elif choice == '4':
                generate_report(agent_name, 'en', 'pdf')
            elif choice == '5':
                get_failed_checks(agent_name)

        elif choice == '0':
            print("\nExiting. Goodbye!\n")
            break
        else:
            print("\nInvalid choice, please try again.")
            input("\nPress Enter to continue...")

if __name__ == "__main__":
    # Note: Make sure the ai_engine.py script is running in another terminal
    main_menu()

