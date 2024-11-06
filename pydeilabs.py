import os
import sys
import requests
import configparser
from getpass import getpass
from bs4 import BeautifulSoup

# Determine the script's directory
script_dir = os.path.dirname(os.path.realpath(__file__))

# Configuration
host = "https://deilabs.dei.unipd.it"
login_page = f"{host}/login"
lab_in_out_page = f"{host}/laboratory_in_outs"
config_dir = os.path.join(script_dir, "config")
cookies_file = os.path.join(config_dir, "cookies.txt")
exit_file = os.path.join(config_dir, "exit_url")
configfile = os.path.join(config_dir, "setup.config")

# Ensure configuration directory exists
os.makedirs(config_dir, exist_ok=True)

# Load configuration
config = configparser.ConfigParser(allow_no_value=True)
if os.path.exists(configfile):
    config.read(configfile)


def save_config(configfile_path):
    with open(configfile_path, 'w') as file:
        config.write(file)


def get_token(session):
    response = session.get(login_page)
    soup = BeautifulSoup(response.text, 'html.parser')
    token = soup.find('input', {'name': '_token'})['value']
    return token


def do_login(session, email, password):
    token = get_token(session)
    payload = {
        '_token': token,
        'email': email,
        'password': password,
        'remember': '0'
    }
    response = session.post(login_page, data=payload)
    if "Login" in response.text:
        print("Failed login")
        sys.exit(1)


def get_labs(session):
    response = session.get(lab_in_out_page)
    if response.text.__contains__('Exit from'):
        print("Already entered")
        sys.exit(1)
    soup = BeautifulSoup(response.text, 'html.parser')
    options = soup.find_all('option')
    labs = {option['value']: option.text.strip() for option in options}
    return labs


def find_lab(session, lab_name):
    labs = get_labs(session)
    lab_ids = [lab_id for lab_id, name in labs.items() if lab_name in name]

    if not lab_ids:
        print("No laboratory matches the supplied label. Aborting")
        sys.exit(1)
    elif len(lab_ids) > 1:
        print("Multiple laboratories match the supplied label. Aborting")
        sys.exit(1)

    return lab_ids[0]


def enter_lab(session, lab_id):
    token = get_token(session)
    payload = {
        '_token': token,
        'laboratory_id': lab_id
    }
    response = session.post(lab_in_out_page, data=payload)
    if "OK" in response.text:
        print("Successfully entered lab")
    else:
        print("Failed entering. Unexpected error occurred")
        sys.exit(1)

    soup = BeautifulSoup(response.text, 'html.parser')
    exit_url = soup.find('form', {'id': 'edit_laboratory_in_outs_form'})['action']
    with open(exit_file, 'w') as f:
        f.write(exit_url)


def exit_lab(session):
    if not os.path.exists(exit_file):
        print("Not logged in from CLI. Aborting")
        sys.exit(1)

    with open(exit_file, 'r') as f:
        exit_url = f.read().strip()

    token = get_token(session)
    payload = {
        '_token': token,
        '_method': 'PUT'
    }
    response = session.post(exit_url, data=payload)
    if "OK" in response.text:
        print("Successfully exited")
    else:
        print("Failed exiting. Unexpected error occurred")
        sys.exit(1)


def configure(args):
    if '-n' in args:
        config['DEFAULT']['name'] = args[args.index('-n') + 1]
    if '-l' in args:
        config['DEFAULT']['lab'] = args[args.index('-l') + 1]
    if '-p' in args:
        password = getpass("Enter DEI account password: ")
        config['DEFAULT']['psw'] = password
    if '-r' in args:
        config['DEFAULT'].pop('psw', None)
        print("Password reset")

    save_config(configfile)


def main():
    if '-h' in sys.argv or '--help' in sys.argv:
        print("Usage: python3 script.py [configuration] [in|out]")
        print("  Configure:")
        print("    -n NAME     Set DEI account name")
        print("    -l LAB      Set current office name, format e.g.: 330 DEI/A")
        print("    -p          Set user password (WARNING: saved unencrypted)")
        print("    -r          Reset password")
        print("  Register entry/exit:")
        print("    in          Register entry with current configuration")
        print("    out         Register exit with current configuration")
        sys.exit(0)

    if '-n' in sys.argv or '-l' in sys.argv or '-p' in sys.argv or '-r' in sys.argv:
        configure(sys.argv)
        sys.exit(0)

    email = config['DEFAULT'].get('name', '')
    lab = config['DEFAULT'].get('lab', '')
    password = config['DEFAULT'].get('psw', '')

    if not email or not lab:
        print("Configuration incomplete")
        sys.exit(1)

    if not password:
        password = getpass(f"Password for {email}: ")

    session = requests.Session()

    if 'in' in sys.argv:
        do_login(session, email, password)
        lab_id = find_lab(session, lab)
        enter_lab(session, lab_id)
    elif 'out' in sys.argv:
        do_login(session, email, password)
        exit_lab(session)
    else:
        print("Invalid argument")
        sys.exit(1)


if __name__ == "__main__":
    main()
