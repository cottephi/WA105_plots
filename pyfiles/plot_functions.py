#!/usr/bin/python
import math,numpy,pickle,time,argparse, os,errno,re,sys, datetime, scipy.optimize
from scipy.interpolate import interp1d
sys.path.append("../../root-6.09.02/")
import ROOT
import scipy.fftpack
from array import array
import matplotlib.pyplot as plt
from time import gmtime, strftime
#import table

def unix_to_date(date):
    "converts unix timestamp (int) to date string ('Y-m-d H:M:S')"
    return datetime.datetime.fromtimestamp(date).strftime('%Y-%m-%d %H:%M:%S')

def date_to_unix(unix):
    "converts date string ('Y-m-d H:M:S') to unix timestamp (int)"
    return int(datetime.datetime.strptime(unix, '%Y-%m-%d %H:%M:%S').strftime("%s"))
    
def Interpolate(time, date, const_var, title, ytitle, ytitlefft, path, tmin = 0, tmax = 1):

  if((tmin == 0) & (tmax == 1)):
    tmin = time[0]
    tmax = tmin + time[len(time) - 1]

  zoom = time[(time >= tmin) & (time <= tmax)]

  if len(const_var) != len(title) or len(const_var) != len(ytitle) or len(title) != len(ytitle):
    print("ERROR: variable, title and ytitle must have the same length")
    return 1
    
  for i in range(0,len(const_var)):
    var = const_var[i][(time >= tmin) & (time <= tmax)]
    if title[i] == "GridV":
      var = var / 1000
    inter_var = interp1d(zoom,var)
    evenly_spaced_time = numpy.arange(zoom[0],zoom[-1],1)
    function_to_fft = inter_var(evenly_spaced_time)
    fft_var = numpy.fft.fft(function_to_fft)
    freq_var = numpy.array(numpy.fft.fftfreq(fft_var.shape[-1]))
    fft_var = numpy.array(fft_var.real)
    c1 = ROOT.TCanvas("c1", "dit", 2000, 1200)
    leg = ROOT.TLegend(0.3,0,0.7,0.08)
    leg.SetNColumns(2)
    
    top_pad = ROOT.TPad("top_pad", "top_pad",0,0.45, 1.0, 0.9)
    top_pad.Draw()
    top_pad.cd()
    top_pad.SetTopMargin(0.2)
    top_pad.SetBottomMargin(0.1)
    top_pad.SetGrid()
    
    gr1 = ROOT.TGraph(len(zoom), zoom, var)
    gr1.Draw("AL")
    gr1.SetTitle(title[i] + " FFT")
    gr1.SetLineWidth(1)
    gr1.SetLineColor(ROOT.kRed)
    gr1.GetXaxis().SetTimeDisplay(1)
    gr1.GetXaxis().SetTimeFormat("%H: %M %F1970-01-01 00:00:00")
    gr1.GetXaxis().SetLimits(zoom[0], zoom[-1])
    gr1.GetXaxis().SetNdivisions(10,4,0,ROOT.kFALSE)
    gr1.GetXaxis().SetLabelSize(gr1.GetXaxis().GetTitleSize()*2)
    gr1.GetYaxis().SetTitleOffset(0.6)
    gr1.GetYaxis().SetLabelSize(gr1.GetYaxis().GetTitleSize()*2)
    gr1.GetYaxis().SetTitle(ytitle[i])
    gr1.GetYaxis().SetTitleSize(gr1.GetYaxis().GetTitleSize()*2.5)
    leg.AddEntry(gr1,title[i],"l")
    c1.cd()

    bottom_pad = ROOT.TPad("bottom_pad", "bottom_pad",0,0.09, 1.0, 0.45)
    bottom_pad.Draw()
    bottom_pad.cd()
    bottom_pad.SetTopMargin(0.05)
    bottom_pad.SetBottomMargin(0.2)
    bottom_pad.SetGrid()

    gr2 = ROOT.TGraph(len(freq_var), freq_var, fft_var)
    gr2.Draw("AL")
    gr2.SetTitle("")
    gr2.SetLineWidth(1)
    gr2.SetLineColor(ROOT.kBlue)
    gr2.GetYaxis().SetRangeUser(-200,200)
    #gr2.GetYaxis().SetRangeUser(-gr2.GetYaxis().GetXmax()/200,gr2.GetYaxis().GetXmax()/200)
    gr2.GetXaxis().SetTitle("Frequency [Hz]")    
    gr2.GetXaxis().SetLabelSize(0.08)
    gr2.GetXaxis().SetRangeUser(0,gr2.GetXaxis().GetXmax())
    gr2.GetXaxis().SetTitleSize(gr2.GetXaxis().GetTitleSize()*2.5)
    gr2.GetYaxis().SetTitleOffset(0.6)
    gr2.GetYaxis().SetLabelSize(0.08)
    gr2.GetYaxis().SetTitle(ytitlefft[i])
    gr2.GetYaxis().SetTitleSize(gr2.GetYaxis().GetTitleSize()*2.5)
    leg.AddEntry(gr2,"Frequency " + title[i],"l")
    c1.cd()
    
    leg.Draw()
    c1.SetLeftMargin(0.1)
    c1.SaveAs(path + title[i] + "_" + date + ".pdf")
    c1.SaveAs(path + title[i] + "_" + date + ".root")
    c1.Close()
    
  return 0
  
def plot_temperatures(time, date, const_temperatures, title, path, tmin = 0, tmax = 1):

  is_list = isinstance(const_temperatures,list)
  if((tmin == 0) & (tmax == 1)):
    tmin = time[0]
    tmax = tmin + time[len(time) - 1]
    
  zoom = time[(time >= tmin) & (time <= tmax)]
  if is_list == True:
  
    temperatures = []
    
    for i in range(0,len(const_temperatures)):
      temperatures.append(const_temperatures[i][(time >= tmin) & (time <= tmax)])
  else:
    
    temperatures = const_temperatures[(time >= tmin) & (time <= tmax)]
  
  c1 = ROOT.TCanvas("c1", "dit", 2000, 1200)
  c1.SetBottomMargin(0.15)
  
  if is_list == True:
  
    leg = ROOT.TLegend(0,0,1,0.08)
    leg.SetNColumns(6)
    col = [ROOT.kBlack, ROOT.kCyan, ROOT.kBlue, ROOT.kRed, ROOT.kGreen, ROOT.kYellow, ROOT.kYellow+2, ROOT.kMagenta, ROOT.kGreen+2, ROOT.kGray, ROOT.kPink+2, ROOT.kMagenta+2]
  
    mgrT = ROOT.TMultiGraph()
    grmT = [ ROOT.TGraph(len(zoom), zoom, temp) for temp in temperatures ]
    maxT = -1000
    minT = 1000
    
    for i, grT, color in zip(range(0,len(temperatures)), grmT, col):

      if maxT < max(temperatures[i]):
        maxT = max(temperatures[i])
        
      if minT > min(temperatures[i]):
        minT = min(temperatures[i])
        
      grT.SetLineWidth(3)
      grT.SetLineColor(color)
      leg.AddEntry(grT,"Chain 2 T%i" %(i+1), "l")
      mgrT.Add(grT)
    mgrT.Draw("AL")
    mgrT.SetTitle(title + "_" + date)
    mgrT.GetYaxis().SetLabelSize(0.04)
    #mgrT.SetMinimum(0)
    #mgrT.SetMaximum(maxT*1.1)
    mgrT.GetXaxis().SetTitle("")
    mgrT.GetXaxis().SetTimeDisplay(1)
    mgrT.GetXaxis().SetTimeFormat("%H: %M %F1970-01-01 00:00:00")
    #mgrT.GetXaxis().SetLabelSize(0)
    mgrT.GetXaxis().SetNdivisions(10,4,0,ROOT.kFALSE)
    mgrT.GetXaxis().SetLimits(zoom[0], zoom[-1])
    mgrT.GetYaxis().SetTitle("Temperature [K]")
    mgrT.GetYaxis().SetTitleOffset(0.5)
    mgrT.GetYaxis().SetTitleSize(mgrT.GetYaxis().GetTitleSize()*2.5)
    
  else:
  
    leg = ROOT.TLegend(0.3,0,0.7,0.08)
    grT = ROOT.TGraph(len(zoom), zoom, temperatures)
    maxT = max(temperatures)
    minT = min(temperatures)
    grT.SetLineWidth(3)
    grT.SetLineColor(ROOT.kRed)
    leg.AddEntry(grT,title, "l")
    grT.Draw("AL")
    grT.SetTitle(title + "_" + date)
    grT.GetYaxis().SetLabelSize(0.04)
    #grT.SetMinimum(0)
    #grT.SetMaximum(maxT*1.1)
    grT.GetXaxis().SetTitle("")
    grT.GetXaxis().SetTimeDisplay(1)
    grT.GetXaxis().SetTimeFormat("%H: %M %F1970-01-01 00:00:00")
    #grT.GetXaxis().SetLabelSize(0)
    grT.GetXaxis().SetNdivisions(10,4,0,ROOT.kFALSE)
    grT.GetXaxis().SetLimits(zoom[0], zoom[-1])
    grT.GetYaxis().SetTitle("Temperature [K]")
    grT.GetYaxis().SetTitleOffset(0.5)
    grT.GetYaxis().SetTitleSize(grT.GetYaxis().GetTitleSize()*2.5)
    
    
  leg.SetTextSize(leg.GetTextSize()*0.2)
  leg.Draw()
  c1.SetLeftMargin(0.1)
  c1.SaveAs(path + title + "_" + date +  ".pdf")
  c1.SaveAs(path + title + "_" + date + ".root")
  c1.Close()
  
  return 0
    
def plot_pressures(time, date, const_pressures, title, path, tmin = 0, tmax = 1):

  is_list = isinstance(const_pressures,list)
  if((tmin == 0) & (tmax == 1)):
    tmin = time[0]
    tmax = tmin + time[len(time) - 1]
    
  zoom = time[(time >= tmin) & (time <= tmax)]
  if is_list == True:
    pressures = []
    for i in range(0,len(const_pressures)):
      pressures.append(const_pressures[i][(time >= tmin) & (time <= tmax)])
  else:
    pressures = const_pressures[(time >= tmin) & (time <= tmax)]
  
  c1 = ROOT.TCanvas("c1", "dit", 2000, 1200)
  c1.SetBottomMargin(0.15)
  
  if is_list == True:
  
    leg = ROOT.TLegend(0,0,1,0.08)
    leg.SetNColumns(6)
    col = [ROOT.kBlack, ROOT.kCyan, ROOT.kBlue, ROOT.kRed, ROOT.kGreen, ROOT.kYellow, ROOT.kYellow+2, ROOT.kMagenta, ROOT.kGreen+2, ROOT.kGray, ROOT.kPink+2, ROOT.kMagenta+2]
  
    mgrT = ROOT.TMultiGraph()
    grmT = [ ROOT.TGraph(len(zoom), zoom, temp) for temp in pressures ]
    maxT = -1000
    minT = 1000
    
    for i, grT, color in zip(range(0,len(pressures)), grmT, col):

      if maxT < max(pressures[i]):
        maxT = max(pressures[i])
        
      if minT > min(pressures[i]):
        minT = min(pressures[i])
        
      grT.SetLineWidth(3)
      grT.SetLineColor(color)
      leg.AddEntry(grT,"Chain 2 T%i" %(i+1), "l")
      mgrT.Add(grT)
    mgrT.Draw("AL")
    mgrT.SetTitle(title + "_" + date)
    mgrT.GetYaxis().SetLabelSize(0.04)
    #mgrT.SetMinimum(0)
    #mgrT.SetMaximum(maxT*1.1)
    mgrT.GetXaxis().SetTitle("")
    mgrT.GetXaxis().SetTimeDisplay(1)
    mgrT.GetXaxis().SetTimeFormat("%H: %M %F1970-01-01 00:00:00")
    #mgrT.GetXaxis().SetLabelSize(0)
    mgrT.GetXaxis().SetNdivisions(10,4,0,ROOT.kFALSE)
    mgrT.GetXaxis().SetLimits(zoom[0], zoom[-1])
    mgrT.GetYaxis().SetTitle("Pressure [mBar]")
    mgrT.GetYaxis().SetTitleOffset(0.5)
    mgrT.GetYaxis().SetTitleSize(mgrT.GetYaxis().GetTitleSize()*2.5)
    
  else:
  
    leg = ROOT.TLegend(0.3,0,0.7,0.08)
    grT = ROOT.TGraph(len(zoom), zoom, pressures)
    maxT = max(pressures)
    minT = min(pressures)
    grT.SetLineWidth(3)
    grT.SetLineColor(ROOT.kRed)
    leg.AddEntry(grT,title, "l")
    grT.Draw("AL")
    grT.SetTitle(title + "_" + date)
    grT.GetYaxis().SetLabelSize(0.04)
    #grT.SetMinimum(0)
    #grT.SetMaximum(maxT*1.1)
    grT.GetXaxis().SetTitle("")
    grT.GetXaxis().SetTimeDisplay(1)
    grT.GetXaxis().SetTimeFormat("%H: %M %F1970-01-01 00:00:00")
    #grT.GetXaxis().SetLabelSize(0)
    grT.GetXaxis().SetNdivisions(10,4,0,ROOT.kFALSE)
    grT.GetXaxis().SetLimits(zoom[0], zoom[-1])
    grT.GetYaxis().SetTitle("Pressure [mBar]")
    grT.GetYaxis().SetTitleOffset(0.5)
    grT.GetYaxis().SetTitleSize(grT.GetYaxis().GetTitleSize()*2.5)
    
    
  leg.SetTextSize(leg.GetTextSize()*0.2)
  leg.Draw()
  c1.SetLeftMargin(0.1)
  c1.SaveAs(path + title + "_" + date +  ".pdf")
  c1.SaveAs(path + title + "_" + date + ".root")
  c1.Close()
  
  return 0
    
    
