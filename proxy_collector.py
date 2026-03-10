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
    '@VpnTvGp', '@VPN_iransaz', '@chat_nakoni',
    '@MamadMango',
    '@PrVpn_Robot',
    '@VPNHamrahBOT',
    '@erfzi',
    '@CHAT_NAKONE',
    '@FreeNeetIrani',
    '@poopnetvpnbot',
    '@betty',
    '@belinga',
    '@marzha',
    '@vpn_seller_v2ray',
    '@safar65',
    '@Qiebt',
    '@shop',
    '@HADiViRUS',
    '@V2_Ciity',
    '@C12H7Cl2Bro2',
    '@poland2',
    '@Supervisor404',
    '@Dr1414_1414',
    '@pm_nsi',
    '@sina7cri',
    '@vip2',
    '@Shafaqm',
    '@azolany',
    '@hajika_v2_bot',
    '@hhhnju',
    '@HTTPINJECTORGROUP',
    '@sowgandns',
    '@Turbo2ProxyBot',
    '@custom2',
    '@Blue22',
    '@Sherminw',
    '@v2rayghavii',
    '@Oxigenserver2bot',
    '@ret20',
    '@vpn_proxy666',
    '@Ela83220',
    '@My_vpnshopbot',
    '@Bahar_SP2',
    '@TsTeamShopBot',
    '@serveride',
    '@Busneess_iebot',
    '@Behzad_mawludi',
    '@amitsluug',
    '@oxigen_sup',
    '@NaYab_Support',
    '@unxorn',
    '@iraan4',
    '@Mhmv2ray_bot',
    '@rtxti',
    '@Serveretbot',
    '@TBG21_Support',
    '@SoftNetConnect_bot',
    '@MMDLeecherNimBot',
    '@UNKNOWN9LADY',
    '@ConfigPixelArtBot',
    '@GithubGitlabDownloader_bot',
    '@sam580233',
    '@norbert',
    '@Eag1e_YT_GP',
    '@YamYamProxy1',
    '@photon',
    '@v2ray443_support',
    '@InfinityNetSupport',
    '@UYTRDESWERT',
    '@exchi']

