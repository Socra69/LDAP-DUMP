import ipaddress
import socket
from getpass import getpass
from ldap3 import Server, Connection, ALL, SIMPLE, SYNC
import ldap3
from colorama import Fore, Style, init
import sys
from datetime import datetime
import os, os.path


class LDAPSearch:
    def __init__(self):
        self.username = None
        self.password = None
        self.hostname = None
        self.dom_con = None
        self.name_context = None
        self.dom_1 = None
        self.conn = None
        self.domain = None
        self.info = Fore.YELLOW + Style.BRIGHT
        self.fail = Fore.RED + Style.BRIGHT
        self.success = Fore.GREEN + Style.BRIGHT
        self.close = Style.RESET_ALL
        self.t1 = None
        self.t2 = None

    def banner(self):
        print(self.info + "")
        print('                   __    ____  ___    ____  ____')
        print('   ____ ___  _____/ /   / __ \/   |  / __ \/ __ \__  ______ ___  ____')
        print('  / __ `__ \/ ___/ /   / / / / /| | / /_/ / / / / / / / __ `__ \/ __ \ ')
        print(' / / / / / (__  ) /___/ /_/ / ___ |/ ____/ /_/ / /_/ / / / / / / /_/ /')
        print('/_/ /_/ /_/____/_____/_____/_/  |_/_/   /_____/\__,_/_/ /_/ /_/ .___/')
        print('                   Active Directory LDAP Enumerator          /_/ v1.0')
        print("                     Another Project by TheMayor \n" + self.close)

    def get_credentials(self):
        self.username = input(self.close + 'Enter your username (no domain): ')
        self.password = getpass('Enter your password: ')

    def anonymous_bind(self):
        try:
            dom_con = ipaddress.ip_address(input('\nDomain Controller IP: '))
            self.t1 = datetime.now()
            if sys.platform.startswith('win32'):
                print(
                    self.info + "\nLet's try to find a hostname for the domain controller..." + self.close)
                self.hostname = socket.gethostbyaddr(str(dom_con))[0]
                if self.hostname is not None:
                    print(
                        self.success + '\n[success] Target hostname is ' + self.hostname + '\n' + self.close)
                else:
                    print(
                        self.info + '[warn] Could not identify target hostname. Continuing...\n' + self.closee)
                    self.hostname = self.dom_con
            else:
                self.hostname = dom_con
        except (ipaddress.AddressValueError, socket.herror):
            print(
                self.info + "[error] Invalid IP Address or unable to contact host. Please try again." + self.close)
            self.anonymous_bind()
        except socket.timeout:
            print(
                self.info + "[error] Timeout while trying to contact the host. Please try again." + self.close)
            self.anonymous_bind()
        server = Server(str(dom_con), get_info=ALL)
        self.conn = Connection(server, auto_bind=True)
        with open(f"{self.hostname}.ldapdump.txt", 'w') as f:
            f.write(str(server.info))
        print(
            self.info + "[info] Let's try to identify a domain naming convention for the domain.\n" + self.close)
        with open(f"{self.hostname}.ldapdump.txt", 'r') as f:
            for line in f:
                if line.startswith("    DC="):
                    self.name_context = line.strip()
                    self.name_context = self.name_context.replace("DC=", "")
                    self.name_context = self.name_context.replace(",", ".")
                    print(
                        self.success + f"[success] Possible domain name found - {self.name_context}\n" + self.close)
                    break
        self.domain = self.name_context
        domain_contents = self.domain.split(".")
        self.domain = domain_contents[0]
        self.dom_1 = f"DC={domain_contents[0]},DC={domain_contents[1]}"
        print(
            self.info + f'[info] All set for now. Come back with credentials to dump additional domain information. Full raw output saved as {self.hostname}.ldapdump.txt\n' + self.close)
        self.t2 = datetime.now()
        total = self.t2 - self.t1
        total = str(total)
        print(self.info +
              f"LDAP enumeration completed in {total}.\n" + self.close)

    def authenticated_bind(self):
        try:
            self.dom_con = ipaddress.ip_address(
                input('\nDomain Controller IP: '))
            self.t1 = datetime.now()
            if sys.platform.startswith('win32'):
                print(
                    self.info + "\nLet's try to find a hostname for the domain controller..." + self.close)
                self.hostname = socket.gethostbyaddr(str(self.dom_con))[0]
                if self.hostname is not None:
                    print(
                        self.success + '\n[success] Target hostname is ' + self.hostname + '\n' + self.close)
                else:
                    print(
                        self.info + '[warn] Could not identify target hostname. Continuing...\n' + self.closee)
                    self.hostname = self.dom_con
            else:
                self.hostname = self.dom_con
        except (ipaddress.AddressValueError, socket.herror):
            print(
                self.info + "[error] Invalid IP Address or unable to contact host. Please try again." + self.close)
            self.authenticated_bind()
        except socket.timeout:
            print(
                self.info + "[error] Timeout while trying to contact the host. Please try again." + self.close)
            self.authenticated_bind()
        server = Server(str(self.dom_con), get_info=ALL)
        self.conn = Connection(server, auto_bind=True)
        with open(f"{self.hostname}.ldapdump.txt", 'w') as f:
            f.write(str(server.info))
        print(
            self.info + "[info] Let's try to identify a domain naming convention for the domain.\n" + self.close)
        with open(f"{self.hostname}.ldapdump.txt", 'r') as f:
            for line in f:
                if line.startswith("    DC="):
                    self.name_context = line.strip()
                    self.name_context = self.name_context.replace("DC=", "")
                    self.name_context = self.name_context.replace(",", ".")
                    print(
                        self.success + f"[success] Possible domain name found - {self.name_context}\n" + self.close)
                    break
        self.domain = self.name_context
        domain_contents = self.domain.split(".")
        self.domain = domain_contents[0]
        self.dom_1 = f"DC={domain_contents[0]},DC={domain_contents[1]}"
        server = Server(str(self.hostname), get_info=ALL)
        try:
            self.conn = Connection(
                server, user=f"{self.domain}\\{self.username}", password=self.password, auto_bind=True)
            self.conn.bind()
        except ldap3.core.exceptions.LDAPBindError:
            print(self.info + "Invalid credentials. Please try again." + self.close)
            self.get_credentials()
            self.authenticated_bind()
        print(self.success +
              f"[success] Connected to {self.hostname}.\n" + self.close)
        self.search_users(), self.search_groups(), self.kerberoast_accounts(), self.aspreproast_accounts(), self.unconstrained_search(), self.constrainted_search(
        ), self.computer_search(), self.ad_search(), self.mssql_search(), self.exchange_search(), self.gpo_search(), self.admin_count_search(), self.find_fields()

    def search_users(self):
        self.conn.search(
            f'{self.dom_1}', '(&(objectclass=person)(objectCategory=Person))', attributes=ldap3.ALL_ATTRIBUTES)
        entries_val = self.conn.entries
        print('\n' + '-'*38 + 'Users' + '-'*37 + '\n')
        entries_val = str(entries_val)
        if os.path.exists(f"{self.domain}.users.txt"):
            os.remove(f"{self.domain}.users.txt")
        with open(f"{self.domain}.users.txt", 'w') as f:
            f.write(entries_val)
            f.close
        with open(f"{self.domain}.users.txt", 'r+') as f:
            user_val = 0
            for line in f:
                if line.startswith('    sAMAccountName: '):
                    sam_name = line.strip()
                    sam_name = sam_name.replace('sAMAccountName: ', '')
                    print(sam_name)
                    user_val += 1
                    if user_val >= 25:
                        print(
                            f'\n[info] Truncating results at 25. Check {self.domain}.users.txt for full details.')
                        break
            f.close()

    def search_groups(self):
        # Query LDAP for groups
        self.conn.search(f'{self.dom_1}', '(objectclass=group)',
                         attributes=ldap3.ALL_ATTRIBUTES)
        entries_val = self.conn.entries
        print('\n' + '-'*37 + 'Groups' + '-'*37 + '\n')
        entries_val = str(entries_val)
        if os.path.exists(f"{self.domain}.groups.txt"):
            os.remove(f"{self.domain}.groups.txt")
        with open(f"{self.domain}.groups.txt", 'w') as f:
            f.write(entries_val)
            f.close
        with open(f"{self.domain}.groups.txt", 'r+') as f:
            group_val = 0
            for line in f:
                if line.startswith('    name: '):
                    group_name = line.strip()
                    group_name = group_name.replace('name: ', '')
                    print(group_name)
                    group_val += 1
                    if group_val >= 25:
                        print(
                            self.info + f'\n[info] Truncating results at 25. Check {self.domain}.groups.txt for full details.' + self.close)
                        break
            f.close()

        # Query LDAP for Kerberoastable users
    def kerberoast_accounts(self):
        self.conn.search(f'{self.dom_1}', '(&(&(servicePrincipalName=*)(UserAccountControl:1.2.840.113556.1.4.803:=512))(!(UserAccountControl:1.2.840.113556.1.4.803:=2)))',
                         attributes=ldap3.ALL_ATTRIBUTES)
        entries_val = self.conn.entries
        print('\n' + '-'*30 + 'Kerberoastable Users' + '-'*30 + '\n')
        entries_val = str(entries_val)
        if os.path.exists(f"{self.domain}.kerberoast.txt"):
            os.remove(f"{self.domain}.kerberoast.txt")
        with open(f"{self.domain}.kerberoast.txt", 'w') as f:
            f.write(entries_val)
            f.close()
        with open(f"{self.domain}.kerberoast.txt", 'r+') as f:
            kerb_val = 0
            for line in f:
                if line.startswith('    sAMAccountName: '):
                    kerb_name = line.strip()
                    kerb_name = kerb_name.replace('sAMAccountName: ', '')
                    print(kerb_name)
                    kerb_val += 1
                    if kerb_val >= 25:
                        print(
                            self.info + f'\n[info] Truncating results at 25. Check {self.domain}.users.txt for full details.' + self.close)
                        break
            f.close()

    def aspreproast_accounts(self):
        # Query LDAP for ASREPRoastable Users
        self.conn.search(f'{self.dom_1}', '(&(objectClass=user)(userAccountControl:1.2.840.113556.1.4.803:=4194304))', attributes=[
            'sAMAccountName'])
        entries_val = self.conn.entries
        print('\n' + '-'*30 + 'ASREPRoastable Users' + '-'*30 + '\n')
        entries_val = str(entries_val)
        if os.path.exists(f"{self.domain}.asreproast.txt"):
            os.remove(f"{self.domain}.asreproast.txt")
        with open(f"{self.domain}.asreproast.txt", 'w') as f:
            f.write(entries_val)
            f.close()
        with open(f"{self.domain}.asreproast.txt", 'r+') as f:
            asrep_val = 0
            for line in f:
                if line.startswith('    sAMAccountName: '):
                    asrep_name = line.strip()
                    asrep_name = asrep_name.replace('sAMAccountName: ', '')
                    print(asrep_name)
                    asrep_val += 1
                    if asrep_val >= 25:
                        print(
                            self.info + f'\n[info] Truncating results at 25. Check {self.domain}.users.txt for full details.' + self.close)
                        break
            f.close()

    def unconstrained_search(self):
        # Query LDAP for Unconstrained Delegation Rights
        self.conn.search(f'{self.dom_1}', "(&(userAccountControl:1.2.840.113556.1.4.803:=524288))",
                         attributes=ldap3.ALL_ATTRIBUTES)
        entries_val = self.conn.entries
        print('\n' + '-'*28 + 'Unconstrained Delegations' + '-'*27 + '\n')
        entries_val = str(entries_val)
        if os.path.exists(f"{self.domain}.unconstrained.txt"):
            os.remove(f"{self.domain}.unconstrained.txt")
        with open(f"{self.domain}.unconstrained.txt", 'w') as f:
            f.write(entries_val)
            f.close()
        with open(f"{self.domain}.unconstrained.txt", 'r+') as f:
            uncon_val = 0
            for line in f:
                if line.startswith('    sAMAccountName: '):
                    uncon_name = line.strip()
                    uncon_name = uncon_name.replace('sAMAccountName: ', '')
                    print(f'{uncon_name}')
                    uncon_val += 1
                    if uncon_val >= 25:
                        print(
                            self.info + f'\n[info] Truncating results at 25. Check {self.domain}.constrained.txt for full details.' + self.close)
                        break
            f.close()

    def constrainted_search(self):
        # Query LDAP for Constrained Delegation Rights
        self.conn.search(f'{self.dom_1}', "(msDS-AllowedToDelegateTo=*)",
                         attributes=ldap3.ALL_ATTRIBUTES)
        entries_val = self.conn.entries
        print('\n' + '-'*29 + 'Constrained Delegations' + '-'*28 + '\n')
        entries_val = str(entries_val)
        if os.path.exists(f"{self.domain}.constrained.txt"):
            os.remove(f"{self.domain}.constrained.txt")
        with open(f"{self.domain}.constrained.txt", 'w') as f:
            f.write(entries_val)
            f.close()
        with open(f"{self.domain}.constrained.txt", 'r+') as f:
            con_val = 0
            for line in f:
                if line.startswith('    cn: '):
                    constrained_name = line.strip()
                    constrained_name = constrained_name.replace('cn: ', '')
                if line.startswith('    msDS-AllowedToDelegateTo: '):
                    del_to = line.strip()
                    del_to = del_to.replace('msDS-AllowedToDelegateTo: ', '')
                    print(
                        f'{constrained_name} has constrained delegation rights to {del_to}')
                    con_val += 1
                    if con_val >= 25:
                        print(
                            self.info + f'\n[info] Truncating results at 25. Check {self.domain}.constrained.txt for full details.' + self.close)
                        break
            f.close()

    def computer_search(self):
        # Query LDAP for computer accounts
        self.conn.search(f'{self.dom_1}', '(&(objectClass=computer)(!(objectclass=msDS-ManagedServiceAccount)))',
                         attributes=ldap3.ALL_ATTRIBUTES)
        entries_val = self.conn.entries
        print('\n' + '-'*36 + 'Computers' + '-'*35 + '\n')
        entries_val = str(entries_val)
        if os.path.exists(f"{self.domain}.computers.txt"):
            os.remove(f"{self.domain}.computers.txt")
        with open(f"{self.domain}.computers.txt", 'a') as f:
            f.write(entries_val)
            f.close()
        with open(f"{self.domain}.computers.txt", 'r+') as f:
            comp_val = 0
            for line in f:
                if line.startswith('    sAMAccountName: '):
                    comp_name = line.strip()
                    comp_name = comp_name.replace('sAMAccountName: ', '')
                    comp_name = comp_name.replace('$', '')
                    print(comp_name)
                    comp_val += 1
                    if comp_val >= 25:
                        print(
                            self.info + f'\n[info] Truncating results at 25. Check {self.domain}.computers.txt for full details.' + self.close)
                        break
            f.close()
        if sys.platform.startswith('win32'):
            print(
                self.info + "\n[info] Let's try to resolve hostnames to IP addresses. This may take some time depending on the number of computers...\n" + self.close)
            with open(f"{self.domain}.computers.txt", 'r+') as f:
                comp_val1 = 0
                for line in f:
                    if line.startswith('    sAMAccountName: '):
                        comp_name = line.strip()
                        comp_name = comp_name.replace('sAMAccountName: ', '')
                        comp_name = comp_name.replace('$', '')
                        try:
                            comp_ip = socket.gethostbyname(comp_name)
                            if comp_ip:
                                print(f'{comp_name} - {comp_ip}')
                            else:
                                continue
                        except socket.gaierror:
                            pass
                        comp_val1 += 1
                        if comp_val1 >= 25:
                            print(
                                self.info + f'\n[info] Truncating results at 25. Check {self.domain}.computers.txt for full details.' + self.close)
                            break
                f.close()
        else:
            pass

    def ad_search(self):
        # Query LDAP for domain controllers
        self.conn.search(f'{self.dom_1}', '(&(objectCategory=Computer)(userAccountControl:1.2.840.113556.1.4.803:=8192))',
                         attributes=ldap3.ALL_ATTRIBUTES)
        entries_val = self.conn.entries
        print('\n' + '-'*31 + 'Domain Controllers' + '-'*31 + '\n')
        entries_val = str(entries_val)
        if os.path.exists(f"{self.domain}.domaincontrollers.txt"):
            os.remove(f"{self.domain}.domaincontrollers.txt")
        with open(f"{self.domain}.domaincontrollers.txt", 'a') as f:
            f.write(entries_val)
            f.close()
        with open(f"{self.domain}.domaincontrollers.txt", 'r+') as f:
            comp_val = 0
            for line in f:
                if line.startswith('    dNSHostName: '):
                    comp_name = line.strip()
                    comp_name = comp_name.replace('dNSHostName: ', '')
                    comp_name = comp_name.replace('$', '')
                    print(comp_name)
                    comp_val += 1
                    if comp_val >= 25:
                        print(
                            self.info + f'\n[info] Truncating results at 25. Check {self.domain}.computers.txt for full details.' + self.close)
                        break
            f.close()

    def mssql_search(self):
        # Query LDAP for MSSQL Servers
        self.conn.search(f'{self.dom_1}', '(&(objectCategory=Computer)(servicePrincipalName=MSSQLSvc*))',
                         attributes=ldap3.ALL_ATTRIBUTES)
        entries_val = self.conn.entries
        print('\n' + '-'*34 + 'MSSQL Servers' + '-'*33 + '\n')
        entries_val = str(entries_val)
        if os.path.exists(f"{self.domain}.mssqlservers.txt"):
            os.remove(f"{self.domain}.mssqlservers.txt")
        with open(f"{self.domain}.mssqlservers.txt", 'a') as f:
            f.write(entries_val)
            f.close()
        with open(f"{self.domain}.mssqlservers.txt", 'r+') as f:
            comp_val = 0
            for line in f:
                if line.startswith('    dNSHostName: '):
                    comp_name = line.strip()
                    comp_name = comp_name.replace('dNSHostName: ', '')
                    comp_name = comp_name.replace('$', '')
                    print(comp_name)
                    comp_val += 1
                    if comp_val >= 25:
                        print(
                            self.info + f'\n[info] Truncating results at 25. Check {self.domain}.computers.txt for full details.' + self.close)
                        break
            f.close()

    def exchange_search(self):
        # Query LDAP for Exchange Servers
        self.conn.search(f'{self.dom_1}', '(&(objectCategory=Computer)(servicePrincipalName=exchangeMDB*))',
                         attributes=ldap3.ALL_ATTRIBUTES)
        entries_val = self.conn.entries
        print('\n' + '-'*32 + 'Exchange Servers' + '-'*32 + '\n')
        entries_val = str(entries_val)
        if os.path.exists(f"{self.domain}.exchangeservers.txt"):
            os.remove(f"{self.domain}.exchangeservers.txt")
        with open(f"{self.domain}.exchangeservers.txt", 'a') as f:
            f.write(entries_val)
            f.close()
        with open(f"{self.domain}.exchangeservers.txt", 'r+') as f:
            comp_val = 0
            for line in f:
                if line.startswith('    sAMAccountName: '):
                    comp_name = line.strip()
                    comp_name = comp_name.replace('sAMAccountName: ', '')
                    comp_name = comp_name.replace('$', '')
                    print(comp_name)
                    comp_val += 1
                    if comp_val >= 25:
                        print(
                            self.info + f'\n[info] Truncating results at 25. Check {self.domain}.computers.txt for full details.' + self.close)
                        break
            f.close()

    def gpo_search(self):
        # Query LDAP for Group Policy Objects (GPO)
        self.conn.search(f'{self.dom_1}', '(objectclass=groupPolicyContainer)',
                         attributes=ldap3.ALL_ATTRIBUTES)
        entries_val = self.conn.entries
        print('\n' + '-'*30 + 'Group Policy Objects' + '-'*30 + '\n')
        entries_val = str(entries_val)
        if os.path.exists(f"{self.domain}.GPO.txt"):
            os.remove(f"{self.domain}.GPO.txt")
        with open(f"{self.domain}.GPO.txt", 'a') as f:
            f.write(entries_val)
            f.close()
        with open(f"{self.domain}.GPO.txt", 'r+') as f:
            gpo_val = 0
            for line in f:
                if line.startswith('    displayName: '):
                    gpo_name = line.strip()
                    gpo_name = gpo_name.replace('displayName: ', 'GPO Name: ')
                if line.startswith('    gPCFileSysPath: '):
                    gpcname = line.strip()
                    gpcname = gpcname.replace(
                        'gPCFileSysPath: ', 'GPO File Path: ')
                    print(f'{gpo_name}\n{gpcname}')
                    gpo_val += 1
                    if gpo_val >= 25:
                        print(
                            self.info + f'\n[info] Truncating results at 25 users. Check {self.domain}.constrained.txt for full details.' + self.close)
                        break
            f.close()

    def admin_count_search(self):
        # Query LDAP for users with adminCount=1
        self.conn.search(f'{self.dom_1}', '(&(!(memberof=Builtin))(adminCount=1)(objectclass=person)(objectCategory=Person))',
                         attributes=ldap3.ALL_ATTRIBUTES)
        entries_val = self.conn.entries
        print('\n' + '-'*30 + 'Protected Admin Users' + '-'*29 +
              '\nThese are user accounts with adminCount=1 set\n')
        entries_val = str(entries_val)
        if os.path.exists(f"{self.domain}.admincount.txt"):
            os.remove(f"{self.domain}.admincount.txt")
        with open(f"{self.domain}.admincount.txt", 'a') as f:
            f.write(entries_val)
            f.close()
        with open(f"{self.domain}.admincount.txt", 'r+') as f:
            gpo_val = 0
            for line in f:
                if line.startswith('    sAMAccountName: '):
                    admin_name = line.strip()
                    admin_name = admin_name.replace('sAMAccountName: ', '')
                    print(admin_name)
                    gpo_val += 1
                    if gpo_val >= 25:
                        print(
                            self.info + f'\n[info] Truncating results at 25 users. Check {self.domain}.admincount.txt for full details.' + self.close)
                        break
        f.close()
        self.conn.unbind()
        print(
            self.success + f'\n[success] Information dump completed. Text files containing raw data have been placed in this directory for your review.\n' + self.close)

    def find_fields(self):
        descript_info = []
        idx = 0
        print(
            self.info + '\n[info] Checking the output for information in description fields.\n' + self.close)
        with open(f'{self.domain}.users.txt', 'r') as refile:
            lines = refile.readlines()
            for line in lines:
                descriptions = "description:"
                if descriptions in line:
                    if "Built-in" in line or "Key Distribution Center Service Account" in line:
                        pass
                    else:
                        line = line.replace('description: ', '')
                        descript_info.insert(idx, line)
                        idx += 1
        refile.close()
        if len(descript_info) == 0:
            print(
                self.info + '[info] No information identified based on static parameters. Check the output file manually. Quitting...' + self.close)
            quit()
        else:
            lineLen = len(descript_info)
            print(
                self.success + '[success] Dumped the following information from object descriptions - Check text file for full details\n' + self.close)
            for i in range(lineLen):
                end = descript_info[i]
                print(self.info + f'{end}')
            # print()
            self.t2 = datetime.now()
            total = self.t2 - self.t1
            total = str(total)
            print(self.info +
                  f"LDAP enumeration completed in {total}.\n" + self.close)
            quit()

    def run(self):
        init()
        ldap_search.banner()
        try:
            choice = input(
                'Use credentials for binding? (Y/N): ').strip().upper()
            if choice == 'Y':
                self.get_credentials()
                self.authenticated_bind()
            elif choice == 'N':
                self.anonymous_bind()
            else:
                raise ValueError(self.info + '[error] Invalid choice\n')
        except ValueError as ve:
            print(ve)
            self.run()
        except KeyboardInterrupt:
            print(
                self.info + '\n[info] You either fat fingered this or something else. Either way, quitting...\n' + self.close)


ldap_search = LDAPSearch()
ldap_search.run()
