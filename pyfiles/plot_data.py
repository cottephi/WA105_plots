#!/usr/bin/python
import numpy,pickle,time,argparse, os,errno,re,sys, datetime, subprocess
sys.path.append("../../root-6.09.02/")
import ROOT
from plot_functions import *
import matplotlib.pyplot as plt
import scipy.interpolate
import numpy.fft
from time import gmtime, strftime

if len(sys.argv) != 5: # 1 is addValueInRegion.py + 3 arguments
  print "ERROR: Need 4 arguments: the start and end date, file to process and the output folder"
  sys.exit(1)

#Parameters to Supress output from ROOT
ROOT.gROOT.SetBatch(1)
#ROOT.gErrorIgnoreLevel = ROOT.kWarning

def primer_load_data(wanted_param):
  data_input = open(sys.argv[3], "r")
  command = "sed -n -e '/^" + wanted_param + "/p' ./param_list.txt | cut -d ' ' -f 2"
  code = subprocess.check_output([command], shell=True)
  if len(code) == 0:
    print("WARNING: " + wanted_param + " not found in ./param_list.txt. Ignored.")
    return ""

  code = code[:-1]
  first_line = subprocess.check_output("head -n1 " + sys.argv[3], shell=True)
  if code not in first_line:
    print("WARNING: " + code + ", code for " + wanted_param + ", not found in data file")
    return ""

  code_list = first_line.split(' ')
  pos = code_list.index(code)
  pos = pos + 1
  param = subprocess.check_output("cut -d ' ' -f " + str(pos) + " " + sys.argv[3], shell=True)
  param = param[:-1]
  param = param.split("\n")
  param.pop(0)
  return param
  
def load_data(wanted_param):
  time = primer_load_data("time")
  time = numpy.array( numpy.reshape(time, len(time)) )
  if wanted_param != "time":
    param = primer_load_data(wanted_param)
    if param == "":
      return ["ignore"]
    param = numpy.array( numpy.reshape(param, len(time)) )
    return param.astype(numpy.float)
  else:
    return time.astype(numpy.float)





print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!WARNING!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
print("Never use parameters name such as 'temp_1', 'temp_2' ... 'temp_10'... otherwise the 'sed' command of 'primer_load_data' will select both 'temp_1' and 'temp_10' when looking for 'temp_1', resulting in a crash. It is recommanded to put such numbering at the beginning of the name.")
print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!END OF WARNING!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")

###################################################################
###################################################################
###################################################################
#Load data
###################################################################
###################################################################
###################################################################

##################################### time
time = load_data("time")
if time[0] == "ignore":
  print("ERROR loading time. Plot can not continue.")
  exit(1)

##################################### Temperatures
temperatures = []
for i in range(0,12):
  temp = ( "%i_TE_RbCh2" %(i+1) )
  temperatures.append(load_data(temp))

Hall_T = load_data("Hall_T")

##################################### Pressures
pressures = []
pressures.append(load_data("PE_Abs_Tank"))
pressures.append(load_data("PE_Diff_Tank_Ins"))
pressures.append(load_data("PE_Diff_Tank_Atm"))

##################################### levelmeters
j = 1
levelmeters = []
for i in range(0,7):
  if(i==3): j +=1
  levelmeters.append( load_data("level_crp%i" %j) )
  j += 1

##################################### LEM UP I
LEM_Up_I = []
for i in range(0,12):
  LEM = ( "LEM_%i" %(i+1) )
  LEM = LEM + "_Up_I"
  LEM_Up_I.append(load_data(LEM)) 

##################################### LEM UP V
LEM_Up_V = []
for i in range(0,12):
  LEM = ( "LEM_%i" %(i+1) )
  LEM = LEM + "_Up_V"
  LEM_Up_V.append(load_data(LEM))

##################################### LEM Down I
LEM_Down_I = []
for i in range(0,12):
  LEM = ( "LEM_%i" %(i+1) )
  LEM = LEM + "_Down_I"
  LEM_Down_I.append(load_data(LEM))   

##################################### LEM Down V
LEM_Down_V = []
for i in range(0,12):
  LEM = ( "LEM_%i" %(i+1) )
  LEM = LEM + "_Down_V"
  LEM_Down_V.append(load_data(LEM)) 

##################################### Grid I
GRID_1_I = load_data("GRID_1_I")

##################################### Grid V
GRID_1_V = load_data("GRID_1_V")

##################################### Cathode I
Cathode_I = load_data("Cathode_I")

##################################### Cathode V
Cathode_V = load_data("Cathode_V")


