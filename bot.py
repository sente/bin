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
password = getpass.getpass("password? ")


def cmd(str):
        s = subprocess.Popen(str, shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        stdout,stderr = s.communicate()
        return stdout, stderr


def execute_cmd(cmd_string="",foo=""):
    stdout,stderr = cmd(cmd_string)

    if stdout or stderr:
        os.mkdir("/var/www/sente/htdocs/xmpp-bot/data/" + foo)

        if stdout:
            with open("/var/www/sente/htdocs/xmpp-bot/data/" + foo + "/stdout", "w") as handle:
                handle.write(stdout)

        if stderr:
            with open("/var/www/sente/htdocs/xmpp-bot/data/" + foo + "/stderr", "w") as handle:
                handle.write(stderr)

    return (stdout, stderr,)


def message_handler(connect_object, message_node):
    from_user = message_node.getFrom().getStripped()

    print from_user
    if not from_user.startswith(accepted_user):
        connect_object.send( xmpp.Message( message_node.getFrom(), "not authorized"))

    command = str(message_node.getBody())

    foo = "".join(random.sample("0123456789ABCDEF",8))

    message,message_stderr = execute_cmd(cmd_string=command, foo=foo)

    if message:
        size=len(message)
        lines=len(message.split("\n"))
        stderr_size=len(message_stderr)

        url= "http://www.sente.cc/xmpp-bot/data/%s/stdout" % foo

        summary = "%d bytes %d lines %d stderr" % (size, lines, stderr_size)
        tail = "full response %s" % url
        if len(message_stderr) >  0:
            tail=tail + "\nand stderr: %s" % url.replace("stdout","stderr")

        if lines > 20:
            message_jabber="\n".join(message.splitlines()[0:10])
            connect_object.send( xmpp.Message( message_node.getFrom(), summary))
            connect_object.Process(0)
            connect_object.send( xmpp.Message( message_node.getFrom(), message_jabber))
            connect_object.Process(0)
            connect_object.send( xmpp.Message( message_node.getFrom(), tail))
        else:
            connect_object.send( xmpp.Message( message_node.getFrom(), summary))
            connect_object.Process(0)
            connect_object.send( xmpp.Message( message_node.getFrom(), message))
            connect_object.Process(0)
            connect_object.send( xmpp.Message( message_node.getFrom(), tail))

    elif message_stderr:
        connect_object.send( xmpp.Message( message_node.getFrom() ,message_stderr))
    else:
        connect_object.send( xmpp.Message( message_node.getFrom(),"no output"))


if __name__ == '__main__':
    jid = xmpp.JID(user)
    connection = xmpp.Client(server)
    connection.connect()
    result = connection.auth(jid.getNode(), password, "LFY-client")
    connection.RegisterHandler('message', message_handler)
    connection.sendInitPresence()

    while(connection.Process(0)):
        pass
