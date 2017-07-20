# WA105_plots
Scripts to copy data and plot histograms from wa105db

-Get all the files named Data_* from wa105db/tools/pcotte_getData that you do not already have, using copy_data.sh (no argument)
-Plot with plot_data.sh, need at least the file to analyse as an argument (folder is not enough, need the file). Can also specify the start and end times (4 arguments since need a space between day and hour)
-Python scripts in pyfiles : 
  -plot_functions.py contains all the different functions that could plot what you want. Feel free to add those you might need and do not already exist.
  -plot_data.py is where you will call those functions.
-param_list.txt contains all the parameters that should be in the datafile. If a parameter asked in plot_data.py is not in the param_list.txt, it is ignored. Same if it is in param_list.txt but not in datafile. 

WARNING: Do not remove any function in plot_function.py, just comment them in plot_data.py. Same pour parameters in param_list.

