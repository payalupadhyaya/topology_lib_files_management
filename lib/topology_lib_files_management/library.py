# Copyright (C) 2016 Hewlett Packard Enterprise Development LP
# All Rights Reserved.
#
# The contents of this software are proprietary and confidential
# to the Hewlett Packard Enterprise Development LP. No part of this
# program may be photocopied, reproduced, or translated into another
# programming language without prior written consent of the
# Hewlett Packard Enterprise Development LP.

"""
topology_lib_files_management communication library implementation.
"""

from __future__ import unicode_literals, absolute_import
from __future__ import print_function, division
import os
import re
import requests
import codecs


def scp_command(enode, origin_file, destination_file, remote_user=None,
                remote_ip=None, remote_side=None, remote_pass=None, c=None,
                i=None, p=False, r=False, v=False, bash=False, q=False,
                compress=False, ssh_file=None, port=None, program=None, o=None,
                four=False, six=False, shell='bash'):
    """
    This function will execute a SCP command on the enode
    IMPORTANT: It is implemented to work from bash of the SW

    :param str origin_file: The file or path to copy.
    :param str destination_file: The destination path Ex. /home/.
    :param str remote_user: The user of the remote host.
    :param str remote_ip: The IP Address of the remote host.
    :param str remote_side: Whom is the remote side.
    Options: origin|destination; Default: destination
    :param str remote_pass: The password of the remote host.
    :param str c: Selects the cipher to use for encrypting the data transfer.
    This option is directly passed to ssh(1).
    :param str i: Selects the file from which the identity (private key)
    for RSA authentication is read. This option is directly passed to ssh.
    :param bool p: Preserves modification times, access times,
    and modes from the original file; Default: False.
    :param bool r: Recursively copy entire directories; Default: False.
    :param bool v: Verbose mode. Causes scp and ssh to print debugging messages
    about their progress. This is helpful in debugging connection, authentica-
    tion, and configuration problems; Default: False.
    :param bool bash: -B: Selects batch mode (prevents asking for passwords);
    Default: False.
    :param bool q: Disables the progress meter;  Default: False.
    :param bool compress: -C: Compression enable flag to SSH; Default: False.
    :param str ssh_file: -S ssh_config: Specifies an alternative per-user
    configuration file for ssh. This option is directly passed to ssh.
    :param str port: Specifies the port to connect to on the remote host. Note:
    that this option is written with a capital 'port' because 'p' is already
    reserved for preserving the times and modes of the file in rcp.
    :param str program: Name of program to use for the encrypted connection.
    The program must understand ssh options. -S command.
    :param str o: ssh_option: Can be used to pass options to ssh in the format
    used in ssh_config5.
    :param bool four: -4: Forces scp to use IPv4 addresses only; Default: False
    :param bool six: -6: Forces scp to use IPv6 addresses only. Default: False.
    """

    arguments = locals()

    required_arg = ['origin_file', 'destination_file']

    remote_arg = ['remote_user', 'remote_ip', 'remote_file']

    optional_arg = {'c': '-c', 'i': '-i', 'p': '-p', 'r': '-r', 'v': '-v',
                    'bash': '-B', 'q': '-q', 'compress': '-C',
                    'ssh_file': '-S', 'port': '-P', 'program': '-S',
                    'o': '-o', 'four': '-4', 'six': '-6'}

    options = ''
    command = origin_file + " " + destination_file

    uses_remote_host = False
    for key, value in list(arguments.items()):
        # if exists a remote part, this will add it
        if key in remote_arg and uses_remote_host is False:
            if value is not None:
                uses_remote_host = True
                command = ''
                if remote_side == "origin":
                    command = '{0}@{1}:{2} {3}'.format(remote_user, remote_ip,
                                                       origin_file,
                                                       destination_file)
                else:
                    command = '{0} {1}@{2}:{3}'.format(origin_file,
                                                       remote_user,
                                                       remote_ip,
                                                       destination_file)

        # this will add the optional parameters
        if key not in required_arg:
            if key != "remote_pass" and key in optional_arg:
                if value is True:
                    options = '{0}{1} '.format(options, optional_arg.get(key))
                elif value is not False and value is not None:
                    options = '{0}{1} {2} '.format(options,
                                                   optional_arg.get(key),
                                                   value)

    scp_cmd = 'scp {0}{1}'.format(options, command)

    if remote_user is not None:
        bash = enode.get_shell('bash')
        match_prompt = (
            r'\(yes/no\)\?|password: '
        )
        bash.send_command(scp_cmd, matches=match_prompt)
        response = bash.get_response()

        if 'Are you sure you want' in response:
            bash.send_command('yes', matches=match_prompt)
        bash.send_command(remote_pass)
        pass_response = bash.get_response()
        assert '100%' in pass_response
    else:
        scp_response = enode(scp_cmd, shell=shell)
        assert scp_response is ''