###################### Boxes
#Box_1_1 = [Cathode_V, Cathode_I, GRID_1_V, GRID_1_I, levelmeters[0], LEM_Up_I[0], LEM_Down_I[0], LEM_Up_V[0], LEM_Down_V[0]]
#Box_1_3 = [Cathode_V, Cathode_I, GRID_1_V, GRID_1_I, levelmeters[0], LEM_Up_I[2], LEM_Down_I[2], LEM_Up_V[2], LEM_Down_V[2]]
#Box_2 = [Cathode_V, Cathode_I, GRID_1_V, GRID_1_I, levelmeters[1], LEM_Up_I[1], LEM_Down_I[1], LEM_Up_V[1], LEM_Down_V[1]]
#Box_3_5 = [Cathode_V, Cathode_I, GRID_1_V, GRID_1_I, levelmeters[2], LEM_Up_I[4], LEM_Down_I[4], LEM_Up_V[4], LEM_Down_V[4]]
#Box_3_6 = [Cathode_V, Cathode_I, GRID_1_V, GRID_1_I, levelmeters[2], LEM_Up_I[5], LEM_Down_I[5], LEM_Up_V[5], LEM_Down_V[5]]
#Box_5_10 = [Cathode_V, Cathode_I, GRID_1_V, GRID_1_I, levelmeters[3], LEM_Up_I[9], LEM_Down_I[9], LEM_Up_V[9], LEM_Down_V[9]]
#Box_5_12 = [Cathode_V, Cathode_I, GRID_1_V, GRID_1_I, levelmeters[3], LEM_Up_I[11], LEM_Down_I[11], LEM_Up_V[11], LEM_Down_V[11]]
#Box_6_11 = [Cathode_V, Cathode_I, GRID_1_V, GRID_1_I, levelmeters[4], LEM_Up_I[10], LEM_Down_I[10], LEM_Up_V[10], LEM_Down_V[10]]
#Box_6_12 = [Cathode_V, Cathode_I, GRID_1_V, GRID_1_I, levelmeters[4], LEM_Up_I[11], LEM_Down_I[11], LEM_Up_V[11], LEM_Down_V[11]]
#Box_7_7 = [Cathode_V, Cathode_I, GRID_1_V, GRID_1_I, levelmeters[5], LEM_Up_I[6], LEM_Down_I[6], LEM_Up_V[6], LEM_Down_V[6]]
#Box_7_8 = [Cathode_V, Cathode_I, GRID_1_V, GRID_1_I, levelmeters[5], LEM_Up_I[7], LEM_Down_I[7], LEM_Up_V[7], LEM_Down_V[7]]
#Box_8 = [Cathode_V, Cathode_I, GRID_1_V, GRID_1_I, levelmeters[6], LEM_Up_I[7], LEM_Down_I[7], LEM_Up_V[7], LEM_Down_V[7]]

###################### Time
tmin = float(sys.argv[1])
tmax = float(sys.argv[2])
#tmin = date_to_unix("2017-07-04 21:55:00")
#tmax = date_to_unix("2017-07-04 22:04:00")
if tmin != 0 or tmax != 1:
  date = unix_to_date(float(sys.argv[1])).split()[0]
else:
  date = ""

###################################################################
###################################################################
###################################################################
#Do the plots
###################################################################
###################################################################
###################################################################


###################### Pressures
if pressures[0][0] != "ignore":
  if not os.path.isdir(sys.argv[4] + "/pressures"):
    os.system("mkdir " + sys.argv[4] + "/pressures")
  a = plot_pressures(time, date, pressures[0], "Abs_Pressure_in_Tank", "./" + sys.argv[4] + "/pressures/", tmin, tmax)
if pressures[1][0] != "ignore":
  if not os.path.isdir(sys.argv[4] + "/pressures"):
    os.system("mkdir " + sys.argv[4] + "/pressures")
  a = plot_pressures(time, date, pressures[1], "Diff_Pressure_Tank-Insulation", "./" + sys.argv[4] + "/pressures/", tmin, tmax)
if pressures[2][0] != "ignore":
  if not os.path.isdir(sys.argv[4] + "/pressures"):
    os.system("mkdir " + sys.argv[4] + "/pressures")
  a = plot_pressures(time, date, pressures[2], "Diff_Pressure_Tank_Atm", "./" + sys.argv[4] + "/pressures/", tmin, tmax)

###################### ribon chain 2 temperatures
plot_temps = True
for i in range(0,len(temperatures)):
  if temperatures[i][0] == "ignore":
    plot_temps = False