def plot_V_I(time, date, const_voltage, const_current, title, path, tmin = 0, tmax = 1):
  if((tmin == 0) & (tmax == 1)):
    tmin = time[0]
    tmax = tmin + time[len(time) - 1]

  zoom = time[(time >= tmin) & (time <= tmax)]
  voltage = const_voltage[(time >= tmin) & (time <= tmax)]
  current = const_current[(time >= tmin) & (time <= tmax)]
  if title == "Grid":
    voltage = voltage / 1000

  c1 = ROOT.TCanvas("c1", "dit", 2000, 1200)
  leg = ROOT.TLegend(0.3,0,0.7,0.08)
  leg.SetNColumns(2)

  pad1 = ROOT.TPad("pad1", "", 0, 0, 1, 1)
  gr1 = ROOT.TGraph(len(zoom), zoom, voltage)
  pad1.Draw()
  pad1.cd()
  pad1.SetGrid()
  pad1.SetBottomMargin(0.15)
  gr1.Draw("AL")
  if min(voltage) >= 0:
    gr1.SetMinimum(min(voltage)*0.99)
  else:
    gr1.SetMinimum(min(voltage)*1.01)
  gr1.SetLineWidth(3)
  if max(voltage) >= 0:
    gr1.SetMaximum(max(voltage)*1.01)
  else:
    gr1.SetMaximum(max(voltage)*0.99)
  gr1.SetLineColor(ROOT.kRed)
  gr1.SetTitle("")
  leg.AddEntry(gr1," Voltage","l")
  gr1.GetXaxis().SetTimeDisplay(1)
  gr1.GetXaxis().SetTimeFormat("%H: %M %F1970-01-01 00:00:00")
  gr1.GetXaxis().SetLabelSize(0.035)
  gr1.GetXaxis().SetTitle("")
  gr1.GetXaxis().SetNdivisions(10,4,0,ROOT.kFALSE)
  gr1.GetYaxis().SetTitle("Voltage [kV]")
  c1.cd()

  pad2 = ROOT.TPad("pad2", "", 0, 0, 1, 1)
  pad2.Draw()
  pad2.cd()
  pad2.SetFillStyle(4000)
  pad2.SetFrameFillStyle(0)
  pad2.SetBottomMargin(0.15)
  gr2 = ROOT.TGraph(len(zoom), zoom, current)
  gr2.Draw("ALY+")
  gr2.SetMinimum(0)
  gr2.SetLineWidth(2)
  gr2.SetMaximum(max(current)*1.2)
  gr2.SetLineColorAlpha(ROOT.kBlue, 0.35)
  gr2.SetTitle(title + "_" + date)
  leg.AddEntry(gr2," Current","l")
  gr2.GetXaxis().SetLabelSize(0)
  gr2.GetXaxis().SetTickSize(0)  
  gr2.GetXaxis().SetNdivisions(10,4,0,ROOT.kFALSE)
  gr2.GetYaxis().SetTitle("Current [uA]")
  c1.cd()

  leg.Draw()
  c1.SetLeftMargin(0.1)
  c1.SaveAs(path + title + "_" + date + ".pdf")
  c1.SaveAs(path + title + "_" + date + ".root")
  ######################################## vs VGrid
  c1.Close()
  
  return 0

##############################################################################################
# LEM currents up and down (one plot per LEM)
##############################################################################################

def plot_single_LEM(time, date, const_LEMI_up, const_LEMI_down, const_temperature, legend, tmin = 0, tmax = 1):
  
  title = legend
  path = "./" + sys.argv[4] + "/LEMs/"
  
  if((tmin == 0) & (tmax == 1)):
    tmin = time[0]
    tmax = tmin + time[len(time) - 1]

  zoom = time[(time >= tmin) & (time <= tmax)]
  LEMI_up = const_LEMI_up[(time >= tmin) & (time <= tmax)]
  LEMI_down = const_LEMI_down[(time >= tmin) & (time <= tmax)]
  temperature = const_temperature[(time >= tmin) & (time <= tmax)]

  c1 = ROOT.TCanvas("c1", "dit", 2000, 1200)
  leg = ROOT.TLegend(0.3,0,0.7,0.08)
  leg.SetNColumns(3)

  top_padLU = ROOT.TPad("top_padLU", "top_padLU",0,0.55, 1.0, 1.0)
  top_padLU.Draw()
  top_padLU.cd()
  top_padLU.SetTopMargin(0.2)
  top_padLU.SetBottomMargin(0.05)
  top_padLU.SetGrid()

  gr1 = ROOT.TGraph(len(zoom), zoom, LEMI_up)
  gr1.Draw("AL")
  if min(LEMI_up) >= 0:
    gr1.SetMinimum(min(LEMI_up)*0.99)
  else:
    gr1.SetMinimum(min(LEMI_up)*1.01)
  if max(LEMI_up) >= 0:
    gr1.SetMaximum(max(LEMI_up)*1.01)
  else:
    gr1.SetMaximum(max(LEMI_up)*0.99)  
  gr1.SetTitle(title)
  gr1.SetLineWidth(1)
  gr1.SetLineColor(ROOT.kBlue)
  gr1.GetXaxis().SetLabelSize(0)
  gr1.GetXaxis().SetTimeDisplay(1)
  gr1.GetXaxis().SetTimeFormat("%H: %M %F1970-01-01 00:00:00")
  gr1.GetXaxis().SetLimits(zoom[0], zoom[-1])
  gr1.GetXaxis().SetNdivisions(10,4,0,ROOT.kFALSE)
  gr1.GetYaxis().SetTitleOffset(0.6)
  gr1.GetYaxis().SetLabelSize(0.08)
  gr1.GetYaxis().SetTitle("Current [uA]")
  gr1.GetYaxis().SetTitleSize(gr1.GetYaxis().GetTitleSize()*2.5)
  leg.AddEntry(gr1,"LEM up","l")
  c1.cd()

  bottom_padLU = ROOT.TPad("bottom_padLU", "bottom_padLU",0,0.1, 1.0, 0.55)
  bottom_padLU.Draw()
  bottom_padLU.cd()
  bottom_padLU.SetTopMargin(0.05)
  bottom_padLU.SetBottomMargin(0.2)
  bottom_padLU.SetGrid()

  gr2 = ROOT.TGraph(len(zoom), zoom, LEMI_down)
  gr2.Draw("AL")
  if min(LEMI_down) >= 0:
    gr2.SetMinimum(min(LEMI_down)*0.99)
  else:
    gr2.SetMinimum(min(LEMI_down)*1.01)
  if max(LEMI_down) >= 0:
    gr2.SetMaximum(max(LEMI_down)*1.01)
  else:
    gr2.SetMaximum(max(LEMI_down)*0.99) 
  gr2.SetTitle("")
  gr2.SetLineWidth(1)
  gr2.SetLineColor(ROOT.kRed)
  gr2.GetXaxis().SetLabelSize(0.08)
  gr2.GetXaxis().SetTimeDisplay(1)
  gr2.GetXaxis().SetTimeFormat("%H: %M %F1970-01-01 00:00:00")
  gr2.GetXaxis().SetLimits(zoom[0], zoom[-1])
  gr2.GetXaxis().SetNdivisions(10,4,0,ROOT.kFALSE)
  gr2.GetYaxis().SetTitleOffset(0.6)
  gr2.GetYaxis().SetLabelSize(0.08)
  gr2.GetYaxis().SetTitle("Current [uA]")
  gr2.GetYaxis().SetTitleSize(gr2.GetYaxis().GetTitleSize()*2.5)
  leg.AddEntry(gr2,"LEM down","l")
  c1.cd()

  bottom2_padLU = ROOT.TPad("bottom2_padLU", "bottom_padLU",0,0.1, 1.0, 0.55)
  bottom2_padLU.Draw()
  bottom2_padLU.cd()
  bottom2_padLU.SetFillStyle(4000)
  bottom2_padLU.SetFillColor(0)
  bottom2_padLU.SetFrameFillStyle(4000)
  bottom2_padLU.SetTopMargin(0.05)
  bottom2_padLU.SetBottomMargin(0.2)

  gr3 = ROOT.TGraph(len(zoom), zoom, temperature)
  gr3.Draw("ALY+")
  if min(temperature) >= 0:
    gr3.SetMinimum(min(temperature)*0.99)
  else:
    gr3.SetMinimum(min(temperature)*1.01)
  if max(LEMI_down) >= 0:
    gr3.SetMaximum(max(temperature)*1.01)
  else:
    gr3.SetMaximum(max(temperature)*0.99)
  gr3.SetTitle("")
  gr3.SetLineWidth(1)
  gr3.SetLineColor(ROOT.kGreen+2)
  gr3.GetXaxis().SetLabelSize(0.08)
  gr3.GetXaxis().SetTimeDisplay(1)
  gr3.GetXaxis().SetTimeFormat("%H: %M %F1970-01-01 00:00:00")
  gr3.GetXaxis().SetLimits(zoom[0], zoom[-1])
  gr3.GetXaxis().SetNdivisions(10,4,0,ROOT.kFALSE)
  gr3.GetYaxis().SetTitleOffset(0.6)
  gr3.GetYaxis().SetLabelSize(0.08)
  gr3.GetYaxis().SetTitle("Temperature [K]")
  gr3.GetYaxis().SetTitleSize(gr3.GetYaxis().GetTitleSize()*2.5)
  leg.AddEntry(gr3,"Hall temperature","l")
  c1.cd()

  leg.SetTextSize(leg.GetTextSize()*0.2)
  leg.Draw()
  c1.SetLeftMargin(0.1)
  c1.SaveAs(path + title + "_" + date +  ".pdf")
  c1.SaveAs(path + title + "_" + date + ".root")
  c1.Close()

  return 0 


##############################################################################################
# All voltages and currents over time
##############################################################################################

