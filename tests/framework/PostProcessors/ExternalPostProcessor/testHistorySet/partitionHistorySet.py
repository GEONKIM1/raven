
import numpy as np
import math

def time(self):
  for history in range(len(self.time)):
    for ts in range(len(self.time[history])):
      if self.time[history][ts] >= 0.001:
        break
    self.time[history] = self.time[history][ts:]
  return self.time

def x(self):
  for history in range(len(self.time)):
    for ts in range(len(self.time[history])):
      if self.time[history][ts] >= 0.001:
        break
    self.x[history] = self.x[history][ts:]
  return self.x

def y(self):
  for history in range(len(self.time)):
    for ts in range(len(self.time[history])):
      if self.time[history][ts] >= 0.001:
        break
    self.y[history] = self.y[history][ts:]
  return self.y

def z(self):
  for history in range(len(self.time)):
    for ts in range(len(self.time[history])):
      if self.time[history][ts] >= 0.001:
        break
    self.z[history] = self.z[history][ts:]
  return self.z