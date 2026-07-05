"""
A static dictionary for Semantic Caching of common Linux commands.
This intercepts the LLM explainer so that common queries are instant and cheap.
"""

COMMAND_CACHE = {
    "ls": (
        "**`ls`**: Lists directory contents.\n\n"
        "**Syntax:** `ls [options] [file/directory]`\n\n"
        "**Examples:**\n"
        "1. `ls -l` (Lists files in long format with details)\n"
        "2. `ls -a` (Lists all files including hidden ones)\n"
        "3. `ls -lh` (Lists details in human-readable sizes)"
    ),
    "tar": (
        "**`tar`**: Tape archiver utility for storing and extracting files from an archive file.\n\n"
        "**Syntax:** `tar [options] [archive-file] [file/directory]`\n\n"
        "**Examples:**\n"
        "1. `tar -czvf archive.tar.gz /path/to/dir` (Create a compressed gzip archive)\n"
        "2. `tar -xzvf archive.tar.gz` (Extract a compressed gzip archive)\n"
        "3. `tar -cvf archive.tar /path/to/dir` (Create an uncompressed archive)"
    ),
    "grep": (
        "**`grep`**: Prints lines matching a pattern.\n\n"
        "**Syntax:** `grep [options] pattern [file]`\n\n"
        "**Examples:**\n"
        "1. `grep 'error' /var/log/syslog` (Search for the word 'error' in a file)\n"
        "2. `grep -r 'TODO' .` (Search recursively for 'TODO' in the current directory)\n"
        "3. `grep -i 'hello' text.txt` (Search case-insensitively for 'hello')"
    ),
    "cd": (
        "**`cd`**: Changes the current directory.\n\n"
        "**Syntax:** `cd [directory]`\n\n"
        "**Examples:**\n"
        "1. `cd /var/log` (Change to the /var/log directory)\n"
        "2. `cd ..` (Move one directory up)\n"
        "3. `cd ~` (Go to the user's home directory)"
    ),
    "rm": (
        "**`rm`**: Removes files or directories.\n\n"
        "**Syntax:** `rm [options] [file/directory]`\n\n"
        "**Examples:**\n"
        "1. `rm file.txt` (Remove a specific file)\n"
        "2. `rm -r folder/` (Remove a directory and its contents recursively)\n"
        "3. `rm -f file.txt` (Force removal without prompting)"
    ),
    "find": (
        "**`find`**: Searches for files in a directory hierarchy.\n\n"
        "**Syntax:** `find [path] [expression]`\n\n"
        "**Examples:**\n"
        "1. `find . -name '*.txt'` (Find all .txt files in the current directory and subdirectories)\n"
        "2. `find / -size +100M` (Find files larger than 100MB on the entire system)\n"
        "3. `find . -mtime -7` (Find files modified in the last 7 days)"
    ),
    "mv": (
        "**`mv`**: Moves or renames files and directories.\n\n"
        "**Syntax:** `mv [options] source destination`\n\n"
        "**Examples:**\n"
        "1. `mv old.txt new.txt` (Rename a file)\n"
        "2. `mv file.txt /path/to/dest/` (Move a file to a different directory)\n"
        "3. `mv -i file.txt /dest/` (Prompt before overwriting an existing file)"
    ),
    "cp": (
        "**`cp`**: Copies files and directories.\n\n"
        "**Syntax:** `cp [options] source destination`\n\n"
        "**Examples:**\n"
        "1. `cp file.txt copy.txt` (Copy a file)\n"
        "2. `cp -r folder/ new_folder/` (Copy a directory and its contents recursively)\n"
        "3. `cp -a /source /dest` (Archive mode: copy preserving all permissions and attributes)"
    ),
    "mkdir": (
        "**`mkdir`**: Creates a new directory.\n\n"
        "**Syntax:** `mkdir [options] directory`\n\n"
        "**Examples:**\n"
        "1. `mkdir folder` (Create a directory named 'folder')\n"
        "2. `mkdir -p /a/b/c` (Create parent directories as needed)\n"
        "3. `mkdir dir1 dir2` (Create multiple directories at once)"
    ),
    "cat": (
        "**`cat`**: Concatenates files and prints them on the standard output.\n\n"
        "**Syntax:** `cat [options] [file]`\n\n"
        "**Examples:**\n"
        "1. `cat file.txt` (Display the contents of a file)\n"
        "2. `cat file1.txt file2.txt > combined.txt` (Combine two files into a new one)\n"
        "3. `cat -n file.txt` (Number all output lines)"
    )
}