def plot_all_LEMs_V_I(time, date, const_LEMsV_up, const_LEMsI_up, const_LEMsV_down, const_LEMsI_down, const_gridV, tmin = 0, tmax = 1):

  title = "All_LEMs"
  path = "./" + sys.argv[4] + "/all_V_I/"
  
  if((tmin == 0) & (tmax == 1)):
    tmin = time[0]
    tmax = tmin + time[len(time) - 1]

  zoom = time[(time >= tmin) & (time <= tmax)]
  LEMsI_up = []
  LEMsV_up = []
  LEMsI_down = []
  LEMsV_down = []  
  for i in range(0,len(const_LEMsI_up)):
    LEMsI_up.append(const_LEMsI_up[i][(time >= tmin) & (time <= tmax)])
  for i in range(0,len(const_LEMsV_up)):
    LEMsV_up.append(const_LEMsV_up[i][(time >= tmin) & (time <= tmax)])
  for i in range(0,len(const_LEMsI_down)):
    LEMsI_down.append(const_LEMsI_down[i][(time >= tmin) & (time <= tmax)])
  for i in range(0,len(const_LEMsV_down)):
    LEMsV_down.append(const_LEMsV_down[i][(time >= tmin) & (time <= tmax)] / 1000)
  gridV = const_gridV[(time >= tmin) & (time <= tmax)] / 1000

  col = [ROOT.kBlack, ROOT.kCyan, ROOT.kBlue, ROOT.kRed, ROOT.kGreen, ROOT.kYellow, ROOT.kYellow+2, ROOT.kMagenta, ROOT.kGreen+2, ROOT.kGray, ROOT.kPink+2, ROOT.kMagenta+2]

  max_VU = -10000
  max_VD = -10000
  
  cLU = ROOT.TCanvas("cLU","cLU",2000,1200)
  leg = ROOT.TLegend(0,0,1,0.1)
  leg.SetNColumns(7)
  
  top_padLU = ROOT.TPad("top_padLU", "top_padLU",0,0.55, 1.0, 1.0)
  top_padLU.Draw()
  top_padLU.cd()
  top_padLU.SetTopMargin(0.2)
  top_padLU.SetBottomMargin(0.05)
  top_padLU.SetGrid()
  mgrV_up = ROOT.TMultiGraph()
  grmV_up = [ ROOT.TGraph(len(zoom), zoom, lemsV_UP) for lemsV_UP in LEMsV_up ]
  for i, grV_up, color in zip(range(0,len(LEMsV_up)), grmV_up, col):
    if max_VU < max(LEMsV_up[i]):
      max_VU = max(LEMsV_up[i])
    grV_up.SetLineWidth(3)
    grV_up.SetLineColor(color)
    leg.AddEntry(grV_up,"LEM %i" %(i+1), "l")
    mgrV_up.Add(grV_up)
  mgrV_up.Draw("AL")
  mgrV_up.SetTitle(title + "_" + date)
  mgrV_up.GetYaxis().SetLabelSize(0.07)
  mgrV_up.SetMinimum(0)
  mgrV_up.SetMaximum(max_VU*1.1)
  mgrV_up.GetXaxis().SetTitle("")
  mgrV_up.GetXaxis().SetTimeDisplay(1)
  mgrV_up.GetXaxis().SetTimeFormat("%H: %M %F1970-01-01 00:00:00")
  mgrV_up.GetXaxis().SetLabelSize(0)
  mgrV_up.GetXaxis().SetNdivisions(10,4,0,ROOT.kFALSE)
  mgrV_up.GetXaxis().SetLimits(zoom[0], zoom[-1])
  mgrV_up.GetYaxis().SetTitle("Voltage [V]")
  mgrV_up.GetYaxis().SetTitleOffset(0.5)
  mgrV_up.GetYaxis().SetTitleSize(mgrV_up.GetYaxis().GetTitleSize()*2.5)
  cLU.cd()
  
  bottom_padLU = ROOT.TPad("bottom_padLU", "bottom_padLU",0,0.1, 1.0, 0.55)
  bottom_padLU.Draw()
  bottom_padLU.cd()
  bottom_padLU.SetTopMargin(0.05)
  bottom_padLU.SetBottomMargin(0.2)
  bottom_padLU.SetGrid()
  mgrV_down = ROOT.TMultiGraph()
  grmV_down = [ ROOT.TGraph(len(zoom), zoom, lemsV_DOWN) for lemsV_DOWN in LEMsV_down ]
  for i, grV_down, color in zip(range(0,len(LEMsV_down)), grmV_down, col):
    if max_VD < max(LEMsV_down[i]):
      max_VD = max(LEMsV_down[i])
    grV_down.SetLineWidth(3)
    grV_down.SetLineColor(color)
    mgrV_down.Add(grV_down)
  mgrV_down.Draw("AL")
  mgrV_down.SetTitle("")
  mgrV_down.GetYaxis().SetLabelSize(0.07)
  mgrV_down.SetMinimum(0)
  mgrV_down.SetMaximum(max(gridV)*1.1)
  mgrV_down.GetXaxis().SetTimeDisplay(1)
  mgrV_down.GetXaxis().SetTimeFormat("%H: %M %F1970-01-01 00:00:00")
  mgrV_down.GetXaxis().SetTitle("")
  mgrV_down.GetXaxis().SetLimits(zoom[0], zoom[-1])
  mgrV_down.GetXaxis().SetLabelSize(0.08)
  mgrV_down.GetXaxis().SetLabelOffset(0.05)
  mgrV_down.GetXaxis().SetNdivisions(10,4,0,ROOT.kFALSE)
  mgrV_down.GetYaxis().SetTitle("Voltage [kV]")
  mgrV_down.GetYaxis().SetTitleOffset(0.5)
  mgrV_down.GetYaxis().SetTitleSize(mgrV_down.GetYaxis().GetTitleSize()*2.5)
  cLU.cd()

  bottom_pady1 = ROOT.TPad("bottom_pady1", "bottom_pady1",0,0.1, 1.0, 0.55)
  bottom_pady1.Draw()
  bottom_pady1.cd()
  bottom_pady1.SetFillStyle(4000)
  bottom_pady1.SetFillColor(0)
  bottom_pady1.SetFrameFillStyle(4000)
  bottom_pady1.SetTopMargin(0.05)
  bottom_pady1.SetBottomMargin(0.2)
  bottom_pady1.SetGridx(1)
  gr_gridV = ROOT.TGraph(len(zoom), zoom, gridV)
  gr_gridV.Draw("AL")
  gr_gridV.SetMinimum(0)
  gr_gridV.SetMaximum(max(gridV)*1.1)  
  gr_gridV.SetTitle("")
  gr_gridV.SetLineWidth(3)
  gr_gridV.SetLineColor(ROOT.kOrange-6)
  gr_gridV.GetXaxis().SetLabelSize(0)
  gr_gridV.GetXaxis().SetTimeDisplay(1)
  gr_gridV.GetXaxis().SetTimeFormat("%H: %M %F1970-01-01 00:00:00")
  gr_gridV.GetXaxis().SetLimits(zoom[0], zoom[-1])
  gr_gridV.GetXaxis().SetNdivisions(10,4,0,ROOT.kFALSE)
  gr_gridV.GetYaxis().SetTitleOffset(0.6)
  gr_gridV.GetYaxis().SetLabelSize(0)
  gr_gridV.GetYaxis().SetTitle("")
  gr_gridV.GetYaxis().SetTitleSize(gr_gridV.GetYaxis().GetTitleSize()*2.5)
  leg.AddEntry(gr_gridV,"Grid Voltage","l")
  cLU.cd()

  leg.SetTextSize(leg.GetTextSize()*0.2)
  leg.Draw()
  cLU.SetLeftMargin(0.1)
  cLU.SaveAs(path + title + "_" + date +  ".pdf")
  cLU.SaveAs(path + title + "_" + date + ".root")
  cLU.Close()

  title = "All_LEMs_Down"
  
  max_VD = -10000
  max_ID = -10000
  
  cLD = ROOT.TCanvas("cLD","cLD",2000,1200)
  leg = ROOT.TLegend(0,0,1,0.1)
  leg.SetNColumns(6)
  
  top_padLD = ROOT.TPad("top_padLD", "top_padLD",0,0.5, 1.0, 1.0)
  top_padLD.Draw()
  top_padLD.cd()
  top_padLD.SetTopMargin(0.2)
  top_padLD.SetBottomMargin(0.01)
  top_padLD.SetGrid()
  mgrV_down = ROOT.TMultiGraph()
  grmV_down = [ ROOT.TGraph(len(zoom), zoom, lemsV_DOWN) for lemsV_DOWN in LEMsV_down ]
  for i, grV_down, color in zip(range(0,len(LEMsV_down)), grmV_down, col):
    if max_VD < max(LEMsV_down[i]):
      max_VD = max(LEMsV_down[i])
    grV_down.SetLineWidth(3)
    grV_down.SetLineColor(color)
    leg.AddEntry(grV_down,"LEM %i" %(i+1), "l")
    mgrV_down.Add(grV_down)
  mgrV_down.Draw("AL")
  mgrV_down.SetTitle(title + "_" + date)
  mgrV_down.GetYaxis().SetLabelSize(0.1)
  mgrV_down.SetMinimum(0)
  mgrV_down.SetMaximum(max_VD*1.1)
  mgrV_down.GetXaxis().SetTitle("")
  mgrV_down.GetXaxis().SetLabelSize(0)
  mgrV_down.GetXaxis().SetNdivisions(10,4,0,ROOT.kFALSE)
  mgrV_down.GetYaxis().SetTitle("Voltage [kV]")
  mgrV_down.GetYaxis().SetTitleOffset(0.5)
  mgrV_down.GetYaxis().SetTitleSize(mgrV_down.GetYaxis().GetTitleSize()*2.5)
  cLD.cd()
  
  bottom_padLD = ROOT.TPad("bottom_padLD", "bottom_padLD",0,0.1, 1.0, 0.5)
  bottom_padLD.Draw()
  bottom_padLD.cd()
  bottom_padLD.SetTopMargin(0)
  bottom_padLD.SetBottomMargin(0.2)
  bottom_padLD.SetGrid()
  mgrI_down = ROOT.TMultiGraph()
  grmI_down = [ ROOT.TGraph(len(zoom), zoom, lemsI_DOWN) for lemsI_DOWN in LEMsI_down ]
  for i, grI_down, color in zip(range(0,len(LEMsI_down)), grmI_down, col):
    if max_ID < max(LEMsI_down[i]):
      max_ID = max(LEMsI_down[i])
    grI_down.SetLineWidth(3)
    grI_down.SetLineColor(color)
    mgrI_down.Add(grI_down)
  mgrI_down.Draw("AL")
  mgrI_down.SetTitle("")
  mgrI_down.GetYaxis().SetLabelSize(0.1)
  mgrI_down.SetMinimum(0)
  mgrI_down.SetMaximum(max_ID*1.1)
  mgrI_down.GetXaxis().SetTimeDisplay(1)
  mgrI_down.GetXaxis().SetTimeFormat("%H: %M %F1970-01-01 00:00:00")
  mgrI_down.GetXaxis().SetTitle("")
  mgrI_down.GetXaxis().SetLabelSize(0.1)
  mgrI_down.GetXaxis().SetNdivisions(10,4,0,ROOT.kFALSE)
  mgrI_down.GetYaxis().SetTitle("Current [uA]")
  mgrI_down.GetYaxis().SetTitleOffset(0.5)
  mgrI_down.GetYaxis().SetTitleSize(mgrI_down.GetYaxis().GetTitleSize()*2.5)
  cLD.cd()
  leg.SetTextSize(leg.GetTextSize()*0.2)
  leg.Draw()
  cLD.SetLeftMargin(0.1)
  cLD.SaveAs(path + title + "_" + date +  ".pdf")
  cLD.SaveAs(path + title + "_" + date + ".root")
  cLD.Close()

  title = "All_LEMs_Up"
  
  max_VU = -10000
  max_IU = -10000
  
  cLU = ROOT.TCanvas("cLU","cLU",2000,1200)
  leg = ROOT.TLegend(0,0,1,0.1)
  leg.SetNColumns(6)
  
  top_padLU = ROOT.TPad("top_padLU", "top_padLU",0,0.5, 1.0, 1.0)
  top_padLU.Draw()
  top_padLU.cd()
  top_padLU.SetTopMargin(0.2)
  top_padLU.SetBottomMargin(0.01)
  top_padLU.SetGrid()
  mgrV_up = ROOT.TMultiGraph()
  grmV_up = [ ROOT.TGraph(len(zoom), zoom, lemsV_UP) for lemsV_UP in LEMsV_up ]
  for i, grV_up, color in zip(range(0,len(LEMsV_up)), grmV_up, col):
    if max_VU < max(LEMsV_up[i]):
      max_VU = max(LEMsV_up[i])
    grV_up.SetLineWidth(3)
    grV_up.SetLineColor(color)
    leg.AddEntry(grV_up,"LEM %i" %(i+1), "l")
    mgrV_up.Add(grV_up)
  mgrV_up.Draw("AL")
  mgrV_up.SetTitle(title + "_" + date)
  mgrV_up.GetYaxis().SetLabelSize(0.1)
  mgrV_up.SetMinimum(0)
  mgrV_up.SetMaximum(max_VU*1.1)
  mgrV_up.GetXaxis().SetTitle("")
  mgrV_up.GetXaxis().SetLabelSize(0)
  mgrV_up.GetXaxis().SetNdivisions(10,4,0,ROOT.kFALSE)
  mgrV_up.GetYaxis().SetTitle("Voltage [kV]")
  mgrV_up.GetYaxis().SetTitleOffset(0.5)
  mgrV_up.GetYaxis().SetTitleSize(mgrV_up.GetYaxis().GetTitleSize()*2.5)
  cLU.cd()
  
  bottom_padLU = ROOT.TPad("bottom_padLU", "bottom_padLU",0,0.1, 1.0, 0.5)
  bottom_padLU.Draw()
  bottom_padLU.cd()
  bottom_padLU.SetTopMargin(0)
  bottom_padLU.SetBottomMargin(0.2)
  bottom_padLU.SetGrid()
  mgrI_up = ROOT.TMultiGraph()
  grmI_up = [ ROOT.TGraph(len(zoom), zoom, lemsI_UP) for lemsI_UP in LEMsI_up ]
  for i, grI_up, color in zip(range(0,len(LEMsI_up)), grmI_up, col):
    if max_IU < max(LEMsI_up[i]):
      max_IU = max(LEMsI_up[i])
    grI_up.SetLineWidth(3)
    grI_up.SetLineColor(color)
    mgrI_up.Add(grI_up)
  mgrI_up.Draw("AL")
  mgrI_up.SetTitle("")
  mgrI_up.GetYaxis().SetLabelSize(0.1)
  mgrI_up.SetMinimum(0)
  mgrI_up.SetMaximum(max_IU*1.1)
  mgrI_up.GetXaxis().SetTimeDisplay(1)
  mgrI_up.GetXaxis().SetTimeFormat("%H: %M %F1970-01-01 00:00:00")
  mgrI_up.GetXaxis().SetTitle("")
  mgrI_up.GetXaxis().SetLabelSize(0.1)
  mgrI_up.GetXaxis().SetNdivisions(10,4,0,ROOT.kFALSE)
  mgrI_up.GetYaxis().SetTitle("Current [uA]")
  mgrI_up.GetYaxis().SetTitleOffset(0.5)
  mgrI_up.GetYaxis().SetTitleSize(mgrI_up.GetYaxis().GetTitleSize()*2.5)
  cLU.cd()
  leg.SetTextSize(leg.GetTextSize()*0.2)
  leg.Draw()
  cLU.SetLeftMargin(0.1)
  cLU.SaveAs(path + title + "_" + date +  ".pdf")
  cLU.SaveAs(path + title + "_" + date + ".root")
  cLU.Close()

  
  return 0
  

