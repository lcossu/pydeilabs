import asyncio
import aiohttp
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

# to use in HomeAssistant with the HACS addon pyscript change the main function to the service name
# and add the @service decorator
async def main():
    global config_name, config_lab, config_psw

    if not config_name or not config_lab:
        print("Configuration incomplete")
        return 1

    if not config_psw:
        config_psw = getpass(f"Password for {config_name}: ")

    async with aiohttp.ClientSession() as session:
        # Get the CSRF token for login
        async with session.get(login_page) as response:
            text = await response.text()
            soup = BeautifulSoup(text, 'html.parser')
            token = soup.find('input', {'name': '_token'})['value']

        # Perform login
        payload = {
            '_token': token,
            'email': config_name,
            'password': config_psw,
            'remember': '0'
        }
        async with session.post(login_page, data=payload) as response:
            text = await response.text()
            if "Login" in text:
                print("Failed login")
                return 1

        # Get lab IDs
        async with session.get(lab_in_out_page) as response:
            text = await response.text()
            soup = BeautifulSoup(text, 'html.parser')
            if text.__contains__('Exit from'):
                print("Already entered")
                return 1
            options = soup.find_all('option')
            labs = {option['value']: option.text.strip() for option in options}

        lab_ids = [lab_id for lab_id, name in labs.items() if config_lab in name]

        if not lab_ids:
            print("No laboratory matches the supplied label. Aborting")
            return 1
        elif len(lab_ids) > 1:
            print("Multiple laboratories match the supplied label. Aborting")
            return 1

        lab_id = lab_ids[0]

        # Enter the lab
        payload = {
            '_token': token,
            'laboratory_id': lab_id
        }
        async with session.post(lab_in_out_page, data=payload) as response:
            text = await response.text()
            if "OK" in text:
                print("Successfully entered lab")
            else:
                print("Failed entering. Unexpected error occurred")
                return 1

if __name__ == "__main__":
    asyncio.run(main())
