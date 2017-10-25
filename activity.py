#!/script/virtualenv/py3.6/bin/python
# -*-coding: utf-8 -*-

"""
Author          : Arijit Basu
Email           : sayanarijit@gmail.com
Documentation   : https://sayanarijit.github.io/activity
"""

# --------------------------- CONFIGURATION ---------------------------

DBHOST = "localhost"                                # Databse hosted on
DBUSER = "root"                                     # Database user
DBPASSWORD = ""                                     # Database password
SUDO = True                                         # Whether to use "sudo ssh hostname" or just "ssh hostname"
USERNAME = "root"                                   # Remote login user
PASSWORD = "dummy"                                  # Remote login password *Should not be blank*
SSH_KEY = "/root/.ssh/id_rsa"                       # Private key for passwordless ssh auth *Should not be blank*
EXTRA_OPTIONS = ["-o", "StrictHostKeyChecking=no"]  # Applies to both ssh and scp
TIMEOUT = 120                                       # Applies to both ssh, scp
PARALLEL_LIMIT = 200                                # Maximum number of parallel workers allowed per activity
WEBLINK = "http://localhost/activity"               # If mentioned, it will be visible in interactive mode

# ---------------------------------------------------------------------

import sys
import os
import shutil
from concurrent.futures import ThreadPoolExecutor, as_completed
import getpass
from tqdm import tqdm
from subprocess import Popen, PIPE
import argparse
import socket
import json
import textwrap
import datetime
import re
from shlex import quote
from tabulate import tabulate
from termcolor import colored
import colorama
from dictmysql import DictMySQL, cursors
colorama.init()


# Define functions to be used by multiprocessing

def _ping_single(args):
    host, user, reportid = args
    action = "ping_check"
    cmd = ["ping", "-c1", "-w5", host]
    proc = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=False)
    outs, errs = proc.communicate()
    outs, errs = outs.decode("utf-8"), errs.decode("utf-8")
    exit_code = proc.returncode
    result = dict(user=user, reportid=reportid, action=action, hostname=host,
                  command=" ".join(cmd), stdout=outs, stderr=errs, exit_code=exit_code)
    return result

def _exec_single(args):
    host, user, reportid, action, command = args
    command = "/bin/sh -c "+quote(command)
    cmd = ["sshpass", "-p", PASSWORD]
    if SUDO:
        cmd += ["sudo","-n","--"]
    cmd += ["ssh","-q","-l",USERNAME,"-i",SSH_KEY] + EXTRA_OPTIONS + [host, command]

    proc = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=False)
    try:
        outs, errs = proc.communicate(timeout=TIMEOUT)
        outs, errs = outs.decode("utf-8"), errs.decode("utf-8")
        exit_code = proc.returncode
    except:
        proc.kill()
        outs, errs = "", "ssh: failed to connect"
        exit_code = 1
    finally:
        result = dict(user=user, reportid=reportid, action=action, hostname=host,
                      command=command, stdout=outs, stderr=errs, exit_code=exit_code)
        return result

def _console_check_single(args):
    host, user, reportid = args
    action = "console_check"
    cons = ["ilo", "con", "imm", "ilom", "alom", "xscf", "power"]
    action = "console_check"
    available = []
    exit_code = 1
    for con in cons:
        cmd = ["ping", "-c1", "-w5", host+"-"+con]
        proc = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=False)
        proc.communicate()
        if proc.returncode == 0:
            exit_code = 0
            available.append(host+"-"+con)
    result = dict(user=user, reportid=reportid, action=action, hostname=host,
                  command=json.dumps(cons), stdout=json.dumps(available), stderr="", exit_code=exit_code)
    return result

def _port_scan_single(args):
    host, user, reportid, port = args
    action = "port_scan: " + str(port)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(TIMEOUT)
    try:
        exit_code = sock.connect_ex((host, port))
        sock.settimeout(None)
    except:
        exit_code = 1
    finally:
        sock.settimeout(None)
        sock.close()
        result = dict(user=user, reportid=reportid, action=action,
                      hostname=host, command=port, exit_code=exit_code)
        return result

def _scp_single(args):
    host, user, reportid, localpath, remotepath = args
    action = "scp: '"+localpath+"' -> '"+remotepath+"'"
    cmd = ["sshpass", "-p", PASSWORD]
    if SUDO:
        cmd += ["sudo"]
    cmd += ["scp","-i",SSH_KEY] + EXTRA_OPTIONS
    cmd += ["-pr", localpath, USERNAME+"@"+host+":"+remotepath]
    outs, errs, exit_code = "", "", 1
    proc = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=False)
    try:
        outs, errs = proc.communicate(timeout=TIMEOUT)
        outs, errs = outs.decode("utf-8"), errs.decode("utf-8")
        exit_code = proc.returncode
    except:
        proc.kill()
        outs, errs = "", "scp: failed to connect"
        exit_code = 1
    finally:
        result = dict(user=user, reportid=reportid, action=action, hostname=host,
                      command=" ".join(cmd).replace(PASSWORD,"***"),
                      stdout=outs, stderr=errs, exit_code=exit_code)
        return result

