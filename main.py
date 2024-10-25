import os
import sys
import time
import json
from curl_cffi import requests
from datetime import datetime
from colorama import Fore, Style, init
from urllib.parse import parse_qs
from config.banner import show_banner

# Initialize colorama
init(autoreset=True)


class Colors:
    RED = Fore.LIGHTRED_EX
    WHITE = Fore.LIGHTWHITE_EX
    GREEN = Fore.LIGHTGREEN_EX
    YELLOW = Fore.LIGHTYELLOW_EX
    BLUE = Fore.LIGHTBLUE_EX
    BLACK = Fore.LIGHTBLACK_EX
    RESET = Style.RESET_ALL


class Config:
    API_BASE_URL = "https://moon.popp.club"
    WEB_REFERER = "https://planet.popp.club/"
    USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0"
    HEADERS = {
        "User-Agent": USER_AGENT,
        "Accept": "application/json",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "sec-ch-ua": '"Not/A)Brand";v="8", "Chromium";v="126", "Microsoft Edge";v="126", "Microsoft Edge WebView2";v="126"',
        "content-type": "application/json;charset=utf-8",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "Origin": WEB_REFERER.rstrip("/"),
        "Sec-Fetch-Site": "same-site",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Referer": WEB_REFERER,
        "Accept-Language": "en-US,en;q=0.9",
    }


class ApiResponse:
    def __init__(self, response):
        self.raw_response = response
        self.json_data = response.json()
        self.code = self.json_data.get("code")
        self.message = self.json_data.get("msg")
        self.data = self.json_data.get("data", {})

    def is_success(self):
        return str(self.code) == "200"

    def get_token(self):
        if not self.is_success():
            return None

        if isinstance(self.data, dict) and "token" in self.data:
            token = self.data["token"]
            if not token.startswith("Bearer "):
                token = f"Bearer {token}"
            return token
        return None

    def get_error_message(self):
        return self.message or "Unknown error occurred"


class TokenManager:
    @staticmethod
    def get_local_token(userid):
        if not os.path.exists("tokens.json"):
            open("tokens.json", "w").write(json.dumps({}))
        tokens = json.loads(open("tokens.json", "r").read())
        return tokens.get(str(userid), False)

    @staticmethod
    def save_local_token(userid, token):
        tokens = json.loads(open("tokens.json", "r").read())
        tokens[str(userid)] = token
        open("tokens.json", "w").write(json.dumps(tokens, indent=4))

    @staticmethod
    def save_failed_token(userid, data):
        file = "auth_failed.json"
        if not os.path.exists(file):
            open(file, "w").write(json.dumps({}))
        acc = json.loads(open(file, "r").read())
        if str(userid) not in acc:
            acc[str(userid)] = data
            open(file, "w").write(json.dumps(acc, indent=4))


class ApiClient:
    def __init__(self, token=None):
        self.headers = Config.HEADERS.copy()
        if token:
            if not token.startswith("Bearer "):
                token = f"Bearer {token}"
            self.headers["Authorization"] = token

    def post(self, endpoint, data=None, params=None):
        url = f"{Config.API_BASE_URL}{endpoint}"
        return requests.post(url, data=data, params=params, headers=self.headers)

    def get(self, endpoint, params=None):
        url = f"{Config.API_BASE_URL}{endpoint}"
        return requests.get(url, params=params, headers=self.headers)