##############################################################################################
# All LEM currents scaled to study leackages
##############################################################################################

def plot_all_LEMs_leackage(time, date, const_LEMsI_up, const_LEMsI_down, Imax, const_Hall_T, path, title, tmin = 0, tmax = 1):
  
  is_list = isinstance(const_LEMsI_up,list) and isinstance(const_LEMsI_down,list)
  if is_list == False: 
    print("ERROR in plot_all_LEMs_leackage: Must give a list all LEMs for leackage plot")
    return
  
  if((tmin == 0) & (tmax == 1)):
    tmin = time[0]
    tmax = tmin + time[len(time) - 1]

  zoom = time[(time >= tmin) & (time <= tmax)]
  LEMsI_up = []
  LEMsI_down = []
  Hall_T = const_Hall_T[(time >= tmin) & (time <= tmax)]
  for i in range(0,len(const_LEMsI_up)):
    LEMsI_up.append(const_LEMsI_up[i][(time >= tmin) & (time <= tmax)])
    LEMsI_down.append(const_LEMsI_down[i][(time >= tmin) & (time <= tmax)])

  col = [ROOT.kBlack, ROOT.kCyan, ROOT.kBlue, ROOT.kRed, ROOT.kGreen, ROOT.kYellow, ROOT.kYellow+2, ROOT.kMagenta, ROOT.kGreen+2, ROOT.kGray, ROOT.kPink+2, ROOT.kMagenta+2]

  
  cLU = ROOT.TCanvas("cLU","cLU",2000,1200)
  leg = ROOT.TLegend(0,0,1,0.1)
  leg.SetNColumns(6)
  
  top_padLUy1 = ROOT.TPad("top_padLUy1", "top_padLUy1",0,0.55, 1.0, 1.0)
  top_padLUy1.Draw()
  top_padLUy1.cd()
  top_padLUy1.SetTopMargin(0.2)
  top_padLUy1.SetBottomMargin(0.05)
  top_padLUy1.SetGrid()
  mgrI_up = ROOT.TMultiGraph()
  grmI_up = [ ROOT.TGraph(len(zoom), zoom, lemsI_UP) for lemsI_UP in LEMsI_up ]
  for i, grI_up, color in zip(range(0,len(LEMsI_up)), grmI_up, col):
    grI_up.SetLineWidth(1)
    grI_up.SetLineColor(color)
    leg.AddEntry(grI_up,"LEM %i" %(i+1), "l")
    mgrI_up.Add(grI_up)
  mgrI_up.Draw("AL")
  mgrI_up.SetTitle(title + "_" + date)
  mgrI_up.GetYaxis().SetLabelSize(0.07)
  mgrI_up.SetMinimum(0)
  mgrI_up.SetMaximum(Imax)
  mgrI_up.GetXaxis().SetTitle("")
  mgrI_up.GetXaxis().SetLabelSize(0)
  mgrI_up.GetXaxis().SetNdivisions(10,4,0,ROOT.kFALSE)
  mgrI_up.GetYaxis().SetTitle("Current up [uA]")
  mgrI_up.GetYaxis().SetTitleOffset(0.5)
  mgrI_up.GetYaxis().SetTitleSize(mgrI_up.GetYaxis().GetTitleSize()*2.5)
  cLU.cd()
  
  top_padLUy2 = ROOT.TPad("top_padLUy2", "top_padLUy2",0,0.55, 1.0, 1.0)
  top_padLUy2.Draw()
  top_padLUy2.cd()
  top_padLUy2.SetTopMargin(0.2)
  top_padLUy2.SetBottomMargin(0.05)
  top_padLUy2.SetFillStyle(4000)
  top_padLUy2.SetFillColor(0)
  top_padLUy2.SetFrameFillStyle(4000)
  gr_Hall_T = ROOT.TGraph(len(zoom), zoom, Hall_T)
  gr_Hall_T.Draw("ALY+")
  gr_Hall_T.GetXaxis().SetRangeUser(zoom[0],zoom[-1])
  gr_Hall_T.SetLineColor(ROOT.kGreen)
  gr_Hall_T.GetYaxis().SetTitle("Hall temperature [K]")
  gr_Hall_T.SetTitle("")
  gr_Hall_T.GetXaxis().SetTitle("")
  gr_Hall_T.GetXaxis().SetLabelSize(0)
  gr_Hall_T.GetXaxis().SetTickSize(0)
  gr_Hall_T.GetYaxis().SetLabelSize(0.07) 
  gr_Hall_T.GetYaxis().SetTitleSize(gr_Hall_T.GetYaxis().GetTitleSize()*2.5) 
  gr_Hall_T.GetYaxis().SetTitleOffset(0.5)
  leg.AddEntry(gr_Hall_T,"Hall temperature", "l")
  cLU.cd()
  
  bottom_padLU = ROOT.TPad("bottom_padLU", "bottom_padLU",0,0.1, 1.0, 0.55)
  bottom_padLU.Draw()
  bottom_padLU.cd()
  bottom_padLU.SetTopMargin(0.05)
  bottom_padLU.SetBottomMargin(0.2)
  bottom_padLU.SetGrid()
  mgrI_down = ROOT.TMultiGraph()
  grmI_down = [ ROOT.TGraph(len(zoom), zoom, lemsI_DOWN) for lemsI_DOWN in LEMsI_down ]
  for i, grI_down, color in zip(range(0,len(LEMsI_down)), grmI_down, col):
    grI_down.SetLineWidth(1)
    grI_down.SetLineColor(color)
    mgrI_down.Add(grI_down)
  mgrI_down.Draw("AL")
  mgrI_down.SetTitle("")
  mgrI_down.GetYaxis().SetLabelSize(0.07)
  mgrI_down.SetMinimum(0)
  mgrI_down.SetMaximum(Imax)
  mgrI_down.GetXaxis().SetTimeDisplay(1)
  mgrI_down.GetXaxis().SetTimeFormat("%H: %M %F1970-01-01 00:00:00")
  mgrI_down.GetXaxis().SetTitle("")
  mgrI_down.GetXaxis().SetLimits(zoom[0], zoom[-1])
  mgrI_down.GetXaxis().SetLabelSize(0.08)
  mgrI_down.GetXaxis().SetLabelOffset(0.05)
  mgrI_down.GetXaxis().SetNdivisions(10,4,0,ROOT.kFALSE)
  mgrI_down.GetYaxis().SetTitle("Current down [uA]")
  mgrI_down.GetYaxis().SetTitleOffset(0.5)
  mgrI_down.GetYaxis().SetTitleSize(mgrI_down.GetYaxis().GetTitleSize()*2.5)
  cLU.cd()

  leg.SetTextSize(leg.GetTextSize()*0.2)
  leg.Draw()
  cLU.SetLeftMargin(0.1)
  cLU.SaveAs(path + title + "_" + date +  ".pdf")
  cLU.SaveAs(path + title + "_" + date + ".root")
  cLU.Close()
  
  return 0
  

