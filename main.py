from seleniumwire import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import discord
import asyncio
from os import environ

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
tree = discord.app_commands.CommandTree(client)

@client.event
async def on_ready():
    print('ready')
    await tree.sync()
    print("command tree sync'd")


@tree.command(
        name='ping',
        description='ping the bot, to see if it is online'
)
async def ping(interaction: discord.Interaction):
        await interaction.response.send_message("pong!", ephemeral=True)
        print("pong'd")

@tree.command(
        name='info',
        description='learn more about this bot!'
)
async def info(interaction: discord.Interaction):
    interaction.response.send_message(
        'This is a discord bot developed by riamtyn (1149377905021952000 discord user id). \n \
        It is intended to be locally hosted. No user information is stored. \
        It works by creating a headless browser, which navigates to https://am0.riseofcultures.com/. \
        (change if you play on a different server, this is for the american server.) If you want to use this bot, \
        learn more about it, or improve it, check out the github page: https://github.com/riamtyn/X-Auth-Token_Retriever_Discord-Bot/ ',
        ephemeral=True
    )

@tree.command(
        name='token',
        description='get your X-Auth-Token.'
)
async def token(interaction: discord.Interaction):
        try:
            await interaction.response.send_message(content="loading...", ephemeral=True)
            options = Options()
            options.add_argument("--headless")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--window-size=1920,1080")
            driver = webdriver.Chrome(options=options)
            driver.get('https://am0.riseofcultures.com/')
            print("headless browser intilized")

            wait = WebDriverWait(driver, 10)

            await interaction.edit_original_response(content="logging in... estimated time: ~15s")

            await asyncio.sleep(15) #simplest way to let the page load

            username_field = wait.until(EC.presence_of_element_located((By.ID, "page_login_always-visible_input_player-identifier")))
            password_field = driver.find_element(By.ID, "page_login_always-visible_input_password")

            username_field.send_keys(environ.get("env_acc_email"))
            password_field.send_keys(environ.get("env_acc_pass"))

            login_button = driver.find_element(By.ID, "page_login_always-visible_button_login")
            login_button.click()
            print("logged in")

            await interaction.edit_original_response(content="waiting for the game to load... estimated time: ~2min")

            token = None
            iteration = 0
            while token is None and iteration < 90: #timeout = 3 min, because we sleep for 2 seconds per check
                for request in driver.requests:
                    if 'X-Auth-Token' in request.headers:
                        token = request.headers['X-Auth-Token'] 
                        print("found token")
                        #print(f'Found token: {token}') <-- don't log the token y'know?
                        break
                iteration += 1
                await asyncio.sleep(2)

            driver.quit() #stop the headless browser
            if token:
                await interaction.edit_original_response(content=f'your X-Auth-Token: ||{token}||') #send token as spoiler
                await interaction.followup.send(content=f"@{interaction.user}", ephemeral=True)
                print("token returned to user")
            else:
                await interaction.edit_original_response(content=f'No token found, Timeout reached. (sorry, try again?)')
                await interaction.followup.send(content=f'@{interaction.user}', ephemeral=True)
                print("token failed to return to user")
        except Exception as e:
            await interaction.edit_original_response(content=f'Error: {e}')
            await interaction.followup.send(content=f'@{interaction.user}', ephemeral=True)
            driver.quit()
            print("headless browser or log in failed")

client.run(environ.get('env_client_token'))


'''
major issues currently:
- if element id's change, the automated browser will fail
- logs the user out, because only one session can be active
- easily able to be overloaded, need to make a queing system
'''
