#!/usr/bin/python
"""
    bot.py: this starts up an XMPP-Jabber bot which lets you interact with the command line

    data is saved in /var/www/sente/htdocs/xmpp-bot/data/
"""


import xmpp
import os
import sys
import getpass
import subprocess
import random

user = "stupow@gmail.com"
server = "gmail.com"

accepted_user = "stuart.powers@gmail.com" #only accept commands from this user
output_root = "/var/www/sente/htdocs/xmpp-bot/data"



def cmd(str):
    """
    execute `str` as a subprocess.Popen piped command, return a tuple of (stdout,stdout)
    """
    s = subprocess.Popen(str, shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    stdout,stderr = s.communicate()
    return stdout, stderr


def execute_cmd(cmd_string="",foo=""):
    """
    execute the `cmd_string`, saving both `stdout` and `stdout`
    and then return `(stdout, stderr,)`
    """

    stdout,stderr = cmd(cmd_string)

    if stdout or stderr:
        output_dir = os.path.join(output_root, foo)
        os.mkdir(output_dir)

        if stdout:
            with open("%s/%s/stdout" % (output_root, foo), "w") as handle:
                handle.write(stdout)
        if stderr:
            with open("%s/%s/stderr" % (output_root, foo), "w") as handle:
                handle.write(stderr)

    return (stdout, stderr,)


def message_handler(connect_object, message_node):

    from_user = message_node.getFrom().getStripped()

    if not from_user.startswith(accepted_user):
        connect_object.send( xmpp.Message( message_node.getFrom(), "not authorized"))

    command = str(message_node.getBody())

    foo = "".join(random.sample("0123456789ABCDEF",8))

    message,message_stderr = execute_cmd(cmd_string=command, foo=foo)

    if message or message_stderr:
        size=len(message)
        lines=len(message.split("\n"))
        stderr_size=len(message_stderr)

        stdout_url= "http://www.sente.cc/xmpp-bot/data/%s/stdout" % foo
        stderr_url= "http://www.sente.cc/xmpp-bot/data/%s/stderr" % foo

        summary = "%s %d bytes\n%s %d bytes" % (stdout_url, len(message), stderr_url, len(message_stderr))
        connect_object.send( xmpp.Message(message_node.getFrom(), summary) )
    else:
        connect_object.Process(0)


if __name__ == '__main__':

    password = getpass.getpass("password? ")
    jid = xmpp.JID(user)
    connection = xmpp.Client(server)
    connection.connect()
    result = connection.auth(jid.getNode(), password, "LFY-client")
    connection.RegisterHandler('message', message_handler)
    connection.sendInitPresence()

    while(connection.Process(0)):
        pass