class Activity:

    def __init__(self, hosts=[], reportid=None, sudo=SUDO, username=USERNAME, password=PASSWORD,
                 ssh_key=SSH_KEY, dbhost=DBHOST, dbuser=DBUSER, dbpassword=DBPASSWORD,
                 extra_options=EXTRA_OPTIONS, timeout=TIMEOUT, process_limit=PARALLEL_LIMIT):

        try:
            self.db = DictMySQL(db='activity', host=dbhost, user=dbuser, passwd=dbpassword, cursorclass=cursors.DictCursor)
        except:
            print("ERROR: failed to connect with database `{db}` with user `{dbuser}`@`{dbhost}`".format(
                dbhost=dbhost, db="activity", dbuser=dbuser
            ), file=sys.stderr)
            exit()

        if not reportid:
            self.reportid = datetime.datetime.now().strftime("%d%B%y-%Hh%Mm%Ss")
        else:
            self.reportid = re.sub("[^a-zA-Z0-9-]","_",reportid).lower()
        try:
            self.user = os.getlogin()
        except:
            self.user = "web"
        self.sudo = sudo
        self.username = username
        self.password = password
        self.ssh_key = ssh_key
        self.extra_options = extra_options
        self.timeout = timeout
        self.process_limit = process_limit
        self.seperator = "[---x---]"  # Separates command outputs
        self.prereq_check() # Check if requirements are met
        self.createtables()

        if self.reportid in self.list():
            self.report = self.db.select(table="reports",
                                         columns="*",
                                         where={"user":self.user, "reportid":self.reportid})
            self.hosts = [f["hostname"] for f in self.report if f["action"] == "ping_check"]
            self.up_hosts = [f["hostname"] for f in self.report if f["action"] == "ping_check" and f["exit_code"] == 0]
            self.down_hosts = list(set(self.hosts) - set(self.up_hosts))
            self.reachable_hosts = [f["hostname"] for f in self.report if f["action"] == "os_check" and f["stdout"] != ""]
            self.unreachable_hosts = [f["hostname"] for f in self.report if f["action"] == "os_check" and f["stdout"] == ""]
        else:
            self.hosts = list(set([h.strip().lower() for h in hosts if h.strip() and len(h.split()) == 1]))
            self.ping_check()

    def prereq_check(self):
        req_tools = ["sudo", "ping", "ssh", "scp", "sshpass"]
        for tool in req_tools[:]:
            if shutil.which(tool) is not None:
                req_tools.remove(tool)
        if len(req_tools) > 0:
            print("ERROR: Following commands not found in system path: "+(", ".join(req_tools)))
            quit()

    def createtables(self):
        if "reports" in [f["table_name"] for f in self.db.table_name()]:
            return False
        sql = """\
            CREATE TABLE IF NOT EXISTS `reports` (
              `id` int(200) UNSIGNED AUTO_INCREMENT PRIMARY KEY,
              `user` varchar(50) NOT NULL,
              `reportid` varchar(50) NOT NULL,
              `action` varchar(200) NOT NULL,
              `hostname` varchar(50) NOT NULL,
              `command` longtext NOT NULL,
              `stdout` longtext,
              `stderr` longtext,
              `exit_code` int(5) NOT NULL
            ) ENGINE=InnoDB DEFAULT CHARSET=latin1;"""
        self.db.query(sql)
        return True

    def list(self):
        return list(set([f["reportid"] for f in self.db.select(table="reports",
                                                          columns=["reportid"],
                                                          where={"user": self.user})]))

    def reload(self):
        self.db.reconnect()
        self.report = self.hosts = self.up_hosts = self.down_hosts = self.reachable_hosts = self.unreachable_hosts = []
        if self.reportid in self.list():
            self.report = self.db.select(table="reports",
                                         columns="*",
                                         where={"user": self.user, "reportid": self.reportid})
            self.hosts = [f["hostname"] for f in self.report if f["action"] == "ping_check"]
            self.up_hosts = [f["hostname"] for f in self.report if f["action"] == "ping_check" and f["exit_code"] == 0]
            self.down_hosts = list(set(self.hosts) - set(self.up_hosts))
            self.reachable_hosts = [f["hostname"] for f in self.report if f["action"] == "os_check" and f["stdout"] != ""]
            self.unreachable_hosts = [f["hostname"] for f in self.report if f["action"] == "os_check" and f["stdout"] == ""]
        return True

    def clean(self):
        if self.reportid not in self.list():
            return False
        self.db.delete(table="reports",where={"user":self.user,"reportid":self.reportid})
        self.report = self.up_hosts = self.down_hosts = self.reachable_hosts = self.unreachable_hosts = []
        self.reload()
        return True

    def rename(self, new_id):
        new_id = re.sub("[^a-zA-Z0-9-]","_",new_id)
        if not new_id or new_id == "" or new_id in self.list():
            return False
        self.db.update(table="reports",value={"reportid": new_id},where={"user":self.user, "reportid": self.reportid})
        self.reportid = new_id
        self.reload()
        return True

    def ping_check(self):
        if len(self.hosts) == 0: return []
        output = []
        self.db.delete(table="reports",where={"user": self.user,
                                              "reportid": self.reportid,
                                              "action": "ping_check"})
        with ThreadPoolExecutor(max_workers=PARALLEL_LIMIT) as pool:
            futures = [pool.submit(_ping_single, [h,self.user,self.reportid]) for h in self.hosts]
            for f in tqdm(as_completed(futures), desc='Pinging hosts', leave=True,
                          ascii=True, mininterval=0.5, miniters=1, total=len(self.hosts)):
                self.db.insert(table="reports", value=f.result())
                output.append(f.result())
        self.reload()
        return output

    def console_check(self):
        if len(self.hosts) == 0: return []
        output = []
        self.db.delete(table="reports",where={"user": self.user,
                                              "reportid": self.reportid,
                                              "action": "console_check"})
        with ThreadPoolExecutor(max_workers=PARALLEL_LIMIT) as pool:
            output = []
            futures = [pool.submit(_console_check_single, [h,self.user,self.reportid]) for h in self.hosts]
            for f in tqdm(as_completed(futures), desc='Pinging consoles', leave=True,
                          ascii=True, mininterval=0.5, miniters=1, total=len(self.hosts)):
                self.db.insert(table="reports", value=f.result())
                output.append(f.result())
        self.reload()
        return output

    def execute(self, hosts, command, action="execute"):
        if len(hosts) == 0: return []
        output = []
        if isinstance(command, list): command = ";".join(command)
        if action == "os_check":
            desc = "SSH/OS check"
        else:
            desc = "Executing remote command"
        if not action.startswith("execute: "):
            self.db.delete(table="reports",where={"user": self.user,
                                                  "reportid": self.reportid,
                                                  "action": action})
        with ThreadPoolExecutor(max_workers=PARALLEL_LIMIT) as pool:
            output = []
            futures = [pool.submit(_exec_single, [h,self.user,self.reportid,action,command]) for h in hosts]
            for f in tqdm(as_completed(futures), desc=desc, leave=True,
                          ascii=True, mininterval=0.5, miniters=1, total=len(hosts)):
                self.db.insert(table="reports", value=f.result())
                output.append(f.result())
        self.reload()
        return output

    def os_check(self):
        if self.up_hosts == None or len(self.up_hosts) == 0: self.ping_check()
        if self.up_hosts == None or len(self.up_hosts) == 0: return []
        action = "os_check"
        command = "uname -srm; python -c 'import platform; print(\" \".join(platform.dist()));'"
        output = self.execute(hosts=self.up_hosts, command=command, action=action)
        return output

    def ssh_check(self):
        if self.reachable_hosts == None or len(self.reachable_hosts) == 0:
            self.os_check()

    def scp(self, localpath, remotepath="~/"):
        self.ssh_check()
        output = []
        action = "scp: '"+localpath+"' -> '"+remotepath+"'"
        self.db.delete(table="reports",
                       where={"user":self.user,"reportid":self.reportid,"action": action})

        with ThreadPoolExecutor(max_workers=PARALLEL_LIMIT) as pool:
            output = []
            futures = [pool.submit(_scp_single, [h, self.user, self.reportid, localpath, remotepath])
                       for h in self.reachable_hosts]
            for f in tqdm(as_completed(futures), desc='Copying over scp', leave=True,
                          ascii=True, mininterval=0.5, miniters=1, total=len(self.reachable_hosts)):
                self.db.insert(table="reports", value=f.result())
                output.append(f.result())
        self.reload()
        return output

    def dump_config(self):
        self.ssh_check()
        commands = [
            "uname -a", "cat /etc/*release", "uptime", "ifconfig -a", "netstat -nr",
            "cat /etc/fstab", "cat /etc/vfstab", "cat /etc/mtab", "cat /etc/network/interfaces",
            "cat /etc/sysconfig/network", "cat /etc/nsswitch.conf", "cat /etc/yp.conf",
            "cat /etc/ssh/sshd_config", "cat /etc/puppet.conf", "cat /etc/sudoers",
            "cat /etc/sudoers.d/*", "cat /usr/local/etc/sudoers", "cat /usr/local/etc/sudoers.d/*"
        ]
        action = "dump_config"
        command = (";echo "+self.seperator+";").join(commands)
        output = self.execute(hosts=self.reachable_hosts,command=command,action=action)
        return output

    def id_and_homedir_check(self, users):
        self.ssh_check()
        output = []
        for user in users:
            action = "id_and_homedir_check: "+ user
            command = "date && id "+user+" && su - "+user+" -c 'cd ~ && pwd && touch test && ls -l test'"
            output += self.execute(hosts=self.reachable_hosts, command=command, action=action)
        return output

    def mount_check(self, mounts):
        self.ssh_check()
        output = []
        for mount in mounts:
            action = "mount_check: " + mount
            command = "date && df -Pl "+mount+" && cd "+mount+" && pwd && touch test && ls -l test"
            output += self.execute(hosts=self.reachable_hosts, command=command, action=action)
        return output

    def port_scan(self, ports):
        if len(self.up_hosts) == 0: return []
        output = []
        for port in ports:
            action = "port_scan: "+ str(port)
            self.db.delete(table="reports",where={"user": self.user,
                                                  "reportid": self.reportid,
                                                  "action": action})
            with ThreadPoolExecutor(max_workers=PARALLEL_LIMIT) as pool:
                output = []
                futures = [pool.submit(_port_scan_single, [h,self.user,self.reportid,port])
                           for h in self.up_hosts]
                for f in tqdm(as_completed(futures), desc='Scanning port '+str(port), leave=True,
                              ascii=True, mininterval=0.5, miniters=1, total=len(self.up_hosts)):
                    self.db.insert(table="reports", value=f.result())
                    output.append(f.result())
        self.reload()
        return output


