Code Line Counter
=================
This project should be valid for python3.x, without need for any extra package.

### usage ###

- clc.py is the core module which provide CLI. Usage: `clc.py [directory_or_file]`. Feed it with one argument `directory`, if no argument fed, it use current working directory.
- gui.py will start the gui. It provide a save button to save result in a txt file.

### extand and improvement

- in clc.py, the algorithm for statistics is in a single function called `analyse_file`, you can improve it with new algorithm.

The target of this project is to make a simple code line counter for python source code.

I found most of metrics tools are not easy for startup. So I made one for myself.

I use OOP and tkinter for this project, currently no extra package required. `tree.py` and `obsqueue.py` come from other projects, they are reused here, so you may see something excess method in these modules.