def plot_all_V_I(time, date, const_cathode_voltage, const_cathode_current, const_grid_voltage, const_grid_current, const_LEMsV_up, const_LEMsI_up, const_LEMsV_down, const_LEMsI_down, const_LV_8, tmin = 0, tmax = 1):
  
  title = "Cathode_Grid"
  path = "./" + sys.argv[4] + "/all_V_I/"
  
  if((tmin == 0) & (tmax == 1)):
    tmin = time[0]
    tmax = tmin + time[len(time) - 1]

  zoom = time[(time >= tmin) & (time <= tmax)]
  cathode_voltage = const_cathode_voltage[(time >= tmin) & (time <= tmax)]
  cathode_current = const_cathode_current[(time >= tmin) & (time <= tmax)]
  grid_voltage = const_grid_voltage[(time >= tmin) & (time <= tmax)]
  grid_current = const_grid_current[(time >= tmin) & (time <= tmax)]
  grid_voltage = grid_voltage / 1000
  LV_8 = const_LV_8[(time >= tmin) & (time <= tmax)]
  LEMsI_up = []
  LEMsV_up = []
  LEMsI_down = []
  LEMsV_down = []  
  for i in range(0,len(const_LEMsI_up)):
    LEMsI_up.append(const_LEMsI_up[i][(time >= tmin) & (time <= tmax)])
  for i in range(0,len(const_LEMsV_up)):
    LEMsV_up.append(const_LEMsV_up[i][(time >= tmin) & (time <= tmax)])
  for i in range(0,len(const_LEMsI_down)):
    LEMsI_down.append(const_LEMsI_down[i][(time >= tmin) & (time <= tmax)])
  for i in range(0,len(const_LEMsV_down)):
    LEMsV_down.append(const_LEMsV_down[i][(time >= tmin) & (time <= tmax)] / 1000)

  c1 = ROOT.TCanvas("c1", "dit", 2000, 1200)
  leg = ROOT.TLegend(0,0,1,0.1)
  leg.SetNColumns(2)

  pad1 = ROOT.TPad("pad1", "", 0, 0, 1, 1)
  pad1.Draw()
  pad1.cd()
  pad1.SetGrid()
  pad1.SetBottomMargin(0.2)
  gr_cath_V = ROOT.TGraph(len(zoom), zoom, cathode_voltage)
  gr_cath_V.Draw("AL")
  gr_cath_V.SetMinimum(0)
  gr_cath_V.SetMaximum(max([max(cathode_voltage),max(grid_voltage)])*1.1)  
  gr_cath_V.SetLineColor(ROOT.kRed)
  gr_cath_V.SetTitle("")
  gr_cath_V.GetXaxis().SetTimeDisplay(1)
  gr_cath_V.GetXaxis().SetTimeFormat("%H: %M %F1970-01-01 00:00:00")
  gr_cath_V.GetXaxis().SetLabelSize(0.025)
  gr_cath_V.GetXaxis().SetTitle("Time")
  gr_cath_V.GetYaxis().SetTitle("Voltage [kV]")
  leg.AddEntry(gr_cath_V," Cathode Voltage","l")
  gr_grid_V = ROOT.TGraph(len(zoom), zoom, grid_voltage)
  gr_grid_V.Draw("SAME")
  gr_grid_V.SetMinimum(0)
  gr_grid_V.SetLineColor(ROOT.kMagenta)
  gr_grid_V.SetTitle("")
  leg.AddEntry(gr_grid_V," Grid Voltage","l")
  c1.cd()
  #
  pad2 = ROOT.TPad("pad2", "", 0, 0, 1, 1)
  pad2.Draw()
  pad2.cd()
  pad2.SetFillStyle(4000)
  pad2.SetFrameFillStyle(0)
  pad2.SetBottomMargin(0.2)
  gr_cath_I = ROOT.TGraph(len(zoom), zoom, cathode_current)
  gr_cath_I.Draw("ALY+")
  gr_cath_I.SetMinimum(0)
  gr_cath_I.SetMaximum(max([max(cathode_current),max(grid_current)])*1.1)
  gr_cath_I.SetLineColor(ROOT.kBlue)
  gr_cath_I.SetTitle(title + "_" + date)
  gr_cath_I.GetXaxis().SetLabelSize(0)
  gr_cath_I.GetXaxis().SetTickSize(0)  
  gr_cath_I.GetYaxis().SetTitle("Current [uA]")
  leg.AddEntry(gr_cath_I," Cathode Current","l")
  gr_grid_I = ROOT.TGraph(len(zoom), zoom, grid_current)
  gr_grid_I.Draw("SAME")
  gr_grid_I.SetMinimum(0)
  gr_grid_I.SetLineColor(ROOT.kCyan)
  gr_grid_I.SetTitle("")
  leg.AddEntry(gr_grid_I," Grid Current","l")
  c1.cd()
  #
  leg.Draw()
  c1.SetLeftMargin(0.1)
  c1.SaveAs(path + title + "_" + date + ".pdf")
  c1.SaveAs(path + title + "_" + date + ".root")
  c1.Close()
  #
  #
  #
  col = [ROOT.kBlack, ROOT.kCyan, ROOT.kBlue, ROOT.kRed, ROOT.kGreen, ROOT.kYellow, ROOT.kYellow+2, ROOT.kMagenta, ROOT.kGreen+2, ROOT.kGray, ROOT.kPink+2, ROOT.kMagenta+2]
  title = "LEMs_Up_V"
  c2 = ROOT.TCanvas("c2", "dit", 2000, 1200)
  c2.SetGrid()
  c2.SetBottomMargin(0.2)
  leg=ROOT.TLegend(0.02,0.02,0.98,0.15)
  leg.SetNColumns(6)
  mgrV_up = ROOT.TMultiGraph()
  grmV_up = [ ROOT.TGraph(len(zoom), zoom, lemsV_UP) for lemsV_UP in LEMsV_up ]
  for i, grV_up, color in zip(range(0,len(LEMsV_up)), grmV_up, col):
    grV_up.SetLineWidth(3)
    grV_up.SetLineColor(color)
    leg.AddEntry(grV_up,"LEM %i" %(i+1), "l")
    mgrV_up.Add(grV_up)
  mgrV_up.Draw("AL")
  mgrV_up.SetTitle(title + "_" + date)
  mgrV_up.SetMinimum(0)
  mgrV_up.GetXaxis().SetTimeDisplay(1)
  mgrV_up.GetXaxis().SetTimeFormat("%H: %M %F1970-01-01 00:00:00")
  mgrV_up.GetXaxis().SetTitle("time")
  mgrV_up.GetYaxis().SetTitle("Voltage [V]")
  mgrV_up.GetYaxis().SetTitleOffset(1.5)
  leg.Draw()
  c2.SetLeftMargin(0.1)
  c2.SaveAs(path + title + "_" + date + ".pdf")
  c2.SaveAs(path + title + "_" + date + ".root")
  c2.Close()
  #
  #
  #
  
  title = "LEMs_Up_I"
  c3 = ROOT.TCanvas("c3", "dit", 2000, 1200)
  leg=ROOT.TLegend(0.02,0.02,0.98,0.15)
  leg.SetNColumns(6)
  #
  pad1 = ROOT.TPad("pad1", "", 0, 0, 1, 1)
  pad1.Draw()
  pad1.cd()
  pad1.SetGrid()
  pad1.SetBottomMargin(0.2)
  mgrI_up = ROOT.TMultiGraph()
  grmI_up = [ ROOT.TGraph(len(zoom), zoom, lemsI_UP) for lemsI_UP in LEMsI_up ]
  for i, grI_up, color in zip(range(0,len(LEMsI_up)), grmI_up, col):
    grI_up.SetLineWidth(3)
    grI_up.SetLineColor(color)
    leg.AddEntry(grI_up,"LEM %i" %(i+1), "l")
    mgrI_up.Add(grI_up)
  mgrI_up.Draw("AL")
  mgrI_up.SetTitle(title + "_" + date)
  mgrI_up.SetMinimum(0)
  mgrI_up.GetXaxis().SetTimeDisplay(1)
  mgrI_up.GetXaxis().SetTimeFormat("%H: %M %F1970-01-01 00:00:00")
  mgrI_up.GetXaxis().SetTitle("time")
  mgrI_up.GetYaxis().SetTitle("Current [uA]")
  mgrI_up.GetYaxis().SetTitleOffset(1.5)
  c3.cd()
  #
  pad2 = ROOT.TPad("pad2", "", 0, 0, 1, 1)
  pad2.Draw()
  pad2.cd()
  pad2.SetFillStyle(4000)
  pad2.SetFrameFillStyle(0)
  pad2.SetBottomMargin(0.2)
  gr_level = ROOT.TGraph(len(zoom), zoom, LV_8)
  gr_level.Draw("ALY+")
  gr_level.GetXaxis().SetLabelSize(0)
  gr_level.GetXaxis().SetTickSize(0)
  gr_level.GetYaxis().SetTitle("Levelmeter CRP 8 [mm]")
  gr_level.SetLineColor(ROOT.kRed)
  gr_level.GetYaxis().SetTitleOffset(1.5)
  gr_level.SetTitle("")
  gr_level.SetMinimum(0)
  gr_level.SetMaximum(25)
  leg.AddEntry(gr_level,"levelmeter 8", "l")
  c3.cd()
  #
  leg.Draw() 
  c3.SetLeftMargin(0.1)
  c3.SaveAs(path + title + "_" + date + ".pdf")
  c3.SaveAs(path + title + "_" + date + ".root")
  c3.Close()
  #
  #
  #
  
  title = "LEMs_Down_V"
  c4 = ROOT.TCanvas("c4", "dit", 2000, 1200)
  c4.SetGrid()
  c4.SetBottomMargin(0.2)
  leg=ROOT.TLegend(0.02,0.02,0.98,0.15)
  leg.SetNColumns(6)
  mgrV_down = ROOT.TMultiGraph()
  grmV_down = [ ROOT.TGraph(len(zoom), zoom, lemsV_DOWN/1000) for lemsV_DOWN in LEMsV_down ]
  for i, grV_down, color in zip(range(0,len(LEMsV_down)), grmV_down, col):
    grV_down.SetLineWidth(3)
    grV_down.SetLineColor(color)
    leg.AddEntry(grV_down,"LEM %i" %(i+1), "l")
    mgrV_down.Add(grV_down)
  mgrV_down.Draw("AL")
  mgrV_down.SetTitle(title + "_" + date)
  mgrV_down.GetXaxis().SetTimeDisplay(1)
  mgrV_down.SetMinimum(0)
  mgrV_down.GetXaxis().SetTimeFormat("%H: %M %F1970-01-01 00:00:00")
  mgrV_down.GetXaxis().SetTitle("time")
  mgrV_down.GetYaxis().SetTitle("Voltage [kV]")
  mgrV_down.GetYaxis().SetTitleOffset(1.5)
  leg.Draw()
  c4.SetLeftMargin(0.1)
  c4.SaveAs(path + title + "_" + date + ".pdf")
  c4.SaveAs(path + title + "_" + date + ".root")
  c4.Close()
  #
  #
  #
  title = "LEMs_Down_I"
  c5 = ROOT.TCanvas("c5", "dit", 2000, 1200)
  leg=ROOT.TLegend(0.02,0.02,0.98,0.15)
  leg.SetNColumns(6)
  #
  pad1 = ROOT.TPad("pad1", "", 0, 0, 1, 1)
  pad1.Draw()
  pad1.cd()
  pad1.SetGrid()
  pad1.SetBottomMargin(0.2)
  mgrI_down = ROOT.TMultiGraph()
  grmI_down = [ ROOT.TGraph(len(zoom), zoom, lemsI_DOWN) for lemsI_DOWN in LEMsI_down ]
  for i, grI_down, color in zip(range(0,len(LEMsI_down)), grmI_down, col):
    grI_down.SetLineWidth(3)
    grI_down.SetLineColor(color)
    leg.AddEntry(grI_down,"LEM %i" %(i+1), "l")
    mgrI_down.Add(grI_down)
  mgrI_down.Draw("AL")
  mgrI_down.SetTitle(title + "_" + date)
  mgrI_down.SetMinimum(0)
  mgrI_down.GetXaxis().SetTimeDisplay(1)
  mgrI_down.GetXaxis().SetTimeFormat("%H: %M %F1970-01-01 00:00:00")
  mgrI_down.GetXaxis().SetTitle("time")
  mgrI_down.GetYaxis().SetTitle("Current [uA]")
  mgrI_down.GetYaxis().SetTitleOffset(1.5)
  c5.cd()
  #
  pad2 = ROOT.TPad("pad2", "", 0, 0, 1, 1)
  pad2.Draw()
  pad2.cd()
  pad2.SetFillStyle(4000)
  pad2.SetFrameFillStyle(0)
  pad2.SetBottomMargin(0.2)
  gr_level = ROOT.TGraph(len(zoom), zoom, LV_8)
  gr_level.Draw("ALY+")
  gr_level.GetXaxis().SetLabelSize(0)
  gr_level.GetXaxis().SetTickSize(0)  
  gr_level.GetYaxis().SetTitle("Levelmeter CRP 8 [mm]")
  gr_level.SetLineColor(ROOT.kRed)
  gr_level.GetYaxis().SetTitleOffset(1.5)
  gr_level.SetTitle("")
  gr_level.SetMinimum(0)
  gr_level.SetMaximum(25)
  leg.AddEntry(gr_level,"levelmeter 8", "l")
  c5.cd()
  #
  leg.Draw() 
  c5.SetLeftMargin(0.1)
  c5.SaveAs(path + title + "_" + date + ".pdf")
  c5.SaveAs(path + title + "_" + date + ".root")
  c5.Close()
  
  return 0



##############################################################################################
# Levelmeters
##############################################################################################

