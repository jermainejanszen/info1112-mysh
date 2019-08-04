# mysh
A command interpreter written in Python

Commands:
- Non-built-in commands:
    Treat as a path to an executable file
- exit:
    Exit mysh with message 'Goodbye!'
- say [arg...]:
    Echoes [arg] to standard output
- changedir [directoryname]:
    Change directory to [directoryname]
- showdir:
    Prints current working directory
- historylist:
    Lists directories previously visited by mysh
- cdn [n]:
    Changes directory to the numbered directory as shown in historylist
- show [filename...]:
    Reads from each filename in turn to standard output
- set [variable[value...]]:
    If no arguments are given print all variable currently defined
    Otherwise sets the entered variables to the given values
- unset [variable]:
    Removes variable from list of defined variables
- sleep [N]:
    Sleeps for [N] seconds

Redirection:
- '<' is used to indicate standard input
- '>' is used to indicate standard output

Piping:
- '|' is used to redirect standard output from one command to the standard input of another