if plot_temps == True:
  if not os.path.isdir(sys.argv[4] + "/temperatures"):
    os.system("mkdir " + sys.argv[4] + "/temperatures")
  a = plot_temperatures(time, date, temperatures, "Temp_Ribon_Chain_2", "./" + sys.argv[4] + "/temperatures/", tmin, tmax)
  a = plot_temperatures(time, date, [temperatures[3],temperatures[4]], "Temp_Ribon_Chain_2_4-5", "./" + sys.argv[4] + "/temperatures/", tmin, tmax)
  a = plot_temperatures(time, date, temperatures[3], "Temp_Ribon_Chain_2_4", "./" + sys.argv[4] + "/temperatures/", tmin, tmax)
  a = plot_temperatures(time, date, temperatures[4], "Temp_Ribon_Chain_2_5", "./" + sys.argv[4] + "/temperatures/", tmin, tmax)
else:
  if temperatures[3][0] != "ignore" and temperatures[4][0] != "ignore":
    if not os.path.isdir(sys.argv[4] + "/temperatures"):
      os.system("mkdir " + sys.argv[4] + "/temperatures")
    a = plot_temperatures(time, date, [temperatures[3],temperatures[4]], "Temp_Ribon_Chain_2_4-5", "./" + sys.argv[4] + "/temperatures/", tmin, tmax)
    a = plot_temperatures(time, date, temperatures[3], "Temp_Ribon_Chain_2_4", "./" + sys.argv[4] + "/temperatures/", tmin, tmax)
    a = plot_temperatures(time, date, temperatures[4], "Temp_Ribon_Chain_2_5", "./" + sys.argv[4] + "/temperatures/", tmin, tmax)
  else:
    if temperatures[3][0] != "ignore":
      if not os.path.isdir(sys.argv[4] + "/temperatures"):
        os.system("mkdir " + sys.argv[4] + "/temperatures")
      a = plot_temperatures(time, date, temperatures[3], "Temp_Ribon_Chain_2_4", "./" + sys.argv[4] + "/temperatures/", tmin, tmax)
    
    if temperatures[4][0] != "ignore":
      if not os.path.isdir(sys.argv[4] + "/temperatures"):
        os.system("mkdir " + sys.argv[4] + "/temperatures")
      a = plot_temperatures(time, date, temperatures[4], "Temp_Ribon_Chain_2_4", "./" + sys.argv[4] + "/temperatures/", tmin, tmax)

###################### Interpolated + fft
if Cathode_V[0] != "ignore" and Cathode_I[0] != "ignore":
  if not os.path.isdir(sys.argv[4] + "/interpolated"):
    os.system("mkdir " + sys.argv[4] + "/interpolated")
  var = []
  title = []
  ytitle = []
  ytitlefft = []
  var.append(Cathode_V)
  var.append(Cathode_I)
  title.append("CathodeV")
  title.append("Cathode_I")
  ytitle.append("Voltage [kV]")
  ytitle.append("Current [uA]")
  ytitlefft.append("kV.s")
  ytitlefft.append("uA.s")
  a = Interpolate(time, date, var, title, ytitle, ytitlefft, "./" + sys.argv[4] + "/interpolated/", tmin, tmax)  

###################### LEMs leackages currents
plot_LEMs = True
for i in range(0,len(LEM_Down_V)):
  if LEM_Down_V[i][0] == "ignore" or LEM_Down_I[i][0] == "ignore" or LEM_Up_V[i][0] == "ignore" or LEM_Up_I[i][0] == "ignore":
    plot_LEMs = False

if plot_LEMs == True and Hall_T[0] != "":
  if not os.path.isdir(sys.argv[4] + "/leackage"):
    os.system("mkdir " + sys.argv[4] + "/leackage")
  path = "./" + sys.argv[4] + "/leackage/"
  title = "all_LEMs_leackage"
  a = plot_all_LEMs_leackage(time, date, LEM_Up_I, LEM_Down_I, 0.01, Hall_T, path, title, tmin, tmax)

###################### LEMs + grid
if GRID_1_V[0] != "ignore" and GRID_1_I[0] != "ignore":
  for i in range(0,len(LEM_Down_V)):
    if LEM_Down_V[i][0] != "ignore" and LEM_Down_I[i][0] != "ignore" and LEM_Up_V[i][0] != "ignore" and LEM_Up_I[i][0] != "ignore":
      if not os.path.isdir(sys.argv[4] + "/LEM_GRID"):
        os.system("mkdir " + sys.argv[4] + "/LEM_GRID")
      title = "LEM_%i" %(i+1)
      a = plot_LEM_GRID(time, date, GRID_1_V, GRID_1_I, LEM_Down_V[i], LEM_Down_I[i], LEM_Up_V[i], LEM_Up_I[i], tmin, tmax, title)

###################### LEMs alone
for i in range(0,12):
  if LEM_Up_I[i][0] != "ignore" and LEM_Down_I[i][0] != "ignore" and Hall_T[0] != "ignore":
    title = "LEM_%i_" %(i+1)
    if not os.path.isdir(sys.argv[4] + "/LEMs"):
      os.system("mkdir " + sys.argv[4] + "/LEMs")
    a = plot_single_LEM(time, date, LEM_Up_I[i], LEM_Down_I[i], Hall_T, title, tmin, tmax)

