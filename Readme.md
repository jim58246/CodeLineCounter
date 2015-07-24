Code Line Counter
=================
This project should be valid for python3.x, without need for any extra package.

### usage ###

- clc.py is the core module which provide CLI. Usage: `clc.py [directory_or_file]`. Feed it with one argument `directory_or_file`, if no argument fed, it uses current working directory.
- gui.py will start the GUI. 

### extend and improvement

- in clc.py, the algorithm for statistics is put in a single function called `analyse_file`, you can improve it with new algorithm.

The target of this project is to make a simple code line counter for python source code.

I have not found a good/easy enough python code counter tool. So I made one for myself.

I use OOP and tkinter for this project, currently no extra package required. `tree.py` and `obsqueue.py` come from other project, they are reused here, so you may see some excess code in these modules.