class PoppBot:
    def __init__(self):
        self.separator = Colors.WHITE + "=" * 51

    @staticmethod
    def data_parsing(data):
        return {k: v[0] for k, v in parse_qs(data).items()}

    def format_number(self, number):
        return "{:,.2f}".format(float(number))

    def format_timestamp(self, timestamp):
        try:
            dt = datetime.fromtimestamp(int(timestamp) / 1000)
            return dt.strftime("%Y-%m-%d %H:%M:%S")
        except:
            return "Invalid timestamp"

    def log(self, message):
        if message.strip():
            print(
                f"{Colors.BLACK}[ {Colors.GREEN}Popp-BOT{Colors.BLACK} ]{Colors.RESET} {message}"
            )
        else:
            print()

    def countdown(self, t):
        while t:
            minutes, seconds = divmod(t, 60)
            hours, minutes = divmod(minutes, 60)
            timer = (
                f"{str(hours).zfill(2)}:{str(minutes).zfill(2)}:{str(seconds).zfill(2)}"
            )
            print(f"{Colors.YELLOW}waiting until {timer} ", flush=True, end="\r")
            t -= 1
            time.sleep(1)
        print(" " * 30, flush=True, end="\r")

    def get_asset_info(self, api_client):
        try:
            response = ApiResponse(api_client.get("/asset/info"))
            if response.is_success():
                data = response.data
                if isinstance(data, dict):
                    # Get address information
                    address = data.get("address", "N/A")
                    address_type = data.get("addressWalletType", "N/A")

                    # Get farming times
                    farming_start = self.format_timestamp(
                        data.get("farmingStartTime", 0)
                    )
                    farming_end = self.format_timestamp(data.get("farmingEndTime", 0))

                    # Get equipped ship info
                    equipped_ship = data.get("equippedShip", {})
                    ship_name = equipped_ship.get("name", "N/A")
                    ship_type = equipped_ship.get("type", "N/A")
                    ship_level = equipped_ship.get("level", "N/A")
                    ship_owned = self.format_timestamp(
                        equipped_ship.get("ownedTime", 0)
                    )

                    # Display information
                    self.log(f"{Colors.GREEN}ASSET INFORMATION")
                    self.log(f"{Colors.WHITE}> Address      : {address}")
                    self.log(f"{Colors.WHITE}> Wallet Type  : {address_type}")
                    self.log(f"{Colors.GREEN}FARMING SCHEDULE")
                    self.log(f"{Colors.WHITE}> Start Time   : {farming_start}")
                    self.log(f"{Colors.WHITE}> End Time     : {farming_end}")
                    self.log(f"{Colors.GREEN}EQUIPPED SHIP")
                    self.log(f"{Colors.WHITE}> Name         : {ship_name}")
                    self.log(f"{Colors.WHITE}> Type         : {ship_type}")
                    self.log(f"{Colors.WHITE}> Level        : {ship_level}")
                    self.log(f"{Colors.WHITE}> Owned Since  : {ship_owned}")
                else:
                    self.log(f"{Colors.RED}Invalid asset info format")
            else:
                self.log(f"{Colors.RED}Failed to get asset info")

        except Exception as e:
            self.log(f"{Colors.RED}Error getting asset info: {str(e)}")

    def renewAccessToken(self, query_id):
        try:
            parsed_data = self.data_parsing(query_id)
            try:
                user = json.loads(parsed_data["user"])
                chat_instance = parsed_data.get("chat_instance", "")
            except Exception as e:
                self.log(f"{Colors.RED}Failed to parse user data: {str(e)}")
                return False

            payload = {
                "initData": query_id,
                "initDataUnSafe": {
                    "user": {
                        "id": int(user["id"]),
                        "first_name": user.get("first_name", ""),
                        "last_name": user.get("last_name", ""),
                        "username": user.get("username", ""),
                        "language_code": user.get("language_code", "en"),
                        "allows_write_to_pm": True,
                        "is_premium": user.get("is_premium", 1),
                    },
                    "chat_instance": chat_instance,
                    "chat_type": "supergroup",
                    "start_param": "6944804952",
                    "auth_date": parsed_data.get("auth_date", ""),
                    "hash": parsed_data.get("hash", ""),
                },
                "inviteUid": "6944804952",
            }

            api_client = ApiClient()
            self.log(f"{Colors.YELLOW}Attempting login...")

            try:
                response = api_client.post("/pass/login", data=json.dumps(payload))
                api_response = ApiResponse(response)

                if api_response.is_success():
                    token = api_response.get_token()
                    if token:
                        self.log(f"{Colors.GREEN}Login successful")
                        return token
                    else:
                        self.log(f"{Colors.RED}Token not found in response")
                        return False
                else:
                    self.log(
                        f"{Colors.RED}Login failed: {api_response.get_error_message()}"
                    )
                    return False

            except Exception as e:
                self.log(f"{Colors.RED}API request failed: {str(e)}")
                return False

        except Exception as e:
            self.log(f"{Colors.RED}Login process failed: {str(e)}")
            return False

    def explore_planet(self, api_client, planet_id):
        try:
            response = ApiResponse(
                api_client.get("/moon/explorer", params={"plantId": planet_id})
            )

            if response.is_success():
                data = response.data
                if isinstance(data, dict):
                    index = data.get("index", 0)
                    special_code = data.get("specialCode")
                    self.log(
                        f"{Colors.GREEN}Planet {planet_id} explored - Index: {index} {special_code if special_code else ''}"
                    )
                else:
                    self.log(f"{Colors.RED}Invalid explorer response format")
            else:
                self.log(f"{Colors.RED}Failed exploring planet {planet_id}")

        except Exception as e:
            self.log(f"{Colors.RED}Error exploring planet {planet_id}: {str(e)}")

    def handle_farming(self, api_client):
        try:
            response = ApiResponse(api_client.get("/moon/claim/farming"))
            if response.is_success():
                self.log(f"{Colors.GREEN}Successfully claimed farming rewards")
            else:
                self.log(f"{Colors.RED}Failed to claim farming rewards")

            self.countdown(5)

            response = ApiResponse(api_client.get("/moon/farming"))
            if response.is_success():
                self.log(f"{Colors.GREEN}Successfully started farming")
            else:
                error_msg = response.get_error_message()
                if "already" in error_msg.lower():
                    self.log(f"{Colors.YELLOW}Farming already active")
                else:
                    self.log(f"{Colors.RED}Failed to start farming: {error_msg}")

        except Exception as e:
            self.log(f"{Colors.RED}Error in farming handler: {str(e)}")

    def claim_referral(self, api_client):
        try:
            response = ApiResponse(api_client.get("/moon/claim/invite"))
            if response.is_success():
                self.log(f"{Colors.GREEN}Successfully claimed referral bonus")
            else:
                self.log(f"{Colors.RED}Failed to claim referral bonus")
        except Exception as e:
            self.log(f"{Colors.RED}Error claiming referral: {str(e)}")

    def perform_game_actions(self, token):
        try:
            api_client = ApiClient(token)

            # Get detailed asset info first
            self.get_asset_info(api_client)

            # Get assets
            response = ApiResponse(api_client.get("/moon/asset"))
            if response.is_success():
                data = response.data
                if isinstance(data, dict):
                    sd = self.format_number(data.get("sd", 0))
                    probe = self.format_number(data.get("probe", 0))
                    eth = self.format_number(data.get("eth", 0))
                    self.log(f"{Colors.GREEN}BALANCE")
                    self.log(f"{Colors.WHITE}> SD    : {sd}")
                    self.log(f"{Colors.WHITE}> PROBE : {probe}")
                    self.log(f"{Colors.WHITE}> ETH   : {eth}")
                else:
                    self.log(f"{Colors.RED}Invalid asset data format")
                    return False
            else:
                self.log(f"{Colors.RED}Failed to get assets")
                return False

            # Explore planets
            self.log(f"{Colors.YELLOW}EXPLORING PLANETS")
            response = ApiResponse(api_client.get("/moon/planets"))
            if response.is_success() and isinstance(response.data, list):
                for planet in response.data:
                    if isinstance(planet, dict) and "id" in planet:
                        planet_id = planet["id"]
                        self.explore_planet(api_client, planet_id)
            else:
                self.log(f"{Colors.RED}Failed to get planets data")

            # Handle farming
            self.log(f"{Colors.BLUE}FARMING STATUS")
            self.handle_farming(api_client)

            # Handle referral
            self.log(f"{Colors.BLUE}REFERRAL STATUS")
            self.claim_referral(api_client)

            return True

        except Exception as e:
            self.log(f"{Colors.RED}Error during game actions: {str(e)}")
            return False

    def main(self):
        try:
            show_banner()
            print()

            if not os.path.exists("data.txt"):
                self.log(f"{Colors.RED}data.txt file not found!")
                return

            datas = open("data.txt", "r").read().splitlines()
            total_accounts = len(datas)

            if not datas:
                self.log(f"{Colors.RED}No account data found in data.txt")
                return

            failed_accounts = []
            while True:
                for no, data in enumerate(datas, 1):
                    try:
                        try:
                            data_parse = self.data_parsing(data)
                            user = json.loads(data_parse["user"])
                            userid = user["id"]
                            username = user.get("first_name", "Unknown")
                        except Exception as e:
                            self.log(
                                f"{Colors.RED}Error parsing account data: {str(e)}"
                            )
                            failed_accounts.append((no, "Data parsing error"))
                            continue

                        self.log(f"{Colors.GREEN}Login as: {Colors.WHITE}{username}")

                        access_token = TokenManager.get_local_token(userid)
                        if not access_token:
                            access_token = self.renewAccessToken(data)
                            if not access_token:
                                failed_accounts.append((no, username))
                                continue
                            TokenManager.save_local_token(userid, access_token)
                            self.countdown(5)

                        if not self.perform_game_actions(access_token):
                            failed_accounts.append(
                                (no, f"{username} - Game actions failed")
                            )
                            continue

                        self.countdown(5)
                        self.log(self.separator)

                    except Exception as e:
                        self.log(f"{Colors.RED}Error processing account {no}: {str(e)}")
                        failed_accounts.append((no, f"Unknown error: {str(e)}"))
                        continue

                if failed_accounts:
                    self.log(f"{Colors.YELLOW}Failed accounts this cycle:")
                    for acc_no, acc_name in failed_accounts:
                        self.log(f"{Colors.RED}Account {acc_no}: {acc_name}")
                    failed_accounts.clear()

                self.log(f"{Colors.YELLOW}Completed cycle")
                self.countdown(370)

        except KeyboardInterrupt:
            print()
            self.log(
                f"{Colors.YELLOW}Program stopped by user. Thank you for using Popp-BOT!"
            )
            sys.exit(0)
        except Exception as e:
            self.log(f"{Colors.RED}Critical error occurred: {str(e)}")


if __name__ == "__main__":
    app = PoppBot()
    app.main()
