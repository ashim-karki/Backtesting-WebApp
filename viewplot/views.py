from django.shortcuts import render

# Create your views here.

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_agg import FigureCanvasAgg
from django.http import HttpResponse

def plot(request):
    # Data for plotting
    t = np.arange(0.0, 1.0, 0.14)
    s = 1 + np.sin(2 * np.pi*2 * t)

    fig, ax = plt.subplots()
    ax.plot(t, s)

    ax.set(xlabel='time (s)', ylabel='voltage (mV)',
           title='About as simple as it gets, folks')
    ax.grid()

    response = HttpResponse(content_type = 'image/png')
    canvas = FigureCanvasAgg(fig)
    canvas.print_png(response)
    return response 