class Activity_Interactive(Activity):
    def __init__(self):
        Activity.__init__(self)

    def confirm(self,prompt="Are you sure?"):
        try:
            ans = input(prompt+" [y/N]: ").strip().lower()
            print()
        except:
            return False
        if ans in ["y","yes"]:
            return True
        return False

    def display_menu(self):
        rows, cols = map(int,os.popen('stty size', 'r').read().split())
        os.system("clear")

        self.activities = {
            "os_check": "Perform OS check of all available hosts",
            "console_check": "List available management consoles of physical servers",
            "id_and_homedir_check": "Check if specified IDs and home directories exists on ssh reachable hosts",
            "dump_config": "Fetch current configuration of ssh reachable hosts",
            "mount_check": "Check if specified directories are mounted properly and if in read-only state",
            "port_scan": "Perform port scan on pingable hosts",
            "scp": "Copy file/directory to ssh reachable hosts over ssh",
            "execute": "Execute commands on ssh reachable hosts."
        }
        self.choices = {
            "new": "Start a fresh activity",
            "open": "Open an existing report",
            "rename": "Rename current report ID to a new ID",
            "clean": "Clean current report",
            "help": "Print help menu",
            "exit": "Exit this menu"
        }
        self.menu = {}
        self.stats = {}
        try:
            self.display
        except:
            self.display = None

        def x(val, stats=None):
            self.menu.update({str(len(self.menu)+1) : val})
            if stats:
                self.stats.update({str(len(self.menu)): stats})
            return len(self.menu)

        if len(self.list()) == 0:
            del self.choices["open"]

        if self.reportid not in self.list():
            del self.choices["rename"]
            del self.choices["clean"]

        if self.reportid in self.list() and len(self.reachable_hosts) > 0:
            try:
                del self.activities["os_check"]
            except:
                pass

        if len(self.hosts) == 0:
            self.activities = {}
        self.help_menu = self.activities.copy()
        self.help_menu.update(self.choices)

        tabs = [(colored(" "+t+" ","white","on_blue") if t == self.reportid else " "+t+" ") for t in self.list()]
        if len(tabs) > 0:
            if self.reportid not in self.list():
                print(textwrap.fill("|".join(tabs).center(cols),cols))
            else:
                print(textwrap.fill("|".join(tabs).center(cols+14),cols))
            print("="*cols)
        print(textwrap.fill(" | ".join(self.choices).center(cols),cols))
        print("-"*cols)

        if len(self.hosts) > 0:
            if WEBLINK: print((WEBLINK+"/"+self.user+"/"+self.reportid).center(cols))
            # Ping check
            print(x("Ping check stats"),"Ping check stats")
            if self.display == "Ping check stats":
                p = []
                p.append([x("All hosts",self.hosts),".  All hosts:",str(len(self.hosts))])
                p.append([])
                p.append([x("Pingable hosts",self.up_hosts),".    Pingable hosts:",str(len(self.up_hosts))])
                p.append([x("Unavailable hosts",self.down_hosts),".    Unavailable hosts:",str(len(self.down_hosts))])
                print(tabulate(p))

            # SSH check
            if len(self.reachable_hosts) > 0 or len(self.unreachable_hosts) > 0:
                print(x("SSH check stats"),"SSH check stats")
                if self.display == "SSH check stats":
                    p = []
                    p.append([x("Pingable hosts",self.up_hosts),".  Pingable hosts:",str(len(self.up_hosts))])
                    p.append([])
                    p.append([x("SSH reachhable hosts",self.reachable_hosts),".    SSH reachhable hosts:",str(len(self.reachable_hosts))])
                    p.append([x("SSH unreachhable hosts",self.unreachable_hosts),".    SSH unreachhable hosts:",str(len(self.unreachable_hosts))])
                    print(tabulate(p))

            # OS check
            if len(self.reachable_hosts) > 0:
                print(x("OS check stats"),"OS check stats")
                if self.display == "OS check stats":
                    osreport =[]
                    for op in [r for r in self.report if r["action"] == "os_check"]:
                        hostname = op["hostname"]
                        if op["stdout"] != "" and len(op["stdout"].split()) > 1:
                            osname, kernel_release, arch = op["stdout"].split()[0:3]
                            if osname == "Linux" and len(op["stdout"].splitlines()) > 1:
                                dist = op["stdout"].splitlines()[1]
                            else:
                                dist = op["stdout"].split()[1]
                            osreport.append(dict(hostname=hostname,os=osname,kernel_release=kernel_release,
                                                arch=arch,dist=dist))
                        else:
                            osreport.append(dict(hostname=hostname,os="N/A",kernel="N/A",kernel_release="N/A",
                                                arch="N/A",dist="N/A"))

                    p = []
                    p.append([x("SSH reachable hosts",self.reachable_hosts),".  SSH reachable hosts:",str(len(self.reachable_hosts))])
                    kernels = set([o["os"] for o in osreport if o["hostname"] in self.reachable_hosts])
                    i = 0
                    for k in kernels:
                        i += 1
                        dists = set([d["dist"]+" "+("(64 bit)" if d["arch"][-2:]=="64" else "(32 bit)") for d in osreport if d["os"] == k])
                        dhosts = [d["hostname"] for d in osreport if d["os"] == k]
                        p.append([])
                        p.append([x(k,dhosts),".    "+k+":",str(len(dhosts))])
                        j = 0
                        for d in dists:
                            j += 1
                            ohosts = [o["hostname"] for o in osreport if o["os"] == k and o["dist"]+" "+("(64 bit)" if o["arch"][-2:]=="64" else "(32 bit)") == d]
                            p.append([x(d,ohosts),".      "+d+":",str(len(ohosts))])
                    print(tabulate(p))

            # Console check
            console_check_report = [r for r in self.report if r["action"] == "console_check"]
            if len(console_check_report) > 0:
                del self.activities["console_check"]
                print(x("Console check stats"),"Console check stats")
                if self.display == "Console check stats":
                    found = [c["hostname"] for c in console_check_report if c["exit_code"] == 0]
                    p = []
                    p.append([x("All hosts",self.hosts),".  All hosts:", len(self.hosts)])
                    p.append([])
                    p.append([x("Console found",found),".    Console found:",len(found)])
                    p.append([x("Console not found",list(set(self.hosts)-set(found))),".    Console not found:",(len(self.hosts)-len(found))])
                    print(tabulate(p))

            # ID and homedir check
            if len(self.reachable_hosts) > 0:
                id_check_report = [r for r in self.report if r["action"].split()[0] == "id_and_homedir_check:"]
                if len(id_check_report) > 0:
                    print(x("ID and home directory check stats"),"ID and home directory check stats")
                    if self.display == "ID and home directory check stats":
                        p = []
                        p.append([x("SSH reachable hosts",self.reachable_hosts),".  SSH reachable hosts:",str(len(self.reachable_hosts))])
                        ids = set([r["command"].split()[5] for r in id_check_report])
                        for idx in ids:
                            this_id_report = [r for r in id_check_report if r["command"].split()[3] == idx]
                            id_present = [r["hostname"] for r in this_id_report if len(r["stdout"].splitlines()) > 1]
                            home_present = [r["hostname"] for r in this_id_report if len(r["stdout"].splitlines()) > 2]
                            has_permission = [r["hostname"] for r in this_id_report if len(r["stdout"].splitlines()) > 3]
                            p.append([])
                            p.append([x("ID '"+idx+"' present",id_present),".    ID '"+idx+"' present:",str(len(id_present))])
                            p.append([x("Home directory present",home_present),".      Home directory present:",str(len(home_present))])
                            p.append([x("Has write permission",has_permission),".        Has write permission:",str(len(has_permission))])
                            p.append([x("No write permission",list(set(home_present)-set(has_permission))),".        No write permission:",str((len(home_present)-len(has_permission)))])
                            p.append([x("Home directory missing",list(set(id_present)-set(home_present))),".      Home directory missing:",str((len(id_present)-len(home_present)))])
                            p.append([x("ID '"+idx+"' missing",list(set(self.reachable_hosts)-set(id_present))),".    ID '"+idx+"' missing:",str((len(this_id_report)-len(id_present)))])
                        print(tabulate(p))

            # Dumped configuration report
            if len(self.reachable_hosts) > 0:
                dumped = {}
                [dumped.update({r["hostname"]:r["stdout"]}) for r in self.report if r["action"] == "dump_config" and r["stdout"] != ""]
                if len(dumped) > 0:
                    del self.activities["dump_config"]
                    print(x("Dumped configuration report",dumped),"Dumped configuration report")

            # Mount check stats
            if len(self.reachable_hosts) > 0:
                mount_check_report = [r for r in self.report if r["action"].split()[0] == "mount_check:"]
                if len(mount_check_report) > 0:
                    print(x("Mount check stats"),"Mount check stats")
                    if self.display == "Mount check stats":
                        p = []
                        p.append([x("SSH reachable hosts",self.reachable_hosts),".  SSH reachable hosts:",str(len(self.reachable_hosts))])
                        mounts = set([r["action"].split()[1] for r in mount_check_report])
                        for m in mounts:
                            this_mount_report = [r for r in mount_check_report if r["action"].split()[1] == m]
                            mounted = [r["hostname"] for r in this_mount_report if len(r["stdout"].splitlines()) > 3]
                            notmounted = [r["hostname"] for r in this_mount_report if len(r["stdout"].splitlines()) < 4]
                            readonly = [r["hostname"] for r in this_mount_report if len(r["stdout"].splitlines()) < 5]
                            diskhigh = [r["hostname"] for r in this_mount_report if len(r["stdout"].splitlines()) > 2 and int(r["stdout"].splitlines()[2].split()[4].replace("%","")) > 90]
                            p.append([])
                            p.append([x("'"+m+"' mounted",mounted),".    '"+m+"' mounted:",str(len(mounted))])
                            p.append([x("Read-only mount",readonly),".      Read-only mount:",str(len(readonly))])
                            p.append([x("High disk usage (>90%)",diskhigh),".      High disk usage (>90%):",str(len(diskhigh))])
                            p.append([x("'"+m+"' not mounted",notmounted),".    '"+m+"' not mounted:",str(len(notmounted))])
                        print(tabulate(p))

            # Port scan stats
            if len(self.up_hosts) > 0:
                port_scan_report = [r for r in self.report if r["action"].split()[0] == "port_scan:"]
                if len(port_scan_report) > 0:
                    print(x("Port scan stats"),"Port scan stats")
                    if self.display == "Port scan stats":
                        p = []
                        p.append([x("Pingable hosts",self.up_hosts),".  Pingable hosts:",str(len(self.up_hosts))])
                        ports = [r["command"] for r in port_scan_report]
                        for port in set(ports):
                            this_port_report = [r for r in port_scan_report if port == r["command"]]
                            p_open = [r["hostname"] for r in this_port_report if r["exit_code"] == 0]
                            p_closed = list(set(self.up_hosts)-set(p_open))
                            p.append([])
                            p.append([x("Port '"+str(port)+"' open",p_open),".    Port '"+str(port)+"' open:",str(len(p_open))])
                            p.append([x("Port '"+str(port)+"' closed",p_closed),".    Port '"+str(port)+"' closed:",str(len(p_closed))])
                        print(tabulate(p))

            # SCP stats
            if len(self.reachable_hosts) > 0:
                scp_report = [r for r in self.report if r["action"].split()[0] == "scp:"]
                if len(scp_report) > 0:
                    print(x("SCP stats"),"SCP stats")
                    if self.display == "SCP stats":
                        p = []
                        p.append([x("SSH reachable hosts",self.reachable_hosts),".  SSH reachable hosts:",str(len(self.reachable_hosts))])
                        commands = set([r["action"].split(": ")[1] for r in scp_report])
                        for c in commands:
                            this_command_report = [r for r in scp_report if r["action"].split(": ")[1] == c]
                            success = [r["hostname"] for r in this_command_report if r["exit_code"] == 0]
                            failed = list(set(self.reachable_hosts)-set(success))
                            p.append([])
                            p.append([x(c+" successful",success),".    "+c+" successful:",str(len(success))])
                            p.append([x(c+" failed",failed),".    "+c+" failed:",str(len(failed))])
                        print(tabulate(p))

            # Execute command stats
            if len(self.reachable_hosts) > 0:
                execute_command_report = [r for r in self.report if r["action"].split()[0] == "execute:"]
                if len(execute_command_report) > 0:
                    print(x("Execute command stats"),"Execute command stats")
                    if self.display == "Execute command stats":
                        p = []
                        p.append([x("SSH reachable hosts",self.reachable_hosts),".  SSH reachable hosts:",str(len(self.reachable_hosts))])
                        commands = set([r["action"].replace("execute: ", "") for r in execute_command_report])
                        for c in commands:
                            this_command_report = [r for r in execute_command_report if r["action"].replace("execute: ", "") == c]
                            success = [r["hostname"] for r in this_command_report if r["exit_code"] == 0]
                            failed = list(set(self.reachable_hosts)-set(success))
                            stdout = {(r["hostname"]+" ("+r["command"]+")"):r["stdout"] for r in this_command_report if r["stdout"] != ""}
                            stderr = {(r["hostname"]+" ("+r["command"]+")"):r["stderr"] for r in this_command_report if r["stderr"] != ""}
                            p.append([])
                            p.append([x("Command for '"+c+"' successful",success),".    Command for '"+c+"' successful:",str(len(success))])
                            p.append([x("Command for '"+c+"' failed",failed),".    Command for '"+c+"' failed:",str(len(failed))])
                            p.append([x("Stdout for '"+c+"'",stdout),".    Stdout for '"+c+"':",str(len(stdout))])
                            p.append([x("Stderr for '"+c+"'",stderr),".    Stderr for '"+c+"':",str(len(stderr))])
                        print(tabulate(p))

            # ------------------------------------------------------------------
            print("-"*cols)
            print(textwrap.fill(" | ".join(self.activities).center(cols),cols))
            print("-"*cols)

        else:
            print()
            print("Enter 'new' to start a new activity".center(cols))
            print()
            if len(self.list()) > 0:
                print("Enter 'open' to open an existing activity report".center(cols))
                print()
            print("Enter 'help' to see a list of options".center(cols))
            print()
            print("-"*cols)

    def get_arg(self,prompt="Enter text",args=[],confirm=None):
        if len(args) >1:
            if confirm:
                if self.confirm(confirm):
                    arg = args[1]
                else:
                    arg = None
            else:
                arg = args[1]
        else:
            try:
                arg = input(prompt+" [keep blank to cancel]: ")
                print()
            except:
                arg = None
        return arg

    def interact(self):
        while True:
            self.reload()
            self.display_menu()
            rows, cols = map(int,os.popen('stty size', 'r').read().split())

            try:
                inp = input("> ").strip().lower().split()
            except:
                print()
                exit()
            if not inp:
                self.display = None
                continue
            print()

            if inp[0] not in [k for k,v in self.help_menu.items()] and inp[0] not in [k for k,v in self.menu.items()]:
                print("Available options are:\n\n\t"+"\n\t".join([k for k,v in self.help_menu.items()]))

            if inp[0] in [k for k,v in self.menu.items()]:
                if inp[0] in self.stats.keys():
                    if isinstance(self.stats[inp[0]],list):
                        print("\n".join(self.stats[inp[0]]))
                    else:
                        for k,v in self.stats[inp[0]].items():
                            print("="*cols)
                            print(k.center(cols))
                            print("-"*cols)
                            print(v)
                else:
                    self.display = self.menu[inp[0]]
                    continue

            if inp[0] == "exit":
                exit()

            if inp[0] == "clean":
                if self.confirm("Are you sure you want to drop this report?"):
                    if self.clean():
                        print("SUCCESS: Dropped report ID '"+self.reportid+"' from database")
                    else:
                        print("SKIPPED: It seems there seems is nothing to clean")

            if inp[0] == "rename":
                new = self.get_arg(prompt="Enter new ID",confirm="Are you sure you want to rename this report ID?", args=inp)
                new = re.sub("[^a-zA-Z0-9-]","_",new).lower()
                if new and self.rename(new):
                    print("SUCCESS: New report ID is: ",self.reportid)
                else:
                    print("SKIPPED: Report ID is unchanged. You can try another ID")

            if inp[0] == "open":
                if len(self.list()) == 0:
                    print("SKIPPED: There is nothing to open")
                else:
                    prompt = "List of reports generated by you:\n\n\t"+"\n\t".join(self.list())+"\n\n"
                    prompt += "Enter report ID to open:"
                    new = self.get_arg(prompt=prompt,args=inp)
                    new = re.sub("[^a-zA-Z0-9-]","_",new).lower()
                    if new and new in self.list():
                        self.reportid = new
                        self.reload()
                        continue
                    else:
                        print("SKIPPED: report ID '"+new+"' not found in DB")

            if inp[0] == "new":
                new = self.get_arg(prompt="Enter fresh report ID:",args=inp)
                new = re.sub("[^a-zA-Z0-9-]","_",new).lower()
                if new and new in self.list():
                    print("SKIPPED: report ID already exists. Try another ID")
                elif new:
                    self.reportid = new
                    self.reload()
                    hosts = []
                    print("Paste hostnames and enter 'DONE'")
                    print("--------------------------------")
                    while True:
                        try:
                            host = input()
                            if host == "DONE":
                                break
                            if host and host != "" and len(host.split()) == 1 and host not in hosts:
                                hosts.append(host)
                        except:
                            pass
                    self.hosts = [h.strip().lower() for h in set(hosts)]
                    self.ping_check()
                else:
                    print("SKIPPED: No fresh activity is created")

            if inp[0] == "os_check":
                if len(self.up_hosts) == 0:
                    getpass.getpass("No accessible host found.\n\n[Press ENTER to continue]")
                    continue
                self.os_check()

            if inp[0] == "console_check":
                self.console_check()

            if inp[0] == "dump_config":
                self.ssh_check()
                if len(self.reachable_hosts) == 0:
                    getpass.getpass("No accessible host found.\n\n[Press ENTER to continue]")
                    continue
                self.dump_config()

            if inp[0] == "id_and_homedir_check":
                self.ssh_check()
                if len(self.reachable_hosts) == 0:
                    getpass.getpass("No accessible host found.\n\n[Press ENTER to continue]")
                    continue
                try:
                    ids = list(set(input("Enter space separated usernames: ").strip().split()))
                    if len(ids) > 0:
                        self.id_and_homedir_check(users=ids)
                except:
                    print("SKIPPED: Invalid input")

            if inp[0] == "mount_check":
                self.ssh_check()
                if len(self.reachable_hosts) == 0:
                    getpass.getpass("No accessible host found.\n\n[Press ENTER to continue]")
                    continue
                try:
                    mounts = list(set(input("Enter space separated mount paths: ").strip().split()))
                    if len(mounts) > 0:
                        self.mount_check(mounts=mounts)
                except:
                    print("SKIPPED: Invalid input")

            if inp[0] == "port_scan":
                if len(self.up_hosts) == 0:
                    getpass.getpass("No accessible host found.\n\n[Press ENTER to continue]")
                    continue
                try:
                    ports = [int(p) for p in set(input("Enter space separated ports to scan: ").strip().split())]
                    if len(ports) > 0:
                        self.port_scan(ports=ports)
                except:
                    print("SKIPPED: Invalid input")

            if inp[0] == "scp":
                self.ssh_check()
                if len(self.reachable_hosts) == 0:
                    getpass.getpass("No accessible host found.\n\n[Press ENTER to continue]")
                    continue
                try:
                    localpath = input("Enter local path: ").strip()
                    remotepath = input("Enter remote path: ").strip()
                except:
                    print("SKIPPED: Invalid input")
                if not os.path.exists(localpath):
                    print("SKIPPED: local path '"+localpath+"' does not exists")
                else:
                    self.scp(localpath=localpath,remotepath=remotepath)

            if inp[0] == "execute":
                self.ssh_check()
                if len(self.reachable_hosts) == 0:
                    getpass.getpass("No accessible host found.\n\n[Press ENTER to continue]")
                    continue
                titles = set([r["action"].replace("execute: ","") for r in self.report if r["action"].split()[0] == "execute:"])
                title = self.get_arg(prompt="Enter a title for this execution")
                if title in titles:
                    print("SKIPPED: Title '"+title+"' already exists. Try another title")
                elif len(title) > 0:
                    osreport =[]
                    for op in [r for r in self.report if r["action"] == "os_check"]:
                        hostname = op["hostname"]
                        if op["stdout"] != "" and len(op["stdout"].split()) > 1:
                            osname, kernel_release, arch = op["stdout"].split()[0:3]
                            if osname == "Linux" and len(op["stdout"].splitlines()) > 1:
                                dist = op["stdout"].splitlines()[1]
                            else:
                                dist = op["stdout"].split()[1]
                            osreport.append(dict(hostname=hostname,os=osname,kernel_release=kernel_release,
                                                arch=arch,dist=dist))
                        else:
                            osreport.append(dict(hostname=hostname,os="N/A",kernel="N/A",kernel_release="N/A",
                                                arch="N/A",dist="N/A"))
                    kernels = set([o["os"] for o in osreport if o["hostname"] in self.reachable_hosts])
                    comm = []
                    for k in kernels:
                        hosts = [o["hostname"] for o in osreport if o["os"] == k]
                        if self.confirm("Is the command same for all "+k+" variants like '"+hosts[0]+"'..."):
                            command = input("Enter command: ").strip()
                            print()
                            if len(command) > 0:
                                comm.append([command, hosts])
                        else:
                            dists = set([o["dist"] for o in osreport if o["os"] == k and o["dist"] != ""])
                            for d in dists:
                                hosts = [o["hostname"] for o in osreport if o["os"] == k and o["dist"] == d]
                                print("\tLet's execute on only "+k+"("+d+") based hosts like '"+hosts[0]+"'...")
                                command = input("\tEnter command: ").strip()
                                print()
                                if len(command) > 0:
                                    comm.append([command, hosts])
                    if len(comm) > 0:
                        for command, hosts in comm:
                            self.execute(action="execute: "+title,hosts=hosts,command=command)
                    else:
                        print("SKIPPED: Nothing to execute")
                else:
                    print("SKIPPED: Invalid title")

            if inp[0] == "help":
                if len(inp) >1:
                    try:
                        print(self.help_menu[inp[1]])
                    except:
                        print("Available options are:\n\n\t"+"\n\t".join([k for k,v in self.help_menu.items()]))
                    print()
                else:
                    if len(self.activities) > 0:
                        print("Activities:")
                        print(tabulate([(k,v) for k,v in self.activities.items()]))
                        print()
                    print("Options:")
                    print(tabulate([(k,v) for k,v in self.choices.items()]))
                    print()

            try:
                getpass.getpass("\n[Press ENTER to continue]")
            except:
                pass