def rm_command(enode, file_to_rm, d=False, f=True, i=False, r=False, v=False,
               shell='bash'):
    """
    This function will execute rm in a linux machine

    :param str file_to_rm: This is the file, or path or the file, or directory
    that will be removed.
    :param bool d: --directory Unlink FILE, even if it is a non-empty directory
    (super-user only); Default: False.
    :param bool f: Ignore nonexistent files, never prompt. Default: True.
    ***If this flag is set as FALSE, it will need to add the functionality
    of answer the question of the prompt, since it is not implemented yet***
    :param bool i: --interactive, prompt before any removal; Default: False.
    :param bool r: Remove the contents of directories recursively;
    Default: False.
    :param bool v: --verbose; explain what is being done; Default: False.
    """

    arguments = locals()
    required_arg = ['file_to_rm']
    optional_arg = {'d': '-d', 'f': '-f', 'i': '-i', 'r': '-r', 'v': '-v'}

    command = file_to_rm
    options = ''

    for key, value in list(arguments.items()):
        if value is True:
            options = '{0}{1} '.format(options, optional_arg.get(key))

    rm_cmd = 'rm {0}{1}'.format(options, command)
    rm_response = enode(rm_cmd, shell=shell)
    assert rm_response is ''


def sftp_getfile(enode, user, server_ip, source_file_path, dest_file_path):
    """
    This function uses sftp command to get file from remote sftp server

    :param str source_file_path: This can be a path with file name or just a
    file name lying in remote sftp server
    :param str dest_file_path: This can be a path with file name or just file
    name to be copied to sftp client(enode)
    """

    sftp_command = 'sftp {}@{}:{} {}'.format(
        user, server_ip, source_file_path, dest_file_path)
    pass_response = enode(sftp_command, shell='bash')
    if 'authenticity' in pass_response:
        enode('yes', shell='bash')
    assert '100%' in pass_response, 'sftp copy failed'


def file_exists(enode, file_name, path):
    """
    This method is used to check file exist in given path
    using ls command

    :param str file_name: File name to verify if exists
    :param str path: Path of the file
    """
    file_exists = enode('ls {}'.format(path), shell='bash')
    assert file_name in file_exists, 'file does not exists'


def echo_filecopy(enode, source_file_path, destn_file_path):

    """
    This function will copy the source file to enode destination file path
    using enode rapid fire() with echo command.

    :param str source_file_path: This is the file, or path or the file to be
    copied
    :param str destn_file_path: This is the file, or path for the destination
    on enode
    """
    assert len(source_file_path) > 0, "empty source file path"
    # TODO add a check for source file existance
    assert os.path.isfile(source_file_path), "source file doesn't exists"
    assert len(destn_file_path) > 0, "empty destination file path"
    file_remove_command = "rm "+destn_file_path
    enode(file_remove_command, shell="bash")
    with open(source_file_path, "r") as source_file:
        for line in source_file:
            enode('echo "' + line + '" >> ' + destn_file_path,
                  shell="bash")


