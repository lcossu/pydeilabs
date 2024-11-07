import configparser
import os
import sys
from tkinter import Tk, Label, Entry, Button, messagebox
import requests
from bs4 import BeautifulSoup

# Configurazione iniziale
if sys.platform == 'win32':
    config_dir = os.path.join(os.getenv('APPDATA'), 'pydeilabs')
elif sys.platform == 'darwin':
    config_dir = os.path.join(os.getenv('HOME'), 'Library/Application Support', 'pydeilabs')
else:
    config_dir = os.path.join(os.getenv('HOME'), '.config', 'pydeilabs')

host = "https://deilabs.dei.unipd.it"
login_page = f"{host}/login"
lab_in_out_page = f"{host}/laboratory_in_outs"
exit_file = os.path.join(config_dir, "exit_url")
configfile = os.path.join(config_dir, "setup.config")
os.makedirs(config_dir, exist_ok=True)

config = configparser.ConfigParser(allow_no_value=True)
if os.path.exists(configfile):
    config.read(configfile)

def save_config():
    with open(configfile, 'w') as file:
        config.write(file)

def get_token(session):
    response = session.get(login_page)
    soup = BeautifulSoup(response.text, 'html.parser')
    token = soup.find('input', {'name': '_token'})['value']
    return token

def show_error_and_open_gui(title, message):
    messagebox.showerror(title, message)
    open_gui()

def do_login(session, email, password):
    try:
        token = get_token(session)
        payload = {
            '_token': token,
            'email': email,
            'password': password,
            'remember': '0'
        }
        response = session.post(login_page, data=payload)
        if "Login" in response.text:
            show_error_and_open_gui("Login Fallito", "Login non riuscito")
            return False
        return True
    except Exception as e:
        show_error_and_open_gui("Errore", f"Errore durante il login: {e}")
        return False

def get_labs(session):
    response = session.get(lab_in_out_page)
    if response.text.__contains__("Exit from"):
        messagebox.showinfo("Già entrato", "Sei già entrato nel laboratorio")
        sys.exit(1)
    soup = BeautifulSoup(response.text, 'html.parser')
    options = soup.find_all('option')
    labs = {option['value']: option.text.strip() for option in options}
    return labs

def find_lab(session, lab_name):
    labs = get_labs(session)
    lab_ids = [lab_id for lab_id, name in labs.items() if lab_name in name]

    if not lab_ids:
        show_error_and_open_gui("Errore", "Nessun laboratorio corrisponde al nome fornito.")
        sys.exit(1)
    elif len(lab_ids) > 1:
        show_error_and_open_gui("Errore", "Trovati più laboratori corrispondenti al nome fornito.")
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
        messagebox.showinfo("Successo", "Ingresso in laboratorio effettuato con successo!")
    else:
        show_error_and_open_gui("Errore", "Errore durante l'ingresso in laboratorio.")

    soup = BeautifulSoup(response.text, 'html.parser')
    exit_url = soup.find('form', {'id': 'edit_laboratory_in_outs_form'})['action']
    with open(exit_file, 'w') as f:
        f.write(exit_url)

def automatic_login():
    session = requests.Session()
    email = config['DEFAULT'].get('name', '')
    password = config['DEFAULT'].get('psw', '')
    lab_name = config['DEFAULT'].get('lab', '')

    if email and password and lab_name:
        if do_login(session, email, password):
            lab_id = find_lab(session, lab_name)
            enter_lab(session, lab_id)
            sys.exit(0)
    else:
        show_error_and_open_gui("Configurazione Incompleta", "I dati di configurazione sono incompleti. Compila i campi nella finestra successiva.")

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Configurazione DEI Lab")
        self.root.configure(bg="lightgray")

        # Valori predefiniti presi dal file di configurazione
        default_name = config['DEFAULT'].get('name', '')
        default_lab = config['DEFAULT'].get('lab', '')
        default_password = config['DEFAULT'].get('psw', '')

        Label(root, text="Nome Utente:", bg="lightgray").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.name_entry = Entry(root, width=30)
        self.name_entry.insert(0, default_name)  # Inserisce il valore di default
        self.name_entry.grid(row=0, column=1, padx=10, pady=5)

        Label(root, text="Laboratorio:", bg="lightgray").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.lab_entry = Entry(root, width=30)
        self.lab_entry.insert(0, default_lab)  # Inserisce il valore di default
        self.lab_entry.grid(row=1, column=1, padx=10, pady=5)

        Label(root, text="Password:", bg="lightgray").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.password_entry = Entry(root, show="*", width=30)
        self.password_entry.insert(0, default_password)  # Inserisce il valore di default
        self.password_entry.grid(row=2, column=1, padx=10, pady=5)
        Button(root, text="Salva configurazione e entra", command=self.save_configuration).grid(row=3, column=0, columnspan=2, padx=10, pady=10)

    def save_configuration(self):
        config['DEFAULT']['name'] = self.name_entry.get()
        config['DEFAULT']['lab'] = self.lab_entry.get()
        config['DEFAULT']['psw'] = self.password_entry.get()
        save_config()
        messagebox.showinfo("Salvato", "Configurazione salvata con successo!")
        self.root.destroy()
        automatic_login()

def open_gui():
    root = Tk()
    app = App(root)
    root.mainloop()

# Avvio del programma
if __name__ == "__main__":
    if config['DEFAULT'].get('name') and config['DEFAULT'].get('lab') and config['DEFAULT'].get('psw'):
        automatic_login()
    else:
        open_gui()