def plot_LM(time, date, const_level_array, title, tmin = 0, tmax = 1):

  if((tmin == 0) & (tmax == 1)):
    tmin = time[0]
    tmax = tmin + time[len(time) - 1]
  zoom = time[(time >= tmin) & (time <= tmax)]
  level_array = []
  for i in range(0,len(const_level_array)):
    level_array.append(const_level_array[i][(time >= tmin) & (time <= tmax)])
 
  col = [ROOT.kBlack, ROOT.kGray, ROOT.kBlue, ROOT.kRed, ROOT.kGreen+1, ROOT.kAzure+10, ROOT.kPink-3]
  c1 = ROOT.TCanvas("c1", "dit", 2000, 1200)
  c1.SetGrid()
  c1.SetBottomMargin(0.2)

  leg=ROOT.TLegend(0.02,0.02,0.98,0.15)
  leg.SetNColumns(4)

  mgr = ROOT.TMultiGraph()
  mgr.SetTitle(title + "_" + date)
  
  grm = [ ROOT.TGraph(len(zoom), zoom, level) for level in level_array ]
  j = 1
  for i, gr, color in zip(range(0,len(level)), grm, col):
    gr.SetLineWidth(3)
    gr.SetLineColor(color)
    if(i==3): j +=1
    leg.AddEntry(gr,"levelmeter CRP %i" %j, "l")
    j += 1
    mgr.Add(gr)
  
  mgr.Draw("AL")
  mgr.SetMinimum(0)
  mgr.SetMaximum(25)
  mgr.GetXaxis().SetTimeDisplay(1)
  mgr.GetXaxis().SetTimeFormat("%H: %M %F1970-01-01 00:00:00")
  mgr.GetXaxis().SetTitle("time")
  mgr.GetYaxis().SetTitle("levelmeters CRP [mm]")
  mgr.GetYaxis().SetTitleSize(0.05)  
  mgr.GetYaxis().SetTitleOffset(0.7)
  mgr.Draw("AL")

  leg.Draw()
    
  c1.SetLeftMargin(0.1)
  c1.SaveAs("./" + sys.argv[4] + "/LevelMeters/" + title + "_" + date +  ".pdf")
  c1.SaveAs("./" + sys.argv[4] + "/LevelMeters/" + title + "_" + date + ".root")
  c1.Close()

  return 0
  
  
##############################################################################################
# Levelmeters differences
##############################################################################################

def plot_LM_Delta(time, date, const_level_list, level_reference, title, tmin = 0, tmax = 1):

  if((tmin == 0) & (tmax == 1)):
    tmin = time[0]
    tmax = tmin + time[len(time) - 1]
  zoom = time[(time >= tmin) & (time <= tmax)]
  
  level_list = []
  for i in range(0,len(const_level_list)):
    level_list.append(const_level_list[i][(time >= tmin) & (time <= tmax)])

  col = [ROOT.kBlack, ROOT.kGray, ROOT.kBlue, ROOT.kRed, ROOT.kGreen+1, ROOT.kAzure+10, ROOT.kPink-3]
  c1 = ROOT.TCanvas("c1", "dit", 2000, 1200)
  c1.SetGrid()
  c1.SetBottomMargin(0.2)

  leg=ROOT.TLegend(0.02,0.02,0.98,0.15)
  leg.SetNColumns(4)

  mgr = ROOT.TMultiGraph()
  mgr.SetTitle(title + "_" + date)
  
  level_list_delta = []
  
  for i in range(0,len(level_list)):
    if level_reference < 4:
      level_list_delta.append(numpy.array(numpy.array(level_list[level_reference-1]) - numpy.array(level_list[i])))
    if level_reference >= 4:
      level_list_delta.append(numpy.array(numpy.array(level_list[level_reference-2]) - numpy.array(level_list[i])))
    
  level_array = numpy.array(level_list_delta)
  
  grm = [ ROOT.TGraph(len(zoom), zoom, level) for level in level_array ]
  j = 1
  for i, gr, color in zip(range(0,len(level)), grm, col):
    gr.SetLineWidth(3)
    gr.SetLineColor(color)
    if(i==3): j +=1
    leg.AddEntry(gr,"levelmeter CRP %i" %j, "l")
    j += 1
    mgr.Add(gr)
  
  mgr.Draw("AL")
  mgr.GetXaxis().SetTimeDisplay(1)
  mgr.GetXaxis().SetTimeFormat("%H: %M %F1970-01-01 00:00:00")
  mgr.GetXaxis().SetTitle("time")
  mgr.GetYaxis().SetTitle("Level difference [mm]")
  mgr.GetYaxis().SetTitleSize(0.05)
  mgr.GetYaxis().SetTitleOffset(0.7)
  mgr.Draw("AL")

  leg.Draw()
    
  c1.SetLeftMargin(0.1)
  c1.SaveAs("./" + sys.argv[4] + "/LevelMeters/" + title + "_" + date + ".pdf")
  c1.SaveAs("./" + sys.argv[4] + "/LevelMeters/" + title + "_" + date + ".root")
  c1.Close()

  return 0

##############################################################################################
# Levelmeters RMS
##############################################################################################

def Plot_LM_RMS(time, date, level_array, title, tmin = 0, tmax = 1):
  
  if((tmin == 0) & (tmax == 1)):
    tmin = time[0]
    tmax = tmin + time[len(time) - 1]
    
  zoom = time[(time >= tmin) & (time <= tmax)]
    
  slices = (zoom[len(zoom)-1]-zoom[0])//(30*60)
  rms_list = []
  time_list = []
  if tmax-tmin <= 30*60:
    print "Time window too short for RMS of levelmeters"
    return 1
  
  for k in range(0,len(level_array)):
    rms = []
    zoom_level = level_array[k][(time >= tmin) & (time <= tmax)]
    for i in range(0,int(slices)+1):
      time_window = zoom[(zoom >= tmin+i*30*60) & (zoom <= tmin+(i+1)*30*60)]
      if len(time_window) == 1:
        continue
      if k == 0:
        time_list.append(time_window[0])
      level = zoom_level[(zoom >= tmin+i*30*60) & (zoom <= tmin+(i+1)*30*60)]
      mean = 0
      rms_tmp = 0
      for j in range(0,len(time_window)):
        mean += level[j]
      mean = mean/len(time_window)
      for j in range(0,len(time_window)):
        rms_tmp += (level[j] - mean)*(level[j] - mean)
      rms_tmp = rms_tmp/(len(time_window)-1)
      rms.append(math.sqrt(rms_tmp))
    rms_list.append(rms)
  col = [ROOT.kBlack, ROOT.kGray, ROOT.kBlue, ROOT.kRed, ROOT.kGreen+1, ROOT.kAzure+10, ROOT.kPink-3]
  c1 = ROOT.TCanvas("c1", "dit", 2000, 1200)
  c1.SetGrid()
  c1.SetBottomMargin(0.2)

  leg=ROOT.TLegend(0.02,0.02,0.98,0.15)
  leg.SetNColumns(4)

  mgr = ROOT.TMultiGraph()
  mgr.SetTitle(title + "_" + date)
  
  time_array = numpy.array(time_list)
  rms_array = numpy.array(rms_list)
  print("Mean levelmeters RMS: ")
  for i in range(0,len(rms_array)):
    if i+1 <=3:
      print(str(i+1) + " " + "%.4f" %numpy.mean(rms_array[i]))
    else:
      print(str(i+2) + " " + "%.4f" %numpy.mean(rms_array[i]))
  
  grm = [ ROOT.TGraph(len(time_array), time_array, RMS) for RMS in rms_array ]
  j = 1
    
  for i, gr, color in zip(range(0,len(rms_array)), grm, col):
    gr.SetLineWidth(3)
    gr.SetLineColor(color)
    if(i==3): j +=1
    leg.AddEntry(gr,"levelmeter CRP %i" %j, "l")
    j += 1
    mgr.Add(gr)
  
  mgr.Draw("AL")
  mgr.GetXaxis().SetTimeDisplay(1)
  mgr.GetXaxis().SetTimeFormat("%H: %M %F1970-01-01 00:00:00")
  mgr.GetXaxis().SetTitle("time")
  mgr.GetYaxis().SetTitle("Level RMS [mm]")
  mgr.GetYaxis().SetTitleSize(0.05)
  mgr.GetYaxis().SetTitleOffset(1)
  mgr.Draw("AL")

  leg.Draw()
    
  c1.SetLeftMargin(0.1)
  c1.SaveAs("./" + sys.argv[4] + "/LevelMeters/" + title + "_" + date + ".pdf")
  c1.SaveAs("./" + sys.argv[4] + "/LevelMeters/" + title + "_" + date + ".root")
  c1.Close()

  return 0
  
##############################################################################################
# Trips
##############################################################################################

def Trips(time, date, const_VGrid, const_VLEMdown, const_level_array, title, tmin = 0, tmax = 1):
  
  if((tmin == 0) & (tmax == 1)):
    tmin = time[0]
    tmax = tmin + time[len(time) - 1]
    
  zoom = time[(time >= tmin) & (time <= tmax)]
  VGrid = const_VGrid[(time >= tmin) & (time <= tmax)]
  VLEMdown = const_VLEMdown[(time >= tmin) & (time <= tmax)]
  level_array = []
  trips_list = []
  level_trips_list = []
  for i in range(0,len(const_level_array)):
    level_array.append(const_level_array[i][(time >= tmin) & (time <= tmax)])
    level_trips_list.append([])
    
  

  for i in range(0,len(VGrid)):
    if i > 0:
      if VGrid[i] < 50 and VGrid[i-1] > 50:
        trips_list.append(zoom[i])
        for j in range(0,len(level_array)):
          level_trips_list[j].append(numpy.array(level_array[j][i]))
       
  if len(trips_list) == 1:
    print "No trip detected"
    return 0
    
  del trips_list[-1]
  for j in range(0,len(level_trips_list)):
    del level_trips_list[j][-1]

  trips_array = numpy.array(trips_list)
  level_trips_array = numpy.array(level_trips_list)
  
  mgr = ROOT.TMultiGraph()
  mgr.SetTitle(title + "_" + date)
  
  grm_trips = [ROOT.TGraph(len(trips_array),trips_array,level) for level in level_trips_array]
  grm_level = [ROOT.TGraph(len(zoom),zoom,levels) for levels in level_array]
  gr_gridV = ROOT.TGraph(len(zoom), zoom, VGrid/1000)
  gr_VLEMdown = ROOT.TGraph(len(zoom), zoom, VLEMdown/1000)  
  
  col = [ROOT.kBlack, ROOT.kYellow, ROOT.kBlue, ROOT.kRed, ROOT.kGreen+1, ROOT.kAzure+10, ROOT.kPink-3]
  
  c1 = ROOT.TCanvas("c1", "dit", 2000, 1200)
  leg=ROOT.TLegend(0.02,0.02,0.98,0.18)
  leg.SetNColumns(4)
  pady1 = ROOT.TPad("pady1", "pady1",0,0, 1.0, 1.0)
  pady1.Draw()
  pady1.cd()
  pady1.SetBottomMargin(0.2)
  j=1
  for i, gr_trips, gr_level, color in zip(range(0,len(level_trips_array)), grm_trips, grm_level, col):
    gr_level.SetLineColorAlpha(color, 0.35)
    gr_level.SetLineWidth(3)
    mgr.Add(gr_level,"AL")
    gr_trips.SetMarkerStyle(28)
    gr_trips.SetMarkerColor(color)
    gr_trips.SetLineColor(color)
    gr_trips.SetLineWidth(3)
    gr_trips.SetMarkerSize(3)
    if(i==3): j +=1
    leg.AddEntry(gr_trips,"levelmeter CRP %i" %j, "p")
    j += 1
    mgr.Add(gr_trips)
  mgr.Draw("AP")
  mgr.SetMinimum(0)
  mgr.SetMaximum(25)
  mgr.GetXaxis().SetRangeUser(zoom[0],zoom[-1])
  mgr.GetYaxis().SetTitle("LAr level [mm]")
  mgr.GetXaxis().SetTimeDisplay(1)
  mgr.GetXaxis().SetTimeFormat("%H: %M %F1970-01-01 00:00:00")
  mgr.GetXaxis().SetTitle("time")
  mgr.GetXaxis().SetTitleSize(0.05)
  mgr.GetYaxis().SetTitleOffset(0.7)
  mgr.GetYaxis().SetTitleSize(0.05)
  mgr.GetYaxis().SetLabelSize(0.045)
  c1.cd()
  #
  pady2 = ROOT.TPad("pady2", "pady2",0,0, 1.0, 1.0)
  pady2.Draw()
  pady2.cd()  
  pady2.SetBottomMargin(0.2)
  pady2.SetFillStyle(4000)
  pady2.SetFillColor(0)
  pady2.SetFrameFillStyle(4000)
  gr_gridV.Draw("ALY+")
  gr_gridV.GetXaxis().SetRangeUser(zoom[0],zoom[-1])
  gr_gridV.SetLineColor(ROOT.kYellow+3)
  gr_gridV.GetYaxis().SetTitle("Grid Voltage [kV]")
  gr_gridV.SetTitle("")
  gr_gridV.GetXaxis().SetTitle("")
  gr_gridV.GetXaxis().SetLabelSize(0)
  gr_gridV.GetXaxis().SetTickSize(0)
  gr_gridV.GetYaxis().SetLabelSize(0.045) 
  gr_gridV.GetYaxis().SetTitleSize(0.05) 
  gr_gridV.GetYaxis().SetTitleOffset(0.7)
  leg.AddEntry(gr_gridV,"Grid Voltage", "l")
  gr_VLEMdown.Draw("SAME")
  gr_VLEMdown.SetLineColor(ROOT.kBlue)
  leg.AddEntry(gr_VLEMdown,"LEM_Down_Voltage", "l")

  leg.Draw()
  c1.SetLeftMargin(0.1)
  c1.SaveAs("./" + sys.argv[4] + "/Trips/" + title + "_" + date + ".pdf")
  c1.SaveAs("./" + sys.argv[4] + "/Trips/" + title + "_" + date + ".root")
  c1.Close()
  
  return 0
  
 
