import re
import asyncio
from telethon import TelegramClient, events
from telethon.tl.types import Channel, Chat
import os
import requests
from datetime import datetime, timedelta
import sys

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

DEFAULT_CHANNELS = []  # add any default channels here

NETMOD_FILE = 'netmod_configs.txt'
SLIPNET_FILE = 'slipnet_configs.txt'
SESSION_FILE = 'session.session'

SESSION_URLS = [
    'https://github.com/S00SIS/tel/raw/refs/heads/main/session.session',
    'https://raw.githubusercontent.com/S00SIS/tel/main/session.session'
]

class ConfigCollector:
    def __init__(self):
        self.groups = DEFAULT_GROUPS.copy()
        self.channels = DEFAULT_CHANNELS.copy()
        self.all_chats = self.groups + self.channels
        self.netmod_configs = self.load_configs(NETMOD_FILE)
        self.slipnet_configs = self.load_configs(SLIPNET_FILE)
        self.netmod_new_count = 0
        self.slipnet_new_count = 0
        self.discovered_usernames = set()
        self.group_stats = {chat: {'netmod': 0, 'slipnet': 0} for chat in self.all_chats}

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
                if username not in self.all_chats:
                    valid.add(username)
        return valid

    async def fetch_recent_messages(self):
        one_hour_ago = datetime.now() - timedelta(hours=1)
        for chat_username in self.all_chats:
            try:
                chat = await self.client.get_entity(chat_username)
                async for message in self.client.iter_messages(chat):
                    if message.date.replace(tzinfo=None) < one_hour_ago:
                        break
                    if message.text:
                        configs = self.extract_configs(message.text)
                        for config in configs['netmod']:
                            if self.save_config(config, NETMOD_FILE, self.netmod_configs):
                                self.netmod_new_count += 1
                                self.group_stats[chat_username]['netmod'] += 1
                        for config in configs['slipnet']:
                            if self.save_config(config, SLIPNET_FILE, self.slipnet_configs):
                                self.slipnet_new_count += 1
                                self.group_stats[chat_username]['slipnet'] += 1
                        mentions = self.extract_mentions(message.text)
                        self.discovered_usernames.update(mentions)
            except Exception as e:
                print(f"Error processing {chat_username}: {e}")
                continue

    async def handle_new_message(self, event):
        message = event.message
        chat = await event.get_chat()
        chat_username = chat.username if hasattr(chat, 'username') else None
        if chat_username and message.text:
            configs = self.extract_configs(message.text)
            for config in configs['netmod']:
                if self.save_config(config, NETMOD_FILE, self.netmod_configs):
                    self.netmod_new_count += 1
                    if chat_username in self.group_stats:
                        self.group_stats[chat_username]['netmod'] += 1
            for config in configs['slipnet']:
                if self.save_config(config, SLIPNET_FILE, self.slipnet_configs):
                    self.slipnet_new_count += 1
                    if chat_username in self.group_stats:
                        self.group_stats[chat_username]['slipnet'] += 1
            mentions = self.extract_mentions(message.text)
            self.discovered_usernames.update(mentions)

    async def classify_discovered(self):
        if not self.discovered_usernames:
            return
        new_groups = []
        new_channels = []
        for username in self.discovered_usernames:
            try:
                entity = await self.client.get_entity(username)
                if isinstance(entity, Chat):
                    new_groups.append(username)
                elif isinstance(entity, Channel):
                    if entity.broadcast:
                        new_channels.append(username)
                    else:
                        new_groups.append(username)
                else:
                    new_groups.append(username)
            except Exception:
                continue
        if new_groups:
            self.groups.extend(new_groups)
        if new_channels:
            self.channels.extend(new_channels)
        self.all_chats = self.groups + self.channels
        for g in new_groups + new_channels:
            self.group_stats[g] = {'netmod': 0, 'slipnet': 0}

    def update_source_lists(self):
        script_path = sys.argv[0]
        with open(script_path, 'r', encoding='utf-8') as f:
            content = f.read()

        def update_list(name, new_items):
            pattern = re.compile(rf'({name}\s*=\s*\[)(.*?)(\])', re.DOTALL)
            match = pattern.search(content)
            if not match:
                return content
            start, inner, end = match.groups()
            existing_items = re.findall(r"'([^']*)'", inner)
            existing_set = set(existing_items)
            new_unique = [f"'{item}'" for item in new_items if item not in existing_set]
            if not new_unique:
                return content
            new_inner = inner.rstrip() + (',' if inner.strip() and not inner.strip().endswith(',') else '') + '\n    ' + ',\n    '.join(new_unique)
            new_content = content[:match.start(2)] + new_inner + content[match.end(2):]
            return new_content

        if self.groups != DEFAULT_GROUPS:
            new_groups = [g for g in self.groups if g not in DEFAULT_GROUPS]
            if new_groups:
                content = update_list('DEFAULT_GROUPS', new_groups)
        if self.channels != DEFAULT_CHANNELS:
            new_channels = [c for c in self.channels if c not in DEFAULT_CHANNELS]
            if new_channels:
                content = update_list('DEFAULT_CHANNELS', new_channels)

        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(content)

    async def send_to_telegram(self):
        if not telegram_bot_token or not telegram_chat_id:
            return
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M')
        total_netmod = len(self.netmod_configs)
        total_slipnet = len(self.slipnet_configs)
        if os.path.exists(NETMOD_FILE) and os.path.getsize(NETMOD_FILE) > 0:
            caption = f"NetMod Configs - {current_time}\nTotal: {total_netmod}"
            try:
                with open(NETMOD_FILE, 'rb') as f:
                    url = f"https://api.telegram.org/bot{telegram_bot_token}/sendDocument"
                    files = {'document': f}
                    data = {'chat_id': telegram_chat_id, 'caption': caption}
                    requests.post(url, data=data, files=files, timeout=60)
            except Exception:
                pass
        if os.path.exists(SLIPNET_FILE) and os.path.getsize(SLIPNET_FILE) > 0:
            caption = f"Slipnet Configs - {current_time}\nTotal: {total_slipnet}"
            try:
                with open(SLIPNET_FILE, 'rb') as f:
                    url = f"https://api.telegram.org/bot{telegram_bot_token}/sendDocument"
                    files = {'document': f}
                    data = {'chat_id': telegram_chat_id, 'caption': caption}
                    requests.post(url, data=data, files=files, timeout=60)
            except Exception:
                pass

    def print_stats(self):
        print("\n=== Config Collection Summary ===")
        print(f"New NetMod configs: {self.netmod_new_count}")
        print(f"New Slipnet configs: {self.slipnet_new_count}")
        print("\nPer chat statistics:")
        for chat, counts in self.group_stats.items():
            if counts['netmod'] > 0 or counts['slipnet'] > 0:
                print(f"{chat}: NetMod={counts['netmod']}, Slipnet={counts['slipnet']}")
        if self.discovered_usernames:
            print(f"\nDiscovered usernames: {', '.join(sorted(self.discovered_usernames))}")
        print("================================")

    async def start(self):
        if not self.download_session():
            print("Failed to download session file")
            return
        self.client = TelegramClient(SESSION_FILE, int(api_id), api_hash)
        @self.client.on(events.NewMessage(chats=self.all_chats))
        async def message_handler(event):
            await self.handle_new_message(event)
        await self.client.start(phone=phone_number)
        print("Connected. Fetching messages from last hour...")
        await self.fetch_recent_messages()
        await self.classify_discovered()
        self.print_stats()
        await self.send_to_telegram()
        self.update_source_lists()
        print("Waiting 2 minutes for new messages...")
        await asyncio.sleep(120)
        await self.client.disconnect()
        print("Disconnected.")

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

async def main():
    collector = ConfigCollector()
    try:
        await collector.start()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    asyncio.run(main())
