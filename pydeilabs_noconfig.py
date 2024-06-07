import os
import sys
import requests
from getpass import getpass
from bs4 import BeautifulSoup

# Configuration
host = "https://deilabs.dei.unipd.it"
login_page = f"{host}/login"
lab_in_out_page = f"{host}/laboratory_in_outs"

# Global configuration variables
config_name = ""
config_lab = ""
config_psw = ""


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


def configure(args):
    global config_name, config_lab, config_psw

    if '-n' in args:
        config_name = args[args.index('-n') + 1]
    if '-l' in args:
        config_lab = args[args.index('-l') + 1]
    if '-p' in args:
        config_psw = getpass("Enter DEI account password: ")
    if '-r' in args:
        config_psw = ""
        print("Password reset")


def main():
    global config_name, config_lab, config_psw

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

    if not config_name or not config_lab:
        print("Configuration incomplete")
        sys.exit(1)

    if not config_psw:
        config_psw = getpass(f"Password for {config_name}: ")

    session = requests.Session()

    if 'in' in sys.argv or len(sys.argv) == 1:
        do_login(session, config_name, config_psw)
        lab_id = find_lab(session, config_lab)
        enter_lab(session, lab_id)
    else:
        print("Invalid argument")
        sys.exit(1)


if __name__ == "__main__":
    main()