##############################################################################################
# Level & LEM current
##############################################################################################


def plot_LEM_GRID(time, date, const_gridV, const_gridI, const_LEMV_down, const_LEMI_down, const_LEMV_up, const_LEMI_up, tmin = 0, tmax = 0, LEM_name = "LEM_NUMBER_1"):
  
  if((tmin == 0) & (tmax == 1)):
    tmin = time[0]
    tmax = tmin + time[len(time) - 1]
    
  zoom = time[(time >= tmin) & (time <= tmax)]
  gridV = const_gridV[(time >= tmin) & (time <= tmax)]
  gridI = const_gridI[(time >= tmin) & (time <= tmax)]
  LEMV_down = const_LEMV_down[(time >= tmin) & (time <= tmax)]
  LEMI_down = const_LEMI_down[(time >= tmin) & (time <= tmax)]
  LEMV_up = const_LEMV_up[(time >= tmin) & (time <= tmax)]
  LEMI_up = const_LEMI_up[(time >= tmin) & (time <= tmax)]
  
  path = "./" + sys.argv[4] + "/LEM_GRID/"
  
  leg = ROOT.TLegend(0,0,1,0.08)
  leg.SetNColumns(4)
  
  if(max(gridI) > max(LEMI_down)):
    maxI = max(gridI)
  else:
    maxI = max(LEMI_down)

  c1 = ROOT.TCanvas("c1","c1",2200,1200)
  #
  top_pady1 = ROOT.TPad("top_pady1", "top_pady1",0,0.10, 1.0, 0.56)
  top_pady1.Draw()
  top_pady1.cd()
  top_pady1.SetTopMargin(0.1)
  top_pady1.SetBottomMargin(0.2)
  top_pady1.SetGrid()
  gr_gridV = ROOT.TGraph(len(zoom), zoom, gridV)
  gr_gridV.Draw("AL")
  gr_gridV.SetMinimum(0)
  gr_gridV.SetMaximum(max(gridV)*1.1)  
  gr_gridV.SetTitle("Grid and " + LEM_name + " down " + date)
  gr_gridV.SetLineWidth(3)
  gr_gridV.SetLineColor(ROOT.kRed)
  gr_gridV.GetXaxis().SetLabelSize(0)
  gr_gridV.GetXaxis().SetLimits(zoom[0], zoom[-1])
  gr_gridV.GetYaxis().SetTitleOffset(0.6)
  gr_gridV.GetXaxis().SetNdivisions(10,4,0,ROOT.kFALSE)
  gr_gridV.GetYaxis().SetLabelSize(0.1)
  gr_gridV.GetYaxis().SetTitle("Voltage [V]")
  gr_gridV.GetYaxis().SetTitleSize(gr_gridV.GetYaxis().GetTitleSize()*2.5)
  leg.AddEntry(gr_gridV,"Grid Voltage","l")
  c1.cd()
  #
  top_pady3 = ROOT.TPad("top_pady3", "top_pady3",0,0.10, 1.0, 0.56)
  top_pady3.Draw()
  top_pady3.cd()
  top_pady3.SetFillStyle(4000)
  top_pady3.SetFillColor(0)
  top_pady3.SetFrameFillStyle(4000)
  top_pady3.SetTopMargin(0.1)
  top_pady3.SetBottomMargin(0.2)
  top_pady3.SetGridx(1)
  gr_LEMV_down = ROOT.TGraph(len(zoom), zoom, LEMV_down)
  gr_LEMV_down.Draw("AL")
  gr_LEMV_down.SetMinimum(0)
  gr_LEMV_down.SetMaximum(max(gridV)*1.1)  
  gr_LEMV_down.SetTitle("")
  gr_LEMV_down.SetLineWidth(3)
  gr_LEMV_down.SetLineColor(ROOT.kGray+1)
  gr_LEMV_down.GetXaxis().SetLabelSize(0)
  gr_LEMV_down.GetXaxis().SetLimits(zoom[0], zoom[-1])
  gr_LEMV_down.GetXaxis().SetNdivisions(10,4,0,ROOT.kFALSE)
  gr_LEMV_down.GetYaxis().SetLabelSize(0.1)
  leg.AddEntry(gr_LEMV_down,"LEM down Voltage","l")
  c1.cd()
  #
  top_pady4 = ROOT.TPad("top_pady4", "top_pady4",0,0.10, 1.0, 0.56)
  top_pady4.Draw()
  top_pady4.cd()
  top_pady4.SetFillStyle(4000)
  top_pady4.SetFillColor(0)
  top_pady4.SetFrameFillStyle(4000)
  top_pady4.SetTopMargin(0.1)
  top_pady4.SetBottomMargin(0.2)
  top_pady4.SetGridx(1)
  gr_LEMI_down = ROOT.TGraph(len(zoom), zoom, LEMI_down)
  gr_LEMI_down.Draw("ALY+")
  gr_LEMI_down.SetMinimum(0)
  gr_LEMI_down.SetMaximum(maxI*1.1)  
#  gr_LEMI_down.SetMaximum(max(gridI)*1.1)  
  gr_LEMI_down.SetTitle("")
  gr_LEMI_down.SetLineWidth(3)
  gr_LEMI_down.SetLineColorAlpha(ROOT.kBlue, 0.35)
  gr_LEMI_down.GetXaxis().SetLabelSize(0)
  gr_LEMI_down.GetXaxis().SetLimits(zoom[0], zoom[-1])
  gr_LEMI_down.GetXaxis().SetNdivisions(10,4,0,ROOT.kFALSE)
  gr_LEMI_down.GetYaxis().SetLabelSize(0)
  leg.AddEntry(gr_LEMI_down,"LEM down Current","l")
  c1.cd()
  #
  top_pady2 = ROOT.TPad("top_pady2", "top_pady2",0,0.10, 1.0, 0.56)
  top_pady2.Draw()
  top_pady2.cd()
  top_pady2.SetFillStyle(4000)
  top_pady2.SetFillColor(0)
  top_pady2.SetFrameFillStyle(4000)
  top_pady2.SetTopMargin(0.1)
  top_pady2.SetBottomMargin(0.2)
  top_pady2.SetGridx(1)
  gr_level = ROOT.TGraph(len(zoom), zoom, gridI)
  gr_level.Draw("ALY+")
  gr_level.SetMinimum(0)
#  gr_level.SetMaximum(max(gridI)*1.1)
  gr_level.SetMaximum(maxI*1.1)
  gr_level.GetYaxis().SetLabelSize(0.1)
  gr_level.GetYaxis().SetTitle("Current [uA]")
  gr_level.GetYaxis().SetTitleOffset(0.6)
  gr_level.GetYaxis().SetTitleSize(gr_level.GetYaxis().GetTitleSize()*2.5)
  gr_level.SetLineWidth(3)
  gr_level.SetLineColorAlpha(ROOT.kGreen+2, 0.35)
  gr_level.SetTitle("")
  gr_level.GetXaxis().SetLabelSize(0.1)
  gr_level.GetXaxis().SetLimits(zoom[0], zoom[-1])
  gr_level.GetXaxis().SetLabelOffset(0.05)
  gr_level.GetXaxis().SetTimeDisplay(1)
  gr_level.GetXaxis().SetTimeFormat("%H: %M %F1970-01-01 00:00:00")
  gr_level.GetXaxis().SetNdivisions(10,4,0,ROOT.kFALSE)
  gr_level.GetYaxis().SetLabelSize(0.1)
  gr_level.GetYaxis().SetTitle("Current [uA]")
  leg.AddEntry(gr_level, "Grid Current", "l")
  c1.cd()
  #
  #  
  bottom_pady3 = ROOT.TPad("bottom_pady3", "bottom_pady3",0,0.57, 1.0, 1.0)
  bottom_pady3.Draw()
  bottom_pady3.cd()
  bottom_pady3.SetFillStyle(4000)
  bottom_pady3.SetFillColor(0)
  bottom_pady3.SetFrameFillStyle(4000)
  bottom_pady3.SetTopMargin(0.1)
  bottom_pady3.SetBottomMargin(0.05)
  bottom_pady3.SetGrid()
  gr_LEMV_up = ROOT.TGraph(len(zoom), zoom, LEMV_up)
  gr_LEMV_up.Draw("AL")
  gr_LEMV_up.SetTitle(LEM_name + " up " + date)
  gr_LEMV_up.SetLineWidth(3)
  gr_LEMV_up.SetMinimum(0)
  gr_LEMV_up.SetMaximum(max(LEMV_up)*1.1)
  gr_LEMV_up.GetYaxis().SetLabelSize(0.1)
  gr_LEMV_up.GetYaxis().SetTitle("Voltage [V]")
  gr_LEMV_up.GetYaxis().SetTitleOffset(0.6)
  gr_LEMV_up.GetYaxis().SetTitleSize(gr_LEMV_up.GetYaxis().GetTitleSize()*2.5)
  gr_LEMV_up.GetXaxis().SetLabelSize(0)
  gr_LEMV_up.GetXaxis().SetLimits(zoom[0], zoom[-1])
  gr_LEMV_up.GetXaxis().SetNdivisions(10,4,0,ROOT.kFALSE)
  gr_LEMV_up.SetLineColor(ROOT.kBlack)
  leg.AddEntry(gr_LEMV_up,"LEM up Voltage","l")
  c1.cd()
  #
  bottom_pady4 = ROOT.TPad("bottom_pady4", "bottom_pady4",0,0.57, 1.0, 1.0)
  bottom_pady4.Draw()
  bottom_pady4.cd()
  bottom_pady4.SetFillStyle(4000)
  bottom_pady4.SetFillColor(0)
  bottom_pady4.SetFrameFillStyle(4000)
  bottom_pady4.SetTopMargin(0.1)
  bottom_pady4.SetBottomMargin(0.05)
  bottom_pady4.SetGridx(1)
  gr_LEMI_up = ROOT.TGraph(len(zoom), zoom, LEMI_up)
  gr_LEMI_up.Draw("ALY+")
  gr_LEMI_up.SetTitle("")
  gr_LEMI_up.GetYaxis().SetLabelSize(0.1)
  gr_LEMI_up.GetYaxis().SetTitle("Current [uA]")
  gr_LEMI_up.GetYaxis().SetTitleOffset(0.6)
  gr_LEMI_up.GetYaxis().SetTitleSize(gr_LEMI_up.GetYaxis().GetTitleSize()*2.5)
  gr_LEMI_up.SetMinimum(0)
  gr_LEMI_up.SetMaximum(max(LEMI_up)*1.1)
#  gr_LEMI_up.SetMaximum(max(gridI)*1.1)
  gr_LEMI_up.SetLineWidth(3)
  gr_LEMI_up.SetLineColorAlpha(ROOT.kOrange, 0.8)
  gr_LEMI_up.GetXaxis().SetLimits(zoom[0], zoom[-1])
  gr_LEMI_up.GetXaxis().SetNdivisions(10,4,0,ROOT.kFALSE)
  gr_LEMI_up.GetXaxis().SetTitle("")
  gr_LEMI_up.GetXaxis().SetLabelSize(0)
  c1.cd()

  leg.AddEntry(gr_LEMI_up,"LEM up current","l")
  leg.SetTextSize(leg.GetTextSize()*0.2)
  leg.Draw()
  c1.SetLeftMargin(0.1)
  c1.SaveAs(path + LEM_name + "_" + date + ".pdf")
  c1.SaveAs(path + LEM_name + "_" + date + ".root")
  c1.Close()
  
  return 0
   
