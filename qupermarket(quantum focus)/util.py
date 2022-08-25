
"""tools for calculating"""
import copy
import itertools
import functools
import multiprocessing as mp
import string
import re
from collections import OrderedDict, defaultdict, namedtuple
from typing import (
    Union,
    Optional,
    List,
    Dict,
    Tuple,
    Type,
    TypeVar,
    Sequence,
    Callable,
    Mapping,
    Set,
    Iterable,
)
import typing
import numpy as np



def minbattery(mdb:int = None,ab:int = None,cbc:int = None)->int:
    """calculate minimal_battery for each car
    
    Args:
        mdb(int)：minimal departure battery
        ab(int): arrival battery
        cpc(int): car battery capacity
    Return:
        int: minimal_battery
    """
    return (mdb -ab)* cbc

def mintime(dt:int = None,at:int = None)->int:
    """calculate minimal time for each car
    
    Args:
        dt(int)：departure time
        at(int): arrival time
    Return:
        int: minimal_time
    """
    return dt - at

def closing_consumption(csh:int = None,ctw_list:list= None)->int:
    """calculate closing consumption
    
    Args:
        csh(int)：closing_shop_hour
        ctw_list(list): closing_total_weather_kW(production)
    Return:
        int: closing_consumption
    """
    
    sum_csh = csh*24
    
    sum_ctw = 0
    for i in ctw_list:
        if i == "Night":
            pass
        if i == "Rain":
            sum_ctw += 50
        if i == "Cloudy":
            sum_ctw += 80
        if i == "Sun":
            sum_ctw += 180
    print("sum_closing_shop_hour",sum_csh,"closing_total_weather_kW",sum_ctw)
    
    
    return sum_csh - sum_ctw

def open_consumption(stbc:int = None, osc:int = 120, otw:list = None)->int:
    """calculate open consumption
    
    Args:
        stbc(int)：sum of total_battery_charge from car
        osc(int): opening_shop_consumption(production)
        otw(list): opening_total_weather_kW(production)
    Return:
        int: open consumption
    """
    sum_otw = 0
    for i in otw:
        if i == "Night":
            pass
        if i == "Rain":
            sum_otw += 50
        if i == "Cloudy":
            sum_otw += 80
        if i == "Sun":
            sum_otw += 180
    return (stbc + osc) - sum_otw

def future_consumption(csc,ctw,stbc,ohc,otw):
    """calculate future comsuption
    
    Args:
        csc(int)：closing_shop_consumption
        ctw(int): closing_total_weather_kW(production)
        stbc(int)：sum of total_battery_charge
        ohc(int): opening_shop_consumption(production)
        otw(int): opening_total_weather_kW(production)
    Return:
        int: future comsuption
    """
    return closing_consumption(csc,ctw) - open_consumption(stbc,ohc,otw)