DEFAULT_CHANNELS = ['@ShadowProxy66',
    '@england',
    '@OUTLINE_VPN',
    '@Netshot1',
    '@proxy_arak',
    '@NETBAZTM',
    '@blackray',
    '@PRoXY_V2ry',
    '@V2RY_PROXY',
    '@ROJPROXY',
    '@FALLENVPN',
    '@durov',
    '@Kamkarstore',
    '@v_ngfree',
    '@BrilliantGift',
    '@BINNER_IRAN',
    '@send_config',
    '@info',
    '@tik7net_vpn',
    '@initvpn',
    '@blueshop4',
    '@v2raymeli',
    '@vpn_proxy66',
    '@v2proxfree',
    '@ProxyArc',
    '@Laxtm',
    '@PRONET_CLUB',
    '@kamkarstore',
    '@V2RAYVPNCHANNEL',
    '@vasalbemon',
    '@irshum2',
    '@ISPEEDTOPVPN',
    '@d1eghbali',
    '@SHADOWPROXY66',
    '@VPN_PASARGAD',
    '@ConfigV2rayy',
    '@Confing_Network',
    '@PraivetVPN',
    '@DirectVPN',
    '@filembad',
    '@VIPVPN_AF',
    '@Tolee_azadi',
    '@BELOOVEDSHOP',
    '@VPNX44',
    '@ASTROVPN_OFFICIAL',
    '@Ghoghnoosv2ray',
    '@FREEV2RNG',
    '@numb_frozen',
    '@ProxyMTProtoIR',
    '@frekansSad',
    '@dr_news2',
    '@Capoit',
    '@Vpn_freenett',
    '@Mtiii14',
    '@FREECONFIGSPLUS',
    '@AMYRAXVPN',
    '@firenetspeed',
    '@V2RAY1000',
    '@sr011',
    '@Rahin_vpn',
    '@v2rayfree_irani',
    '@OUTLINE_IR',
    '@FNETPRO',
    '@iicenet',
    '@XBAT_TEAM',
    '@Net2ray',
    '@FARAZV2RAY',
    '@Argo_VPN1',
    '@netmelinpv',
    '@proxymtpvpn',
    '@V2RAY1_NG',
    '@filtershekan_channel',
    '@games',
    '@saadafiiiiii',
    '@FERIVP',
    '@hanikowproxi',
    '@SAGHI_PROXY1',
    '@Config_proxy_channel',
    '@v2rayng_proxymelli',
    '@mohmdvfx',
    '@VPNCISCO5STAR',
    '@Me_mogen',
    '@Zero_proxy1',
    '@velenjak',
    '@vampiirem',
    '@vpnfast2ray',
    '@CroSs_Guildd',
    '@blackRay',
    '@FreeConfigi',
    '@MamelekatDaily',
    '@Nftvici',
    '@OborV2ray',
    '@evdirext',
    '@Alphav2ray',
    '@turkey',
    '@mtn_config',
    '@NetZoneNews',
    '@KAFKASPEED',
    '@entekhabat',
    '@v2rayng_Fast',
    '@YamYamProxy',
    '@ZERO_PROXY1',
    '@proxyhubss',
    '@ARGO_VPNN',
    '@RAD_CR_VPN',
    '@v_2ra_yng',
    '@vipde1',
    '@AlFAProxy',
    '@anushavpn',
    '@IPMANTEAM',
    '@ONE_SHOP_OFFICIAL',
    '@BUGFREENET',
    '@kanivpn',
    '@oliver_soul',
    '@GlobalNews_TV',
    '@nvv2r',
    '@MELIPROXYY',
    '@Ha8TagShop',
    '@iran_connect1',
    '@Fouadi1',
    '@wangcai2',
    '@NaYab_Net',
    '@exonac',
    '@xservervpn',
    '@tunneltofan',
    '@V2RACONFING',
    '@zep_shopp'] 