##############################################################################################
# Level & LEM current
##############################################################################################


def plot_Box(time, date, Box, reference_level, level_name, reference_name, tmin = 0, tmax = 0, LEM_1 = "LEM_NUMBER_1"):
  
  if((tmin == 0) & (tmax == 1)):
    tmin = time[0]
    tmax = tmin + time[len(time) - 1]
  zoom = time[(time >= tmin) & (time <= tmax)]
  cathode_voltage = Box[0][(time >= tmin) & (time <= tmax)]
  cathode_current = Box[1][(time >= tmin) & (time <= tmax)]
  grid_voltage = Box[2][(time >= tmin) & (time <= tmax)]
  grid_current = Box[3][(time >= tmin) & (time <= tmax)]
  level = Box[4][(time >= tmin) & (time <= tmax)]
  #level_abs = Box[4][(time >= tmin) & (time <= tmax)]
  #reference = reference_level[(time >= tmin) & (time <= tmax)]
  #level = numpy.array(numpy.array(reference) - numpy.array(level_abs))
  LEM_1_Up_I = Box[5][(time >= tmin) & (time <= tmax)]
  LEM_1_Down_I = Box[6][(time >= tmin) & (time <= tmax)]
  LEM_1_Up_V = Box[7][(time >= tmin) & (time <= tmax)]
  LEM_1_Down_V = Box[8][(time >= tmin) & (time <= tmax)]
  max_V_tmp = [max(cathode_voltage), max(grid_voltage), max(LEM_1_Up_V), max(LEM_1_Down_V)]
  max_V = max(max_V_tmp)
  max_I_tmp = [max(cathode_current), max(grid_current), max(LEM_1_Up_I), max(LEM_1_Down_I)]
  max_I = max(max_I_tmp)
  max_I_LEM_Up=max(LEM_1_Up_I)
  max_I_LEM_Down=max(LEM_1_Down_I)  
  
  leg = ROOT.TLegend(0,0,1,0.1)
  leg.SetNColumns(5)
  
  c1 = ROOT.TCanvas("c1","c1",2200,1200)
  #
  top_pady1 = ROOT.TPad("top_pady1", "top_pady1",0,0.71, 1.0, 1.0)
  top_pady1.Draw()
  top_pady1.cd()
  top_pady1.SetTopMargin(0.1)
  top_pady1.SetBottomMargin(0.01)
  top_pady1.SetGrid()
  gr_LEM_1_Up_I = ROOT.TGraph(len(zoom), zoom, LEM_1_Up_I)
  gr_LEM_1_Up_I.Draw("AL")
  gr_LEM_1_Up_I.SetTitle("LEM's Upper side" + "_" + date)
  gr_LEM_1_Up_I.SetLineWidth(3)
  gr_LEM_1_Up_I.SetLineColor(ROOT.kBlue)
  leg.AddEntry(gr_LEM_1_Up_I,LEM_1 + "_Up_current","l")
  gr_LEM_1_Up_I.GetYaxis().SetLabelSize(0.1)
  c1.cd()
  #
  top_pady2 = ROOT.TPad("top_pady2", "top_pady2",0,0.71, 1.0, 1.0)
  top_pady2.Draw()
  top_pady2.cd()
  top_pady2.SetFillStyle(4000)
  top_pady2.SetFillColor(0)
  top_pady2.SetFrameFillStyle(4000)
  top_pady2.SetTopMargin(0.1)
  top_pady2.SetBottomMargin(0.01)
  gr_level_top = ROOT.TGraph(len(zoom), zoom, level)
  gr_level_top.Draw("ALY+")
  gr_level_top.SetMinimum(0)
  gr_level_top.SetMaximum(25)
  gr_level_top.SetLineWidth(3)
  gr_level_top.SetLineColor(ROOT.kRed)
  gr_level_top.SetTitle("")
  gr_level_top.GetYaxis().SetLabelSize(0.1)
  c1.cd()
  #
  #
  middle_pady1 = ROOT.TPad("middle_pady1", "middle_pady1",0,0.43, 1.0, 0.71)
  middle_pady1.Draw()
  middle_pady1.cd()
  middle_pady1.SetTopMargin(0)
  middle_pady1.SetBottomMargin(0.01)
  middle_pady1.SetGrid()
  gr_LEM_1_Down_I = ROOT.TGraph(len(zoom), zoom, LEM_1_Down_I)
  gr_LEM_1_Down_I.Draw("AL")
  gr_LEM_1_Down_I.SetTitle("LEM's_Down_side" + "_" + date)
  gr_LEM_1_Down_I.SetLineWidth(3)
  gr_LEM_1_Down_I.GetYaxis().SetLabelSize(0.1)
  gr_LEM_1_Down_I.GetYaxis().SetTitle("Current [uA]")
  gr_LEM_1_Down_I.GetYaxis().SetTitleOffset(0.5)
  gr_LEM_1_Down_I.GetYaxis().SetTitleSize(gr_LEM_1_Down_I.GetYaxis().GetTitleSize()*2.5)
  gr_LEM_1_Down_I.GetXaxis().SetLabelSize(0)
  gr_LEM_1_Down_I.SetLineColor(ROOT.kCyan+1)
  leg.AddEntry(gr_LEM_1_Down_I,LEM_1+"_Down_current","l")
  c1.cd()
  #
  middle_pady2 = ROOT.TPad("middle_pady2", "middle_pady2",0,0.43, 1.0, 0.71)
  middle_pady2.Draw()
  middle_pady2.cd()
  middle_pady2.SetFillStyle(4000)
  middle_pady2.SetFillColor(0)
  middle_pady2.SetFrameFillStyle(4000)
  middle_pady2.SetTopMargin(0)
  middle_pady2.SetBottomMargin(0.01)
  gr_level_middle = ROOT.TGraph(len(zoom), zoom, level)
  gr_level_middle.SetLineWidth(3)
  gr_level_middle.SetLineColor(ROOT.kRed)
  gr_level_middle.SetTitle("")
  #leg.AddEntry(gr_level_middle,reference_name + "-" + level_name,"l")
  leg.AddEntry(gr_level_middle,level_name,"l")
  gr_level_middle.Draw("ALY+")
  gr_level_middle.SetMinimum(0)
  gr_level_middle.SetMaximum(25)
  gr_level_middle.GetYaxis().SetLabelSize(0.1)
  #gr_level_middle.GetYaxis().SetTitle(reference_name + "-" + level_name + " [mm]")
  gr_level_middle.GetYaxis().SetTitle(level_name + " [mm]")
  gr_level_middle.GetYaxis().SetTitleOffset(0.5)
  gr_level_middle.GetYaxis().SetTitleSize(gr_level_middle.GetYaxis().GetTitleSize()*2.5)
  gr_level_middle.GetXaxis().SetLabelSize(0)  
  c1.cd()
  #
  #
  bottom_pady1 = ROOT.TPad("bottom_pady1", "bottom_pady1",0,0.1, 1.0, 0.43)
  bottom_pady1.Draw()
  bottom_pady1.cd()
  bottom_pady1.SetTopMargin(0)
  bottom_pady1.SetBottomMargin(0.2)
  bottom_pady1.SetGrid()
  gr_grid_voltage = ROOT.TGraph(len(zoom), zoom, grid_voltage)
  gr_grid_voltage.Draw("AL")
  gr_grid_voltage.SetTitle("")
  gr_grid_voltage.GetYaxis().SetLabelSize(0.1)
  gr_grid_voltage.GetYaxis().SetTitle("Voltage [V]")
  gr_grid_voltage.GetYaxis().SetTitleOffset(0.5)
  gr_grid_voltage.GetYaxis().SetTitleSize(gr_grid_voltage.GetYaxis().GetTitleSize()*2.5)
  gr_grid_voltage.SetMaximum(max_V*1.2)
  gr_grid_voltage.SetLineWidth(3)
  gr_grid_voltage.SetLineColor(ROOT.kYellow+2)
  gr_grid_voltage.GetXaxis().SetTimeDisplay(1)
  gr_grid_voltage.GetXaxis().SetTimeFormat("%H: %M: %S %F1970-01-01 00:00:00")
  gr_grid_voltage.GetXaxis().SetTitle("")
  gr_grid_voltage.GetXaxis().SetTitleSize(gr_grid_voltage.GetXaxis().GetTitleSize()*2.5)
  gr_grid_voltage.GetXaxis().SetTitleOffset(0.5)
  gr_grid_voltage.GetXaxis().SetLabelOffset(0.05)
  gr_grid_voltage.GetXaxis().SetLabelSize(0.1)
  leg.AddEntry(gr_grid_voltage,"Grid voltage","l")
  #gr_cathode_voltage = ROOT.TGraph(len(zoom), zoom, cathode_voltage)
  #gr_cathode_voltage.Draw("SAME")
  #gr_cathode_voltage.SetTitle("")
  #gr_cathode_voltage.GetXaxis().SetLabelSize(0)
  #gr_cathode_voltage.SetLineWidth(3)
  #gr_cathode_voltage.SetLineColor(ROOT.kYellow)
  #leg.AddEntry(gr_cathode_voltage,"Cathode voltage","l")  
  #gr_LEM_1_Up_V = ROOT.TGraph(len(zoom), zoom, LEM_1_Up_V)
  #gr_LEM_1_Up_V.Draw("SAME")
  #gr_LEM_1_Up_V.SetTitle("")
  #gr_LEM_1_Up_V.GetXaxis().SetLabelSize(0)
  #gr_LEM_1_Up_V.SetLineWidth(3)
  #gr_LEM_1_Up_V.SetLineColor(ROOT.kGreen)
  #leg.AddEntry(gr_LEM_1_Up_V,LEM_1 + "_Up_voltage","l")
  gr_LEM_1_Down_V = ROOT.TGraph(len(zoom), zoom, LEM_1_Down_V)
  gr_LEM_1_Down_V.Draw("SAME")
  gr_LEM_1_Down_V.SetLineWidth(3)
  gr_LEM_1_Down_V.SetLineColor(ROOT.kGreen-2)
  leg.AddEntry(gr_LEM_1_Down_V,LEM_1 + "_Down_voltage","l")
  c1.cd()
  #bottom_pady2 = ROOT.TPad("bottom_pady2", "bottom_pady2",0,0.1, 1.0, 0.43)
  #bottom_pady2.Draw()
  #bottom_pady2.cd()
  #bottom_pady2.SetFillStyle(4000)
  #bottom_pady2.SetFillColor(0)
  #bottom_pady2.SetFrameFillStyle(4000)
  #bottom_pady2.SetTopMargin(0)
  #bottom_pady2.SetBottomMargin(0.2)
  #gr_cathode_current = ROOT.TGraph(len(zoom), zoom, cathode_current)
  #gr_cathode_current.Draw("ALY+")
  #gr_cathode_current.SetMaximum(max_I*1.1)
  #gr_cathode_current.SetTitle("")
  #gr_cathode_current.GetYaxis().SetLabelSize(0.1)
  #gr_cathode_current.SetLineWidth(3)
  #gr_cathode_current.SetLineColor(ROOT.kMagenta+2)
  #leg.AddEntry(gr_cathode_current,"Cathode current","l")
  #gr_grid_current = ROOT.TGraph(len(zoom), zoom, grid_current)  
  #gr_grid_current.Draw("SAME")
  #gr_grid_current.SetLineWidth(3)
  #gr_grid_current.SetLineColor(ROOT.kMagenta-4)
  #leg.AddEntry(gr_grid_current,"Grid current","l")
  #c1.cd()
  #
  #
  #
  #
  leg.SetTextSize(leg.GetTextSize()*0.2)
  leg.Draw()
  c1.SetLeftMargin(0.1)
  c1.SaveAs("./" + sys.argv[4] + "/Box/" + level_name + "_" + LEM_1 + "_" + date + ".pdf")
  c1.SaveAs("./" + sys.argv[4] + "/Box/" + level_name + "_" + LEM_1 + "_" + date + ".root")
  c1.Close()
  
  return 0
  
  
  
