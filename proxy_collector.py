import re
import asyncio
from telethon import TelegramClient, events
import os
import requests
from datetime import datetime, timedelta

api_id = os.environ.get('API_ID')
api_hash = os.environ.get('API_HASH')
phone_number = os.environ.get('PHONE_NUMBER')
github_token = os.environ.get('GH_TOKEN')
telegram_bot_token = os.environ.get('TELEGRAM_BOT_TOKEN')
telegram_chat_id = os.environ.get('TELEGRAM_CHAT_ID')

DEFAULT_GROUPS = [
    '@chatnakonn', '@v2ray_proxyz', '@VasLshoGap', '@chat_naakon',
    '@FlexEtesal', '@chat_nakonnn', '@letsproxys', '@Alpha_V2ray_Group',
    '@VpnTvGp', '@VPN_iransaz', '@chat_nakoni'
]

GROUPS_FILE = 'monitored_groups.txt'
NETMOD_FILE = 'netmod_configs.txt'
SLIPNET_FILE = 'slipnet_configs.txt'
SESSION_FILE = 'session.session'

SESSION_URLS = [
    'https://github.com/S00SIS/tel/raw/refs/heads/main/session.session',
    'https://raw.githubusercontent.com/S00SIS/tel/main/session.session'
]

class ConfigCollector:
    def __init__(self):
        self.ensure_files_exist()
        self.group_usernames = self.load_groups()
        self.netmod_configs = self.load_configs(NETMOD_FILE)
        self.slipnet_configs = self.load_configs(SLIPNET_FILE)
        self.netmod_new_count = 0
        self.slipnet_new_count = 0
        self.discovered_groups = set()
        self.group_stats = {group: {'netmod': 0, 'slipnet': 0} for group in self.group_usernames}

    def ensure_files_exist(self):
        for filename in [NETMOD_FILE, SLIPNET_FILE, GROUPS_FILE]:
            if not os.path.exists(filename):
                with open(filename, 'w', encoding='utf-8') as f:
                    if filename == GROUPS_FILE:
                        f.write('\n'.join(DEFAULT_GROUPS) + '\n')

    def load_groups(self):
        groups = []
        if os.path.exists(GROUPS_FILE):
            with open(GROUPS_FILE, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        if not line.startswith('@'):
                            line = '@' + line
                        groups.append(line)
        if not groups:
            groups = DEFAULT_GROUPS
            self.save_groups(groups)
        return groups

    def save_groups(self, groups=None):
        if groups is None:
            groups = self.group_usernames
        with open(GROUPS_FILE, 'w', encoding='utf-8') as f:
            for g in sorted(groups):
                f.write(g + '\n')

    def download_session(self):
        if os.path.exists(SESSION_FILE):
            return True
        if not github_token:
            return False
        headers = {'Authorization': f'token {github_token}'}
        for url in SESSION_URLS:
            try:
                response = requests.get(url, headers=headers, timeout=30)
                if response.status_code == 200:
                    with open(SESSION_FILE, 'wb') as f:
                        f.write(response.content)
                    return True
            except Exception:
                continue
        return False

    def load_configs(self, filename):
        configs = set()
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        configs.add(line)
        return configs

    def save_config(self, config, filename, config_set):
        if config in config_set:
            return False
        with open(filename, 'a', encoding='utf-8') as f:
            if os.path.getsize(filename) > 0:
                f.write('\n')
            f.write(config + '\n')
        config_set.add(config)
        return True

    def extract_configs(self, text):
        if not text:
            return {'netmod': [], 'slipnet': []}
        result = {'netmod': [], 'slipnet': []}
        pattern = r'(nm-dns://[^\s<>"\'(){}|\\^`\[\]]+|slipnet-enc://[^\s<>"\'(){}|\\^`\[\]]+)'
        found = re.findall(pattern, text, re.IGNORECASE)
        for item in found:
            item = item.rstrip('.,;:!?)]}')
            if item.startswith('nm-dns://'):
                result['netmod'].append(item)
            elif item.startswith('slipnet-enc://'):
                result['slipnet'].append(item)
        result['netmod'] = list(dict.fromkeys(result['netmod']))
        result['slipnet'] = list(dict.fromkeys(result['slipnet']))
        return result

    def extract_mentions(self, text):
        if not text:
            return set()
        pattern = r'@(\w+)'
        mentions = re.findall(pattern, text)
        valid = set()
        for m in mentions:
            if len(m) >= 3 and not m.isdigit():
                username = '@' + m
                if username not in self.group_usernames:
                    valid.add(username)
        return valid

    async def fetch_recent_messages(self):
        one_hour_ago = datetime.now() - timedelta(hours=1)
        for group in self.group_usernames:
            try:
                chat = await self.client.get_entity(group)
                chat_title = chat.title if hasattr(chat, 'title') else chat.username
                async for message in self.client.iter_messages(chat):
                    if message.date.replace(tzinfo=None) < one_hour_ago:
                        break
                    if message.text:
                        configs = self.extract_configs(message.text)
                        for config in configs['netmod']:
                            if self.save_config(config, NETMOD_FILE, self.netmod_configs):
                                self.netmod_new_count += 1
                                self.group_stats[group]['netmod'] += 1
                        for config in configs['slipnet']:
                            if self.save_config(config, SLIPNET_FILE, self.slipnet_configs):
                                self.slipnet_new_count += 1
                                self.group_stats[group]['slipnet'] += 1
                        mentions = self.extract_mentions(message.text)
                        self.discovered_groups.update(mentions)
            except Exception as e:
                print(f"Error processing group {group}: {e}")
                continue

    async def handle_new_message(self, event):
        message = event.message
        chat = await event.get_chat()
        chat_username = chat.username if hasattr(chat, 'username') else None
        if message.text:
            configs = self.extract_configs(message.text)
            for config in configs['netmod']:
                if self.save_config(config, NETMOD_FILE, self.netmod_configs):
                    self.netmod_new_count += 1
                    if chat_username:
                        self.group_stats[chat_username]['netmod'] += 1
            for config in configs['slipnet']:
                if self.save_config(config, SLIPNET_FILE, self.slipnet_configs):
                    self.slipnet_new_count += 1
                    if chat_username:
                        self.group_stats[chat_username]['slipnet'] += 1
            mentions = self.extract_mentions(message.text)
            self.discovered_groups.update(mentions)

    async def send_to_telegram(self):
        if not telegram_bot_token or not telegram_chat_id:
            return
        current_date = datetime.now().strftime('%Y-%m-%d %H:%M')
        total_netmod = len(self.netmod_configs)
        total_slipnet = len(self.slipnet_configs)
        caption = f"Config Collector Report {current_date}\n\n"
        caption += f"New configs found:\n"
        caption += f"NetMod: {self.netmod_new_count}\n"
        caption += f"Slipnet: {self.slipnet_new_count}\n\n"
        caption += f"Total collected:\n"
        caption += f"NetMod: {total_netmod}\n"
        caption += f"Slipnet: {total_slipnet}\n"
        caption += f"Monitored groups: {len(self.group_usernames)}\n"
        if self.discovered_groups:
            caption += f"New groups discovered: {', '.join(sorted(self.discovered_groups))}"
        try:
            if os.path.exists(NETMOD_FILE) and os.path.getsize(NETMOD_FILE) > 0:
                with open(NETMOD_FILE, 'rb') as f:
                    url = f"https://api.telegram.org/bot{telegram_bot_token}/sendDocument"
                    files = {'document': f}
                    data = {'chat_id': telegram_chat_id, 'caption': caption}
                    requests.post(url, data=data, files=files, timeout=60)
            if os.path.exists(SLIPNET_FILE) and os.path.getsize(SLIPNET_FILE) > 0:
                with open(SLIPNET_FILE, 'rb') as f:
                    url = f"https://api.telegram.org/bot{telegram_bot_token}/sendDocument"
                    files = {'document': f}
                    data = {'chat_id': telegram_chat_id}
                    requests.post(url, data=data, files=files, timeout=60)
        except Exception:
            pass

    def print_stats(self):
        print("\n=== Config Collection Summary ===")
        print(f"Total new NetMod configs: {self.netmod_new_count}")
        print(f"Total new Slipnet configs: {self.slipnet_new_count}")
        print("\nPer group statistics:")
        for group, counts in self.group_stats.items():
            if counts['netmod'] > 0 or counts['slipnet'] > 0:
                print(f"{group}: NetMod={counts['netmod']}, Slipnet={counts['slipnet']}")
        if self.discovered_groups:
            print("\nNewly discovered groups (saved for future runs):")
            for g in sorted(self.discovered_groups):
                print(g)
        print("================================")

    async def start(self):
        if not self.download_session():
            print("Failed to download session file")
            return
        self.client = TelegramClient(SESSION_FILE, int(api_id), api_hash)
        @self.client.on(events.NewMessage(chats=self.group_usernames))
        async def message_handler(event):
            await self.handle_new_message(event)
        await self.client.start(phone=phone_number)
        print("Connected. Fetching messages from last hour...")
        await self.fetch_recent_messages()
        self.print_stats()
        await self.send_to_telegram()
        if self.discovered_groups:
            new_groups = list(set(self.discovered_groups) - set(self.group_usernames))
            if new_groups:
                self.group_usernames.extend(new_groups)
                self.save_groups()
                print(f"Added {len(new_groups)} new groups to monitored list.")
        print("Waiting 2 minutes for new messages...")
        await asyncio.sleep(120)
        await self.client.disconnect()
        print("Disconnected.")

async def main():
    collector = ConfigCollector()
    try:
        await collector.start()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    asyncio.run(main())