class Activity_CLI(Activity):
    def __init__(self):
        self.parser = argparse.ArgumentParser(prog=__file__, description=None)

        self.parser.add_argument('-hosts', dest="hosts", nargs='*', default=[],
                            help='space seperated hostnames')

        self.parser.add_argument('-id', dest='reportid', default=None,
                            help='''specify the report id which you want to open/create
                            (if not specified, it will be temporarily assigned)''')

        self.parser.add_argument('-user', dest='username', default=USERNAME,
                            help='remote username (default: '+USERNAME+')')

        self.parser.add_argument('-pass', dest='password',  default=PASSWORD,
                            help='remote user\'s password (optional, as it prefers private key authentication)')

        self.parser.add_argument('-dbhost', dest='dbhost', default=DBHOST,
                            help='database hosted on (default: '+DBHOST+')')

        self.parser.add_argument('-dbuser', dest='dbuser', default=DBUSER,
                            help='database username (default: '+DBUSER+')')

        self.parser.add_argument('-dbpass', dest='dbpassword', default=DBPASSWORD,
                            help='database password')

        self.parser.add_argument('-timeout', dest='timeout', type=int,  default=TIMEOUT,
                            help='maximum allowed time in seconds for each execution (default: '+str(TIMEOUT)+')')

        self.parser.add_argument('-threads', dest='threads_threshold', type=int,  default=TIMEOUT,
                            help='maximum number of threads allowed (default: '+str(PARALLEL_LIMIT)+')')

        self.parser.add_argument('-sudo', dest='sudo', default="yes",
                            help='whether to use `sudo ssh`: [yes/no] (default: '+("yes" if SUDO else "no")+')')

        self.parser.add_argument('-ping_check', dest='ping_check', action='store_true', default=False,
                            help='display ping check report for all specified hosts')

        self.parser.add_argument('-console_check', dest='console_check', action='store_true', default=False,
                            help='list available management consoles of physical servers')

        self.parser.add_argument('-os_check', dest='os_check', action='store_true', default=False,
                            help='perform OS check of all available hosts')

        self.parser.add_argument('-dump_config', dest='dump_config', action='store_true', default=False,
                            help='fetch current configuration of available hosts')

        self.parser.add_argument('-port_scan', dest='ports', nargs='*', type=int, default=[],
                            help='''perform port scan on listed hosts
                                    (example: -port_scan 22 80 443)''')

        self.parser.add_argument('-id_and_homedir_check', dest="ids", nargs='*', default=[],
                            help='''perform id and homedirectory check for specified users
                                    (example: -id_and_homedir_check root apache)''')

        self.parser.add_argument('-mount_check', dest='mounts', nargs='*', default=[],
                            help='''check if specified directories are mounted properly and if in read-only state
                                    (example: -mount_check /tmp /var/log)''')

        self.parser.add_argument('-scp', dest='scp', nargs='*', default=[],
                            help='''copy file/directory over ssh to specified hosts
                                    (example: -scp /var/log ~/)''')

        self.parser.add_argument('-execute', dest='command', default=False,
                            help='''execute commands on available hosts. ***NOT PREFERRED IN NON INTERACTIVE MODE***
                                    (example: -execute "date; df -lh"''')

        self.parser.add_argument('-list', dest='list', action='store_true', default=False,
                            help='list all activity reports')

        self.parser.add_argument('-rename', dest='new_id',
                            help='rename the specified activity report (example: -id old_id -rename new_id)')

        self.parser.add_argument('-clean', dest='clean', action='store_true', default=False,
                            help='clean the specified activity report (example: -id id_to_clean -clean)')

        self.parser.add_argument('--version', action='version', version='%(prog)s 1.0')

    def run(self):
        results = self.parser.parse_args()

        if len(results.hosts) > 0 or results.reportid or results.list:
            if results.sudo.lower() in ["n", "no"]:
                sudo = False
            else:
                sudo = True

            a = Activity(hosts=results.hosts, reportid=results.reportid, sudo=sudo, username=results.username, password=results.password,
                         dbuser=results.dbuser, dbpassword=results.dbpassword, timeout=results.timeout)

            if results.ping_check:
                output = a.ping_check()
                print(json.dumps(output,indent=2))
            if results.console_check:
                output = a.console_check()
                print(json.dumps(output,indent=2))
            if results.os_check:
                output = a.os_check()
                print(json.dumps(output,indent=2))
            if results.dump_config:
                output = a.dump_config()
                print(json.dumps(output,indent=2))
            if len(results.ports) > 0:
                output = a.port_scan(ports=results.ports)
                print(json.dumps(output,indent=2))
            if len(results.ids) > 0:
                output = a.id_and_homedir_check(results.ids)
                print(json.dumps(output,indent=2))
            if len(results.mounts) > 0:
                output = a.mount_check(results.mounts)
                print(json.dumps(output,indent=2))
            if len(results.scp) == 2:
                localpath, remotepath = results.scp
                output = a.scp(localpath, remotepath)
                print(json.dumps(output,indent=2))
            if results.command:
                a.ssh_check()
                output = a.execute(hosts=a.reachable_hosts,action="execute: "+results.command,command=results.command)
                print(json.dumps(output,indent=2))
            if results.clean or not results.reportid:
                a.clean()
            if results.new_id:
                a.rename(results.new_id)
            if results.list:
                print(json.dumps(a.list(),indent=2))
        else:
            # Wrong argument
            self.parser.print_help()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Enter non-interactive mode
        a = Activity_CLI()
        a.run()
    else:
        # Enter interactive mode
        a = Activity_Interactive()
        a.interact()