def create_filebkup(enode, destn_file_path):

    """
    This function will create backup of the specified file at same destn path

    :param str destn_file_path: This is the file, or path for the destination
    on enode where backup needs to be created with an extension ".bkup"
    """
    assert len(destn_file_path) > 0, "empty destination file path"
    # TODO add a check for destination file existance
    remote_file_chk_command = "ls -l "+destn_file_path
    output = enode(remote_file_chk_command, shell="bash")
    assert "No such file or directory" not in output, "destn file not exists"
    backup_destn_file_path = destn_file_path + ".bkup"
    backup_create_command = "cp "+destn_file_path+" "+backup_destn_file_path
    enode(backup_create_command, shell="bash")


def restore_filebkup(enode, destn_file_path):

    """
    This function will restores backup of the specified file at same destn path
    and deletes the .bkup file

    :param str destn_file_path: This is the file, or path for the destination
    on enode to be restored back from destn_file_path.bkup file
    """
    assert len(destn_file_path) > 0, "empty destination file path"
    backup_destn_file_path = destn_file_path + ".bkup"
    # TODO add a check for source file existance
    remote_file_chk_command = "ls -l "+backup_destn_file_path
    output = enode(remote_file_chk_command, shell="bash")
    assert "No such file or directory" not in output, "dest file not exists"
    backup_restore_command = "cp "+backup_destn_file_path+" "+destn_file_path
    enode(backup_restore_command, shell="bash")
    enode("rm -f "+backup_destn_file_path, shell="bash")


def _get_file_contents(file_orig):
    """
    Returns the contents of a file hosted on local or remote location

    :param str file_orig: File to get content.
    :returns: The content of the file.
    :rtype: str.
    """
    # TODO: Add support for other remotes, e.g. ftp://
    is_remote = re.compile("http[s]?://")
    if is_remote.match(file_orig):
        result = requests.get(file_orig)
        assert result.status_code is not requests.codes.not_found, \
            "File not found: {}".format(file_orig)
        assert result.status_code is requests.codes.ok, \
            "Unable to get file: {} Error code: {}" \
            "".format(file_orig,
                      result.status_code)
        file_contents = result.text
    else:
        try:
            file = open(file_orig)
            file_contents = file.read()
            file.close()
        except Exception as e:
            assert False, "Unable to get file {}: {}".format(file_orig, e)
    return file_contents


def _python_exec(shell, cmd):
    """ Uses a node shell to run a command and expect Python's prompt """
    shell.send_command(cmd, matches=">>> ")


def exists(enode, file):
    """
    Verifies the file existence with stat

    :param file: the file name (and path if needed)
    :returns: whether the file exists or not
    :rtype: Boolean
    """

    res = enode("stat {file}".format(**locals()), shell="bash")
    return "stat: cannot stat" not in res


def transfer_file(enode, name, file_orig, dst_path="/tmp"):
    """
    Transfer a remote or local text file using remote's Python

    The node must support Python with the "codecs" package
    The codecs package is used to transfer the file using hex format
    This is handy when transferring text files that may have special chars
    that are not properly handled with echo or other tools.

    :param name: the name to give the file after it is copied
    :param file_orig: URL to fetch the file from (including file name)
    :param dst_path: final location where to put the file in remote node
    """
    file_contents = _get_file_contents(file_orig)
    # Encoding the file makes it easy to handle special chars
    encoded = codecs.encode(file_contents.encode(), "hex").decode()
    remote_file = "{dst_path}/{name}".format(**locals())
    # From this point onwards, use remote's Python
    shell = enode.get_shell("bash")
    _python_exec(shell, "python")
    # Store the decoded content on a remote's Python variable
    _python_exec(shell, "import codecs")
    _python_exec(shell, "decoded = codecs.decode('{encoded}', 'hex').decode()"
                        "".format(**locals()))
    # Write the decoded contents to file
    _python_exec(shell, "file = open('{remote_file}', 'w')".format(**locals()))
    _python_exec(shell, "file.write(decoded)")
    _python_exec(shell, "file.close()")
    shell.send_command("exit()")

__all__ = [
    'scp_command',
    'rm_command',
    'sftp_getfile',
    'file_exists',
    'echo_filecopy',
    'create_filebkup',
    'restore_filebkup',
    'exists',
    'transfer_file',
]
