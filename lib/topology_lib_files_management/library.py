# -*- coding: utf-8 -*-
#
# Copyright (C) 2016 Maria Alas
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

"""
topology_lib_files_management communication library implementation.
"""

from __future__ import unicode_literals, absolute_import
from __future__ import print_function, division

# Add your library functions here.


def scp_command(enode, origin_file, destination_file, remote_user=None,
                remote_ip=None, remote_side=None, remote_pass=None, c=None,
                i=None, p=False, r=False, v=False, bash=False, q=False,
                compress=False, ssh_file=None, port=None, program=None, o=None,
                four=False, six=False, shell='bash'):
    """
    This function will execute a SCP command on the enode

    -origin_file: the path and the file that you want to copy,
    example: /etc/ssl/certs/server.crt

    -destination_file: this will be the path of the destination,
    example: /home/.

    -remote_user: this should be the user of the remote host

    -remote_ip: this should be the IP address of the remote host

    -remote_side= origin|destination this should be whom is the remote side,
    if the value is not origin, it will do with the destination as remote

    -remote_pass: this should be the password of the remote host

    -c cipher; selects the cipher to use for encrypting the data
    transfer. This option is directly passed to ssh(1)

    -i identity_file: Selects the file from which the identity (private key)
    for RSA authentication is read. This option is directly passed to ssh(1)

    -p: Preserves modification times, access times,
    and modes from the original file.

    -r: Recursively copy entire directories.

    -v: Verbose mode. Causes scp and ssh(1) to print debugging messages about
    their progress. This is helpful in debugging connection, authentication,
    and configuration problems.

    -batch: -B: Selects batch mode (prevents asking for passwords).

    -q: Disables the progress meter.

    -compress = -C: Compression enable. Passes the -C flag to ssh(1) to enable
    compression.

    -ssh_file = -S ssh_config: Specifies an alternative per-user configuration
    file for ssh. This option is directly passed to ssh(1).

    -port = -P port: Specifies the port to connect to on the remote host. Note
    that this option is written with a capital `P' because -p is already
    reserved for preserving the times and modes of the file in rcp(1).

    -program = -S program: Name of program to use for the encrypted connection.
    The program must understand ssh(1) options.

    -o ssh_option: Can be used to pass options to ssh in the format used in
    ssh_config5. This is useful for specifying options for which there is no
    separate scp command-line flag. For example, forcing the use of protocol
    version 1 is specified using scp -oProtocol=1

    -four = -4: Forces scp to use IPv4 addresses only.

    - six = -6: Forces scp to use IPv6 addresses only
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
        enode._bash_prompt = (
                r'Are you sure you want to continue connecting'
                r' \(yes/no\)\?|root.* password: '
                )
        response = enode(scp_cmd, shell=shell)
        if 'authenticity' in response:
            enode('yes', shell=shell)
        enode._bash_prompt = (
                r'\r\n[^\r\n]+@.+[#$]'
        )
        pass_response = enode(remote_pass, shell=shell)
        assert '100%' in pass_response
    else:
        scp_response = enode(scp_cmd, shell=shell)
        assert scp_response is ''


def rm_command(enode, file_to_rm, d=False, f=True, i=False, r=False, v=False,
               shell='bash'):
    """
    This function will execute rm in a linux machine

    file_to_rm: This is the file, or path or the file, or directory that will
    be removed

    -d: --directory Unlink FILE, even if it is a non-empty directory
    (super-user only)

    -f: --force Ignore nonexistent files, never prompt
    **If this flag is set as FALSE, it will need to add the functionality
    of answer the question of the prompt, since it is not implemented yet***

    -i: --interactive, prompt before any removal

    -r, -R, --recursive, remove the contents of directories recursively

    -v, --verbose: explain what is being done
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
    This function uses sftp command to get file from remote  sftp server

    source_file_path: This can be a path with file name or just a file name
    lying in remote sftp server

    dest_file_path: This can be a path with file name or just file name to be
    copied to sftp client(enode)
    """

    sftp_command = 'sftp {}@{}:{} {}'.format(
        user, server_ip, source_file_path, dest_file_path)
    pass_response = enode(sftp_command, shell='bash')
    if 'authenticity' in pass_response:
        enode('yes', shell='bash')
    assert '100%' in pass_response, 'sftp copy failed'


def file_exists(enode, file_name, path):
    """
    This method is used to check file existenc in given path
    """
    file_exists = enode('ls {}'.format(path), shell='bash')
    assert file_name in file_exists, 'file does not exists'

__all__ = [
    'scp_command',
    'rm_command',
    'sftp_getfile',
    'file_exists'
]