NETMOD_FILE = 'netmod_configs.txt'
SLIPNET_FILE = 'slipnet_configs.txt'
DNS_FILE = 'dns_ips.txt'                 # فایل ذخیره‌سازی DNS‌ها
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
        # کانفیگ‌های جدید در این اجرا
        self.netmod_new_configs = set()
        self.slipnet_new_configs = set()
        self.netmod_new_count = 0
        self.slipnet_new_count = 0
        # DNS‌های جدید در این اجرا
        self.dns_new_ips = set()
        self.dns_new_count = 0
        # تمام DNS‌های دیده‌شده تاکنون (بارگذاری شده از فایل)
        self.dns_all_ips = set()
        self.discovered_usernames = set()
        self.group_stats = {chat: {'netmod': 0, 'slipnet': 0, 'dns': 0} for chat in self.all_chats}

    def load_dns_ips(self):
        """بارگذاری DNS‌های ذخیره‌شده قبلی از فایل"""
        if os.path.exists(DNS_FILE):
            with open(DNS_FILE, 'r', encoding='utf-8') as f:
                for line in f:
                    ip = line.strip()
                    if ip:
                        self.dns_all_ips.add(ip)

    def save_configs_to_file(self):
        """ذخیره کانفیگ‌های جدید در فایل (بازنویسی کامل)"""
        with open(NETMOD_FILE, 'w', encoding='utf-8') as f:
            for config in sorted(self.netmod_new_configs):
                f.write(config + '\n')
        with open(SLIPNET_FILE, 'w', encoding='utf-8') as f:
            for config in sorted(self.slipnet_new_configs):
                f.write(config + '\n')

    def save_dns_to_file(self):
        """افزودن DNS‌های جدید به فایل (بدون تکرار)"""
        # آی‌پی‌هایی که کاملاً جدید هستند (نه در فایل قبلی و نه در این اجرا ذخیره شده‌اند)
        truly_new = self.dns_new_ips - self.dns_all_ips
        if truly_new:
            with open(DNS_FILE, 'a', encoding='utf-8') as f:
                for ip in sorted(truly_new):
                    f.write(ip + '\n')
            # به‌روزرسانی مجموعه کل
            self.dns_all_ips.update(truly_new)

    def extract_configs(self, text):
        """استخراج کانفیگ‌های NetMod و Slipnet"""
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

    def extract_dns_ips(self, text):
        """
        استخراج آدرس‌های IPv4 که بعد از آنها فاصله یا انتهای خط آمده باشد.
        الگو: چهار عدد که با نقطه جدا شده‌اند و پس از آن فضای خالی یا پایان رشته است.
        """
        if not text:
            return []
        # IPv4 با lookahead برای اطمینان از اینکه بعد از IP فاصله یا پایان است
        pattern = r'\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)(?=\s|$)'
        matches = re.findall(pattern, text)
        # حذف تکراری‌ها
        return list(dict.fromkeys(matches))

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
        """بررسی پیام‌های ۲۴ ساعت گذشته در همه چت‌ها"""
        one_hour_ago = datetime.now() - timedelta(hours=120)
        for chat_username in self.all_chats:
            try:
                chat = await self.client.get_entity(chat_username)
                async for message in self.client.iter_messages(chat):
                    if message.date.replace(tzinfo=None) < one_hour_ago:
                        break
                    if message.text:
                        # کانفیگ‌ها
                        configs = self.extract_configs(message.text)
                        for config in configs['netmod']:
                            if config not in self.netmod_new_configs:
                                self.netmod_new_configs.add(config)
                                self.netmod_new_count += 1
                                self.group_stats[chat_username]['netmod'] += 1
                        for config in configs['slipnet']:
                            if config not in self.slipnet_new_configs:
                                self.slipnet_new_configs.add(config)
                                self.slipnet_new_count += 1
                                self.group_stats[chat_username]['slipnet'] += 1
                        # DNS‌ها
                        dns_ips = self.extract_dns_ips(message.text)
                        for ip in dns_ips:
                            if ip not in self.dns_all_ips and ip not in self.dns_new_ips:
                                self.dns_new_ips.add(ip)
                                self.dns_new_count += 1
                                self.group_stats[chat_username]['dns'] += 1
                        # mentions
                        mentions = self.extract_mentions(message.text)
                        self.discovered_usernames.update(mentions)
            except Exception as e:
                print(f"Error processing {chat_username}: {e}")
                continue

    async def handle_new_message(self, event):
        """مدیریت پیام‌های جدید"""
        message = event.message
        chat = await event.get_chat()
        chat_username = chat.username if hasattr(chat, 'username') else None
        if chat_username and message.text:
            # کانفیگ‌ها
            configs = self.extract_configs(message.text)
            for config in configs['netmod']:
                if config not in self.netmod_new_configs:
                    self.netmod_new_configs.add(config)
                    self.netmod_new_count += 1
                    if chat_username in self.group_stats:
                        self.group_stats[chat_username]['netmod'] += 1
            for config in configs['slipnet']:
                if config not in self.slipnet_new_configs:
                    self.slipnet_new_configs.add(config)
                    self.slipnet_new_count += 1
                    if chat_username in self.group_stats:
                        self.group_stats[chat_username]['slipnet'] += 1
            # DNS‌ها
            dns_ips = self.extract_dns_ips(message.text)
            for ip in dns_ips:
                if ip not in self.dns_all_ips and ip not in self.dns_new_ips:
                    self.dns_new_ips.add(ip)
                    self.dns_new_count += 1
                    if chat_username in self.group_stats:
                        self.group_stats[chat_username]['dns'] += 1
            # mentions
            mentions = self.extract_mentions(message.text)
            self.discovered_usernames.update(mentions)

    async def classify_discovered(self):
        if not self.discovered_usernames:
            return 0, 0
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
            self.group_stats[g] = {'netmod': 0, 'slipnet': 0, 'dns': 0}
        return len(new_groups), len(new_channels)

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
        total_netmod = len(self.netmod_new_configs)
        total_slipnet = len(self.slipnet_new_configs)
        total_dns = len(self.dns_all_ips)  # کل DNS‌های ذخیره‌شده تا الان

        # ارسال فایل NetMod
        if self.netmod_new_configs:
            caption = f"NetMod Configs - {current_time}\nTotal: {total_netmod}"
            try:
                with open(NETMOD_FILE, 'rb') as f:
                    url = f"https://api.telegram.org/bot{telegram_bot_token}/sendDocument"
                    files = {'document': f}
                    data = {'chat_id': telegram_chat_id, 'caption': caption}
                    requests.post(url, data=data, files=files, timeout=60)
            except Exception:
                pass

        # ارسال فایل Slipnet
        if self.slipnet_new_configs:
            caption = f"Slipnet Configs - {current_time}\nTotal: {total_slipnet}"
            try:
                with open(SLIPNET_FILE, 'rb') as f:
                    url = f"https://api.telegram.org/bot{telegram_bot_token}/sendDocument"
                    files = {'document': f}
                    data = {'chat_id': telegram_chat_id, 'caption': caption}
                    requests.post(url, data=data, files=files, timeout=60)
            except Exception:
                pass

        # ارسال فایل DNS (در صورت وجود DNS جدید در این اجرا)
        if self.dns_new_count > 0:
            caption = f"DNS IPs - {current_time}\nTotal unique: {total_dns}  (New: {self.dns_new_count})"
            try:
                with open(DNS_FILE, 'rb') as f:
                    url = f"https://api.telegram.org/bot{telegram_bot_token}/sendDocument"
                    files = {'document': f}
                    data = {'chat_id': telegram_chat_id, 'caption': caption}
                    requests.post(url, data=data, files=files, timeout=60)
            except Exception:
                pass

    def print_stats(self, new_groups_count, new_channels_count):
        print("\n=== Config Collection Summary ===")
        print(f"New NetMod configs: {self.netmod_new_count}")
        print(f"New Slipnet configs: {self.slipnet_new_count}")
        print(f"New DNS IPs: {self.dns_new_count}")
        print(f"Total unique NetMod in this run: {len(self.netmod_new_configs)}")
        print(f"Total unique Slipnet in this run: {len(self.slipnet_new_configs)}")
        print(f"Total unique DNS collected so far: {len(self.dns_all_ips)}")
        print(f"Discovered usernames: {len(self.discovered_usernames)}")
        print(f"  -> New groups: {new_groups_count}")
        print(f"  -> New channels: {new_channels_count}")
        print("\nPer chat statistics:")
        for chat, counts in self.group_stats.items():
            if counts['netmod'] > 0 or counts['slipnet'] > 0 or counts['dns'] > 0:
                print(f"{chat}: NetMod={counts['netmod']}, Slipnet={counts['slipnet']}, DNS={counts['dns']}")
        if self.discovered_usernames:
            print(f"\nDiscovered usernames: {', '.join(sorted(self.discovered_usernames))}")
        print("================================")

    async def start(self):
        if not self.download_session():
            print("Failed to download session file")
            return
        # بارگذاری DNS‌های قبلی
        self.load_dns_ips()
        self.client = TelegramClient(SESSION_FILE, int(api_id), api_hash)
        @self.client.on(events.NewMessage(chats=self.all_chats))
        async def message_handler(event):
            await self.handle_new_message(event)
        await self.client.start(phone=phone_number)
        print("Connected. Fetching messages from last hour...")
        await self.fetch_recent_messages()
        new_groups_count, new_channels_count = await self.classify_discovered()
        self.save_configs_to_file()
        self.save_dns_to_file()       # ذخیره DNS‌های جدید به‌صورت افزایشی
        self.print_stats(new_groups_count, new_channels_count)
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