###################### Heinzinger
if Cathode_V[0] != "ignore" and Cathode_I[0] != "ignore":
  if not os.path.isdir(sys.argv[4] + "/Cathode"):
    os.system("mkdir " + sys.argv[4] + "/Cathode")
  a = plot_V_I(time, date, Cathode_V, Cathode_I, "cathode", "./" + sys.argv[4] + "/Cathode/", tmin, tmax)
  
###################### Grid
if GRID_1_V[0] != "ignore" and GRID_1_I[0] != "ignore":
  if not os.path.isdir(sys.argv[4] + "/Grid"):
    os.system("mkdir " + sys.argv[4] + "/Grid")
  a = plot_V_I(time, date, GRID_1_V, GRID_1_I, "Grid", "./" + sys.argv[4] + "/Grid/", tmin, tmax)

###################### all V and I    
plot_LV = True
for i in range(0,len(levelmeters)):
  if levelmeters[i][0] == "ignore":
    plot_LV = False
    
if GRID_1_V[0] != "ignore" and GRID_1_I[0] != "ignore" and plot_LEMs == True:
  if not os.path.isdir(sys.argv[4] + "/all_V_I"):
    os.system("mkdir " + sys.argv[4] + "/all_V_I")
  a = plot_all_LEMs_V_I(time, date, LEM_Up_V, LEM_Up_I, LEM_Down_V, LEM_Down_I, GRID_1_V, tmin, tmax)
  if Cathode_V[0] != "ignore" and Cathode_I[0] != "ignore" and plot_LV == True:
    a = plot_all_V_I(time, date, Cathode_V, Cathode_I, GRID_1_V, GRID_1_I, LEM_Up_V, LEM_Up_I, LEM_Down_V, LEM_Down_I, levelmeters[6], tmin, tmax)


###################### LevelMeters
if plot_LV == True:
  if not os.path.isdir(sys.argv[4] + "/LevelMeters"):
    os.system("mkdir " + sys.argv[4] + "/LevelMeters")
  a = plot_LM(time, date, levelmeters, "levelmeters", tmin, tmax)
  a = Plot_LM_RMS(time, date, levelmeters, "levelmeters_RMS", tmin, tmax)
  a = plot_LM_Delta(time, date, levelmeters, 8, "levelmeters_delta_8", tmin, tmax)

###################### Box
#if not os.path.isdir(sys.argv[4] + "/Box"):
  #os.system("mkdir " + sys.argv[4] + "/Box")
  
#a = plot_Box(time, date, Box_1_1, levelmeters[6], "LV_1", "LV_7", tmin, tmax, "LEM_1")
#a = plot_Box(time, date, Box_1_3, levelmeters[6], "LV_1", "LV_7", tmin, tmax, "LEM_3")
#a = plot_Box(time, date, Box_2, levelmeters[6], "LV_2", "LV_7", tmin, tmax, "LEM_2")
#a = plot_Box(time, date, Box_3_5, levelmeters[6], "LV_3", "LV_7", tmin, tmax, "LEM_5")
#a = plot_Box(time, date, Box_3_6, levelmeters[6], "LV_3", "LV_7", tmin, tmax, "LEM_6")
#a = plot_Box(time, date, Box_5_10, levelmeters[6], "LV_5", "LV_7", tmin, tmax, "LEM_10")
#a = plot_Box(time, date, Box_5_12, levelmeters[6], "LV_5", "LV_7", tmin, tmax, "LEM_12")
#a = plot_Box(time, date, Box_6_11, levelmeters[6], "LV_6", "LV_7", tmin, tmax, "LEM_11")
#a = plot_Box(time, date, Box_6_12, levelmeters[6], "LV_6", "LV_7", tmin, tmax, "LEM_12")
#a = plot_Box(time, date, Box_7_7, levelmeters[6], "LV_7", "LV_7", tmin, tmax, "LEM_7")
#a = plot_Box(time, date, Box_7_8, levelmeters[6], "LV_7", "LV_7", tmin, tmax, "LEM_8")
#a = plot_Box(time, date, Box_8, levelmeters[6], "LV_8", "LV_7", tmin, tmax, "LEM_4")

###################### Trips
#if not os.path.isdir(sys.argv[4] + "/Trips"):
  #os.system("mkdir " + sys.argv[4] + "/Trips")
  
#a = Trips(time, date, GRID_1_V, LEM_Down_V[0], levelmeters, "trips_vs_LV_LEM_1", tmin, tmax)

exit(0)
