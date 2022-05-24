#!/usr/bin/env python3

from datetime import datetime, timedelta

def roundups(dt):
    roundup = dt + (datetime.min - dt) % timedelta(minutes=5)
    return roundup

def rounddos(dt):
    rounddo = dt - (dt - datetime.min) % timedelta(minutes=5)
    return rounddo 
