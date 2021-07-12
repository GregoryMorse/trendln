import numpy as np
#exec(open(r'D:\OneDrive\documents\Projects\trader\trendln\trendln\__init__.py').read())

def datefmt(xdate, cal=None):
    from pandas.tseries.holiday import AbstractHolidayCalendar, Holiday, nearest_workday, \
        USMartinLutherKingJr, USPresidentsDay, GoodFriday, USMemorialDay, \
        USLaborDay, USThanksgivingDay
    from pandas.tseries.offsets import CustomBusinessDay
    class USTradingCalendar(AbstractHolidayCalendar):
        rules = [
            Holiday('NewYearsDay', month=1, day=1, observance=nearest_workday),
            USMartinLutherKingJr,
            USPresidentsDay,
            GoodFriday,
            USMemorialDay,
            Holiday('USIndependenceDay', month=7, day=4, observance=nearest_workday),
            USLaborDay,
            USThanksgivingDay,
            Holiday('Christmas', month=12, day=25, observance=nearest_workday)
        ]
    if cal == None: cal = USTradingCalendar()
    def mydate(x,pos):
        #print((x,pos))
        val = int(x + 0.5)
        if val < 0: return (xdate[0].to_pydatetime() - CustomBusinessDay(-val, calendar=cal)).strftime('%Y-%m-%d')
        elif val >= len(xdate): return (xdate[-1].to_pydatetime() + CustomBusinessDay(val - len(xdate) + 1, calendar=cal)).strftime('%Y-%m-%d')
        else: return xdate[val].strftime('%Y-%m-%d')
    return mydate

def plot_sup_res_learn(curdir, hist):
    import os
    if not os.path.isdir(os.path.join(curdir, 'data')): os.mkdir(os.path.join(curdir, 'data')) #image folder
    import pandas as pd
    import matplotlib.pyplot as plt
    import matplotlib.ticker as ticker
    #for x in plt.get_fignums(): plt.close(plt.figure(x)) #clean up when crashes occur and figures left open
    #plt.get_backend(): 'TkAgg' is default
    hist = hist[:'2019-10-07']
    def fig_slopeint():
        plt.clf()
        plt.rcParams.update({'font.size': 14})
        plt.gcf().set_size_inches(1000/plt.gcf().dpi, 1000/plt.gcf().dpi) #plt.gcf().dpi=100
        spec = gridspec.GridSpec(ncols=1, nrows=2, figure=plt.gcf(), height_ratios=[3, 1])
        plt.subplot(spec[1, 0])
        plt.axis('off')
        plt.gca().get_xaxis().set_visible(False)
        plt.gca().get_yaxis().set_visible(False)
        plt.annotate(r'Standard slope-intercept line equation: $f(x)=y=mx+b$' + '\n'
                           r'For 2 points $(x_0, y_0), (x_1, y_1)$:' + '\n' +
                           r'Slope derived from two points: $m=\frac{\Delta y}{\Delta x}=\frac{y_0-y_1}{x_0-x_1}$' + '\n' +
                           r'Intercept derived from slope and point: $b=y_0-mx_0=y_1-mx_1$' + '\n' +
                           r'Y-axis Distance to point from line: $d=\left|mx_2+b-y_2\right|$' + '\n' +
                           r'''Pythagorean's Theorem for Right Triangles: $c^2=a^2+b^2\equiv$ $d^2=\Delta x^2+\Delta y^2$''' + '\n' +
                           r'Distance between Points: d=$\sqrt{(x_1-x_0)^2+(y_1-y_0)^2}$', (0, 0))
        plt.subplot(spec[0, 0])
        m = (hist.Close.iloc[-3] - hist.Close.iloc[-1]) / -2
        b1, b2 = hist.Close.iloc[-1] - m * 2, hist.Close.iloc[-3] - m * 0
        d = abs(m * 1 + b1 - hist.Close.iloc[-2])
        dist = np.sqrt(np.square(hist.Close.iloc[-3] - hist.Close.iloc[-1]) + np.square(-2))
        height = hist.Close.iloc[-3:].max() - hist.Close.iloc[-3:].min()
        plt.plot(range(len(hist.Close)-3, len(hist.Close)), hist.Close.iloc[-3:])
        plt.yticks(hist.Close.iloc[-3:])
        plt.plot([len(hist.Close)-3, len(hist.Close)-1], [hist.Close.iloc[-3], hist.Close.iloc[-1]], 'g--')
        #perpendicular slope: 1/-m, intercept to midpoint b=y-mx: 
        #intcpt = (hist.Close.iloc[-3] + hist.Close.iloc[-1]) / 2 - (-1/m)

        ax = plt.gca()
        plt.ylim(ax.get_ylim()[0] - height * 0.1, ax.get_ylim()[1])
    #drawdim = plt.gcf().get_size_inches()*plt.gcf().dpi
        bbox = ax.get_window_extent()#.transformed(plt.gcf().dpi_scale_trans.inverted()) #convert pixels to points
        drawdim = [bbox.width, bbox.height]
        xaxwdt, yaxhgt = ax.get_xlim()[1] - ax.get_xlim()[0], ax.get_ylim()[1] - ax.get_ylim()[0]
        mvisual = (hist.Close.iloc[-3] - hist.Close.iloc[-1]) * drawdim[1] / yaxhgt / (-2 * drawdim[0] / xaxwdt) #scale is 2:yaxhgt, could use this in computations, but must do dynamically with event handler since draw scale changes
        #intcpt = (hist.Close.iloc[-3] - ax.get_ylim()[0]) * drawdim[1] / yaxhgt - mvisual * (0.1 * drawdim[0] / xaxwdt)
        #print((mvisual, intcpt, xaxwdt, yaxhgt, drawdim, ax.get_ylim()))
        #(len(hist.Close)-3, hist.Close.iloc[-3])
        #a = plt.annotate('', (0.1 * drawdim[0] / xaxwdt, mvisual * (0.1 * drawdim[0] / xaxwdt) + intcpt), (2.1 * drawdim[0] / xaxwdt, mvisual * (2.1 * drawdim[0] / xaxwdt) + intcpt), xycoords='axes pixels', textcoords='axes pixels', arrowprops={'arrowstyle':'-['})
        intcpt = ((hist.Close.iloc[-3] + hist.Close.iloc[-1]) / 2 - ax.get_ylim()[0]) * drawdim[1] / yaxhgt - (-(drawdim[0] / 2) / mvisual)
        ann = plt.annotate(r'$d=\sqrt{{({}-{})^2+({}-{})^2}}={}$'.format(hist.Close.iloc[-3], hist.Close.iloc[-1], 0, 2, round(dist, 2)), (len(hist.Close)-2, (hist.Close.iloc[-3] + hist.Close.iloc[-1]) / 2), ax.transData.inverted().transform(((drawdim[0] * 0.54)+bbox.x0, (-(drawdim[0] * 0.54)/mvisual + intcpt)+bbox.y0)), textcoords='data', color='green', ha='center', va='center', arrowprops={'arrowstyle':'-[', 'color':'green'})
    #print(drawdim, ann.xyann, mvisual, intcpt, ax.get_xlim())
        plt.annotate(r'$b={}-{}*{}={}-{}*{}={}$'.format(hist.Close.iloc[-1], round(m, 2), 2, hist.Close.iloc[-3], round(m, 2), 0, b1), (len(hist.Close)-3, hist.Close.iloc[-3]), (len(hist.Close)-3, hist.Close.iloc[-3] - height*0.1), arrowprops={'arrowstyle':'->'})
        plt.plot([len(hist.Close)-2, len(hist.Close)-2], [m * 1 + b1, hist.Close.iloc[-2]], 'r--')
        plt.annotate((r'$d=$' + '\n' + r'$\left|{}*{}+{}-{}\right|$' + '\n' + r'$={}$').format(round(m, 2), 1, b1, hist.Close.iloc[-2], round(d, 2)), (len(hist.Close)-2, (m * 1 + b1 + hist.Close.iloc[-2]) / 2), (len(hist.Close)-2+0.1, (m * 1 + b1 + hist.Close.iloc[-2]) / 2), va='center', color='red', arrowprops={'arrowstyle':'-[', 'color':'red'})
        plt.annotate(r'$m=\frac{{{}}}{{{}}}={}$'.format(round(hist.Close.iloc[-3] - hist.Close.iloc[-1], 2), 0 - 2, round(m, 2)), (len(hist.Close)-2, (hist.Close.iloc[-3] + hist.Close.iloc[-1]) / 2), (len(hist.Close)-2+0.2, (hist.Close.iloc[-3] + hist.Close.iloc[-1]) / 2 - height * 0.1), color='black', arrowprops={'arrowstyle':'->'})
        plt.plot([len(hist.Close)-3, len(hist.Close)-1], [hist.Close.iloc[-3], hist.Close.iloc[-3]], 'c--')
        plt.annotate(r'$\Delta x={}-{}={}$'.format(0, 2, 0 - 2), (len(hist.Close)-2, hist.Close.iloc[-3]), (len(hist.Close)-2, hist.Close.iloc[-3] + height * 0.10), color='cyan', ha='center', va='center', arrowprops={'arrowstyle':'-[', 'color':'cyan'})
        plt.plot([len(hist.Close)-1, len(hist.Close)-1], [hist.Close.iloc[-3], hist.Close.iloc[-1]], 'c--')
        plt.annotate(r'$\Delta y={}-{}={}$'.format(hist.Close.iloc[-3], hist.Close.iloc[-1], round(hist.Close.iloc[-3] - hist.Close.iloc[-1], 2)), (len(hist.Close)-1, (hist.Close.iloc[-3] + hist.Close.iloc[-1]) / 2), (len(hist.Close)-2+0.5, (hist.Close.iloc[-3] + hist.Close.iloc[-1]) / 2), color='cyan', ha='center', va='center', arrowprops={'arrowstyle':'-[', 'color':'cyan'})

        plt.title('Closing Price Points Demonstrating Line Calculations')
        plt.xlabel('Date')
        plt.ylabel('Price')
        ax.xaxis.set_major_locator(ticker.IndexLocator(1, 0))
    #ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        ax.xaxis.set_major_formatter(ticker.FuncFormatter(datefmt(hist.index)))
        plt.setp(ax.get_xticklabels(), rotation=30, ha='right')
    #plt.axis('equal')
        def redraw(event):
        #cxaxwdt, cyaxhgt = ax.get_xlim()[1] - ax.get_xlim()[0], ax.get_ylim()[1] - ax.get_ylim()[0]
            bbox = ax.get_window_extent()#.transformed(plt.gcf().dpi_scale_trans.inverted())
            drawdim = [bbox.width, bbox.height]
            mvisual = (hist.Close.iloc[-3] - hist.Close.iloc[-1]) * drawdim[1] / yaxhgt / (-2 * drawdim[0] / xaxwdt)
            intcpt = ((hist.Close.iloc[-3] + hist.Close.iloc[-1]) / 2 - ax.get_ylim()[0]) * drawdim[1] / yaxhgt - (-(drawdim[0] / 2) / mvisual)
        #print(drawdim, ann.xyann, mvisual, intcpt, ax.get_xlim())
            ann.xyann = ax.transData.inverted().transform(((drawdim[0] * 0.54)+bbox.x0, (-(drawdim[0] * 0.54)/mvisual + intcpt)+bbox.y0))
            plt.gcf().canvas.draw_idle()
    #idx = ax.callbacks.connect('xlim_changed', redraw)
    #idy = ax.callbacks.connect('ylim_changed', redraw)
        cid = plt.gcf().canvas.mpl_connect('resize_event', redraw)
        plt.tight_layout()
    #plt.gcf().canvas.draw()
    #redraw(None)
    #plt.gcf().canvas.draw()
    #extent = plt.gcf().get_window_extent(renderer=plt.gcf().canvas.get_renderer()).transformed(plt.gcf().dpi_scale_trans.inverted())
        plt.savefig(os.path.join(curdir, 'data', 'slopeint.svg'), format='svg')#, bbox_inches = extent, pad_inches = 0)
        plt.savefig(os.path.join(curdir, 'data', 'slopeint.png'), format='png')#, bbox_inches = extent, pad_inches = 0)
    #plt.show()
        plt.gcf().canvas.mpl_disconnect(cid)
    #ax.callbacks.disconnect(idx)
    #ax.callbacks.disconnect(idy)

    def fig_linregrs():
        plt.clf()
        plt.rcParams.update({'font.size': 14})
        plt.gcf().set_size_inches(1024/plt.gcf().dpi, 768/plt.gcf().dpi) #plt.gcf().dpi=100
        spec = gridspec.GridSpec(ncols=1, nrows=2, figure=plt.gcf(), height_ratios=[3, 1])
        plt.subplot(spec[1, 0])
        plt.axis('off')
        plt.gca().get_xaxis().set_visible(False)
        plt.gca().get_yaxis().set_visible(False)
        plt.annotate(r'Mean of n-Points along x and y-axes: $\bar{x}=\frac{\sum_{i=1}^n{x_i}}{n}, \bar{y}=\frac{\sum_{i=1}^n{y_i}}{n}$' + '\n' +
                           r'Regression slope: $m=\frac{\sum_{i=1}^n(x_i-\bar{x})(y_i-\bar{y})}{\sum_{i=1}^n(x_i-\bar{x})^2}$' + '  ' +
                           r'Regression intercept: $b=\bar{y}-m\bar{x}$' + '\n' +
                           r'Sum of Squared Residuals for expected $y_i$ $(\hat{y}_i)$: $SSR=\sum_{i=1}^n{(y_i-\hat{y}_i)^2}$' + '\n' +
                           r'Standard Error of Slope: $\sigma_m=\sqrt{\frac{SSR}{(n-2)\sum_{i=1}^n{(x_i-\bar{x})^2}}}$' + '  ' + 
                           r'Standard Error of Intercept: $\sigma_b=\sigma_m\sqrt{\frac{\sum_{i=1}^nx_i^2}{n}}$', (0, 0))
        plt.subplot(spec[0, 0])
        plt.plot(range(len(hist.Close)-3, len(hist.Close)), hist.Close.iloc[-3:], 'bo')
        xbar, ybar = (0 + 1 + 2) / 3, (hist.Close.iloc[-3] + hist.Close.iloc[-2] + hist.Close.iloc[-1]) / 3
        height = hist.Close.iloc[-3:].max() - hist.Close.iloc[-3:].min()
        plt.hlines(ybar, len(hist.Close)-3, len(hist.Close)-1, colors='r', linestyles='--')
        plt.annotate(r'$\bar{{x}}=\frac{{{}+{}+{}}}{{{}}}={}$'.format(0, 1, 2, 3, 1), (xbar + len(hist.Close)-3, (hist.Close.iloc[-3:].min() + hist.Close.iloc[-3:].max()) / 2), (xbar + len(hist.Close)-3, hist.Close.iloc[-3:].min()), color='red', va='center', arrowprops={'arrowstyle':'->', 'color':'red'})
        plt.vlines(xbar + len(hist.Close)-3, hist.Close.iloc[-3:].min(), hist.Close.iloc[-3:].max(), colors='r', linestyles='--')
        plt.annotate(r'$\bar{{y}}=\frac{{{}+{}+{}}}{{{}}}={}$'.format(hist.Close.iloc[-3], hist.Close.iloc[-2], hist.Close.iloc[-1], 3, round(ybar, 2)), (len(hist.Close)-2, ybar), (len(hist.Close)-1, ybar - height * 0.1), color='red', va='top', ha='right', arrowprops={'arrowstyle':'->', 'color':'red'})
        m = ((0 - xbar) * (hist.Close.iloc[-3] - ybar) + (1 - xbar) * (hist.Close.iloc[-2] - ybar) + (2 - xbar) * (hist.Close.iloc[-1] - ybar)) / (np.square(0-xbar)+np.square(1-xbar)+np.square(2-xbar))
        b = ybar - m * xbar
        SSR = np.square(hist.Close.iloc[-3] - (m * 0 + b)) + np.square(hist.Close.iloc[-2] - (m * 1 + b)) + np.square(hist.Close.iloc[-1] - (m * 2 + b))
        err1 = np.sqrt(SSR / ((3 - 2) * (np.square(0-xbar)+np.square(1-xbar)+np.square(2-xbar))))
        err2 = err1*np.sqrt((np.square(0)+np.square(1)+np.square(2))/3)
        plt.annotate(r'$\hat{{y}}_0={}*{}+{}={}$'.format(round(m, 2), 0, round(b, 2), round(m*0+b, 2)), (len(hist.Close) - 3, m*0+b), (len(hist.Close) - 3 + 0.1, m*0+b), va='top', arrowprops={'arrowstyle':'->'})
        plt.annotate(r'$\hat{{y}}_1={}*{}+{}={}$'.format(round(m, 2), 1, round(b, 2), round(m*1+b, 2)), (len(hist.Close) - 2, m*1+b), (len(hist.Close) - 2 + 0.15, m*1+b+height*0.01), arrowprops={'arrowstyle':'->'})
        plt.annotate(r'$\hat{{y}}_2={}*{}+{}={}$'.format(round(m, 2), 2, round(b, 2), round(m*2+b, 2)), (len(hist.Close) - 1, m*2+b), (len(hist.Close) - 1 - 0.1, m*2+b+height*0.1), ha='right', arrowprops={'arrowstyle':'->'})
        plt.plot([len(hist.Close) - 3, len(hist.Close) - 3], [hist.Close.iloc[-3], ybar], color='green')
        plt.plot([len(hist.Close) - 2, len(hist.Close) - 2], [hist.Close.iloc[-2], ybar], color='green')
        plt.plot([len(hist.Close) - 1, len(hist.Close) - 1], [hist.Close.iloc[-1], ybar], color='green')
        plt.annotate(r'$y_0-\bar{{y}}={}$'.format(round(hist.Close.iloc[-3] - ybar, 2)), (len(hist.Close) - 3, (hist.Close.iloc[-3] + ybar) / 2 + height * 0.1), (len(hist.Close) - 3 + 0.1, (hist.Close.iloc[-3] + ybar) / 2 + height * 0.1), color='green', va='center', arrowprops={'arrowstyle':'-[', 'color':'green'})
        plt.annotate(r'$y_1-\bar{{y}}={}$'.format(round(hist.Close.iloc[-2] - ybar, 2)), (len(hist.Close) - 2, (hist.Close.iloc[-2] + ybar) / 2 + height * 0.1), (len(hist.Close) - 2 + 0.1, (hist.Close.iloc[-2] + ybar) / 2 + height * 0.1), color='green', va='center', arrowprops={'arrowstyle':'-[', 'color':'green'})
        plt.annotate(r'$y_2-\bar{{y}}={}$'.format(round(hist.Close.iloc[-1] - ybar, 2)), (len(hist.Close) - 1, (hist.Close.iloc[-1] + ybar) / 2), (len(hist.Close) - 1 - 0.1, (hist.Close.iloc[-1] + ybar) / 2), color='green', va='center', ha='right', arrowprops={'arrowstyle':'-[', 'color':'green'})
        plt.plot([len(hist.Close) - 3, len(hist.Close) - 3], [hist.Close.iloc[-3], m*0+b], color='cyan')
        plt.plot([len(hist.Close) - 2, len(hist.Close) - 2], [hist.Close.iloc[-2], m*1+b], color='cyan')
        plt.plot([len(hist.Close) - 1, len(hist.Close) - 1], [hist.Close.iloc[-1], m*2+b], color='cyan')
        plt.annotate(r'$y_0-\hat{{y}}={}$'.format(round(hist.Close.iloc[-3] - (m*0+b), 2)), (len(hist.Close) - 3, (hist.Close.iloc[-3] + m*0+b) / 2), (len(hist.Close) - 3 + 0.1, (hist.Close.iloc[-3] + m*0+b) / 2), color='cyan', va='center', arrowprops={'arrowstyle':'-[', 'color':'cyan'})
        plt.annotate(r'$y_1-\hat{{y}}={}$'.format(round(hist.Close.iloc[-2] - (m*1+b), 2)), (len(hist.Close) - 2, (hist.Close.iloc[-2] + m*1+b) / 2), (len(hist.Close) - 2 + 0.1, (hist.Close.iloc[-2] + m*1+b) / 2), color='cyan', va='center', arrowprops={'arrowstyle':'-[', 'color':'cyan'})
        plt.annotate(r'$y_2-\hat{{y}}={}$'.format(round(hist.Close.iloc[-1] - (m*2+b), 2)), (len(hist.Close) - 1, (hist.Close.iloc[-1] + m*2+b) / 2 - height * 0.05), (len(hist.Close) - 1 - 0.1, (hist.Close.iloc[-1] + m*2+b) / 2 - height * 0.05), color='cyan', va='center', ha='right', arrowprops={'arrowstyle':'-[', 'color':'cyan'})
        plt.annotate((r'$m=\frac{{({}-{})*{}+({}-{})*{}+({}-{})*{}}}{{({}-{})^2+({}-{})^2+({}-{})^2}}$' + '\n' + '=${}$' + '\n' +
                     r'$SSR={}^2+{}^2+{}^2={}$' + '\n' +
                     r'$\sigma_m=\sqrt{{\frac{{{}}}{{({}-2)(({}-{})^2+({}-{})^2+({}-{})^2)}}}}={}$' + '\n' +
                     r'$\sigma_b={}\sqrt{{\frac{{{}^2+{}^2+{}^2}}{{{}}}}}={}$'
                     ).format(0, round(xbar, 2), round(hist.Close.iloc[-3] - ybar, 2), 1, round(xbar, 2), round(hist.Close.iloc[-2] - ybar, 2), 2, round(xbar, 2), round(hist.Close.iloc[-1] - ybar, 2), 0, round(xbar, 2), 1, round(xbar, 2), 2, round(xbar, 2), round(m, 2),
                             round(hist.Close.iloc[-3] - (m*0+b), 2), round(hist.Close.iloc[-2] - (m*1+b), 2), round(hist.Close.iloc[-1] - (m*2+b), 2), round(SSR, 2),
                             round(SSR, 2), 3, 0, round(xbar, 2), 1, round(xbar, 2), 2, round(xbar, 2), round(err1, 2),
                             round(err1, 2), 0, 1, 2, 3, round(err2, 2)),
                     (len(hist.Close)-2, m * 1 + b), (len(hist.Close)-1, hist.Close.iloc[-3:].min()), color='blue', va='bottom', ha='right', arrowprops={'arrowstyle':'->', 'color':'blue'})
        plt.annotate(r'$b={}-{}*{}={}$'.format(round(ybar, 2), round(m, 2), xbar, round(b, 2)), (len(hist.Close)-3, b), (len(hist.Close)-3+0.1, b), color='blue', ha='left', arrowprops={'arrowstyle':'->', 'color':'blue'})
        plt.plot([len(hist.Close)-3, len(hist.Close)-1], [b, 2 * m + b])
        ax = plt.gca()
        plt.yticks(hist.Close.iloc[-3:])
        plt.title('Closing Price Points Demonstrating Linear Regression')
        plt.xlabel('Date')
        plt.ylabel('Price')
        ax.xaxis.set_major_locator(ticker.IndexLocator(1, 0))
    #ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        ax.xaxis.set_major_formatter(ticker.FuncFormatter(datefmt(hist.index)))
        plt.setp(ax.get_xticklabels(), rotation=30, ha='right')
        plt.tight_layout()
    #extent = plt.gcf().get_window_extent(renderer=plt.gcf().canvas.get_renderer()).transformed(plt.gcf().dpi_scale_trans.inverted())
        plt.savefig(os.path.join(curdir, 'data', 'linregrs.svg'), format='svg')#, bbox_inches = extent, pad_inches = 0)
        plt.savefig(os.path.join(curdir, 'data', 'linregrs.png'), format='png')#, bbox_inches = extent, pad_inches = 0)
    #plt.show()

    def fig_hough():
        plt.clf()
        plt.rcParams.update({'font.size': 14})
        plt.gcf().set_size_inches(1280/plt.gcf().dpi, 1024/plt.gcf().dpi) #plt.gcf().dpi=100
        spec = gridspec.GridSpec(ncols=1, nrows=2, figure=plt.gcf(), height_ratios=[3, 1])
        plt.subplot(spec[1, 0])
        plt.axis('off')
        plt.gca().get_xaxis().set_visible(False)
        plt.gca().get_yaxis().set_visible(False)
        plt.annotate(r'Slope of Perpendicular Line: $m_p=-\frac{1}{m}, mm_p=-1$' + '\n' +
                           r'Perpencicular Line passing through Point: $y=\frac{x_0-x}{m}+y_0$' + '\n' +
                           r'Point $(x\prime, y\prime)$ of Intersection of Lines: $mx+b=\frac{x_0-x}{m}+y_0\equiv x\prime=\frac{x_0+my_0-mb}{m^2+1}, y\prime=mx\prime+b$' + '\n' +
                           r'Distance of Point to Line after simplification: $d=\frac{\left|b+mx_0-y_0\right|}{\sqrt{1 + m^2}}$' + '\n' +
                           r'$\rho=x \cos \theta+y \sin \theta$ where $\sin \theta=\frac{opposite}{hypotenuse}, \cos \theta=\frac{adjacent}{hypotenuse}$ and $y=\frac{\sin \theta}{\cos \theta}x$ while its perpendicular line is $y=-\frac{\cos \theta}{\sin \theta}x+\frac{\rho}{\sin \theta}$', (0, 0))
        plt.subplot(spec[0, 0])
        plt.plot([len(hist.Close)-10, len(hist.Close)-1], [hist.Close.iloc[-10], hist.Close.iloc[-1]], 'ro')
        plt.plot([len(hist.Close)-10, len(hist.Close)-1], [hist.Close.iloc[-10], hist.Close.iloc[-1]], 'k-')
        mn, mx = min(hist.Close.iloc[-10], hist.Close.iloc[-1]), max(hist.Close.iloc[-10], hist.Close.iloc[-1])
        plt.plot([len(hist.Close)-10, len(hist.Close)-1], [mn, mx], 'b--')
        plt.annotate(r'Diagonal length=$\sqrt{{{}^2+{}^2}}={}$'.format(9, round(mx-mn, 2), round(np.sqrt(np.square(9)+np.square(mx-mn)), 2)), (len(hist.Close)-1, mx), (len(hist.Close)-1-1, mx), ha='right', va='top', color='blue', arrowprops={'arrowstyle':'->', 'color':'blue'})
        #plt.xlim(0, 30)
        #plt.ylim(0, 30)
        #plt.gca().add_line(plt.Line2D([0, 30], [30, 0]))
        #height = hist.Close.iloc[-10:].max() - hist.Close.iloc[-10:].min()
        ax = plt.gca()
    #plt.ylim(ax.get_ylim()[0] - height * 0.2, ax.get_ylim()[1])
    #plt.xlim(ax.get_xlim()[0] - 4, ax.get_xlim()[1])
        m = (hist.Close.iloc[-10] - hist.Close.iloc[-1]) / (0 - 9)
        b = hist.Close.iloc[-10] - m * 0 - mn #+ height * 0.2
        plt.annotate(r'$y={}x+{}$'.format(round(m, 2), round(b, 2)), (len(hist.Close)-5.5, (mn+mx)/2), (len(hist.Close)-5.5, mn+(mx-mn)*0.7), arrowprops={'arrowstyle':'->'})
        #axes origin is (len(hist.Close)-10, hist.Close.iloc[-10:].min()-height*0.2)
        bperp = 0 #hist.Close.iloc[-10:].min() - (-1/m * 0)
        #y0=mx0+b, y0=-x0/m+bperp, mx0+b=-x0/m+bperp, m^2x0+m(b-bperp)=-x0, x0(m^2+1)=m(bperp-b), x0=m(bperp-b)/(m^2+1) =(bperp-b)/(m-(-1/m))=(bperb-b)/((m^2+1)/m)
        x0 = (m * (bperp - b)) / (m*m+1)
        angle = np.arctan((-x0/m+bperp) / (x0))
    #print((angle * 180 / np.pi, height, m, b, -1/m, bperp, x0, -x0/m+bperp, x0*m+b, np.abs(b)/np.sqrt(1+m*m)))
        plt.annotate('', (len(hist.Close)-10, mn), (len(hist.Close)-10 + x0, mn + -x0/m + bperp), arrowprops=dict(arrowstyle="<|-", color='red'))
        plt.gca().add_patch(mpatches.Wedge((len(hist.Close)-10 + x0, mn + -x0/m + bperp), 1, angle * 180 / np.pi - 180, angle * 180 / np.pi - 90, fill=False))
        plt.gca().add_patch(mpatches.Wedge((len(hist.Close)-10 + x0, mn + -x0/m + bperp), 0.5, angle * 180 / np.pi - 270, angle * 180 / np.pi - 180, fill=False))
        plt.annotate(r'$90\circ$', (len(hist.Close)-10 + x0 - 1, mn + -x0/m + bperp - 2))
        plt.annotate(r'$90\circ$', (len(hist.Close)-10 + x0 - 1, mn + -x0/m + bperp + 1))
        plt.gca().add_patch(mpatches.Wedge((len(hist.Close)-10, mn), 3, 0, angle * 180 / np.pi, fill=False))
        plt.annotate(r'$\theta={}^\circ$'.format(round(angle * 180/np.pi, 2)), (len(hist.Close) - 6.75, mn+0.1))
        plt.gca().add_patch(mpatches.Wedge((len(hist.Close)-10, mx), 3, 270, 270 + angle * 180 / np.pi, fill=False))
        plt.annotate(r'$\theta$', (len(hist.Close)-9.5, mx-5))
        plt.annotate((r'$\rho=\frac{{\left|{}+{}*{}-{}\right|}}{{\sqrt{{1 + {}^2}}}}$' + '\n' + '$={}\cos {}+{}\sin {}$' + '\n' + '$={}\cos {}+{}\sin {}$' + '\n' + '$={}$').format(
            round(b, 2), round(m, 2), 0, 0, round(m, 2),
            0, round(angle*180/np.pi, 2), round(hist.Close.iloc[-10]-mn, 2), round(angle*180/np.pi, 2), 9, round(angle*180/np.pi, 2), hist.Close.iloc[-1]-mn, round(angle*180/np.pi, 2), round(0 * np.cos(angle) + (hist.Close.iloc[-10]-mn) * np.sin(angle), 2)),
                     (len(hist.Close)-10+x0/2, mn + (-x0/m + bperp) / 2), (len(hist.Close)-10+x0/2, mn + (-x0/m + bperp) / 2+0.9), ha='center', color='red', arrowprops=dict(arrowstyle="->", color='red'))
        plt.plot([len(hist.Close)-10, len(hist.Close)-1], [mn, mn], 'k-')
        plt.plot([len(hist.Close)-10, len(hist.Close)-10], [mn, mx], 'k-')
        plt.annotate('{}'.format(9), (len(hist.Close)-5.5, mn), (len(hist.Close)-5.5, mn+0.5), ha='center', arrowprops=dict(arrowstyle="->"))
        plt.annotate('{}'.format(round(mx-mn, 2)), (len(hist.Close)-10, (mn+mx)/2), (len(hist.Close)-10+0.5, (mn+mx)/2), ha='left', arrowprops=dict(arrowstyle="->"))
        plt.yticks([hist.Close.iloc[-10], hist.Close.iloc[-1]])
        plt.title('Closing Price Points Demonstrating Hough transform accumulation of rho-theta for 2 point line')
        plt.xlabel('Date')
        plt.ylabel('Price')
        ax.xaxis.set_major_locator(ticker.IndexLocator(1, 0))
    #ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        ax.xaxis.set_major_formatter(ticker.FuncFormatter(datefmt(hist.index)))
        plt.setp(ax.get_xticklabels(), rotation=30, ha='right')
        plt.tight_layout()

    #extent = ann.get_window_extent(renderer=plt.gcf().canvas.get_renderer()).transformed(plt.gcf().dpi_scale_trans.inverted())
        plt.savefig(os.path.join(curdir, 'data', 'hough.svg'), format='svg')#, bbox_inches = extent, pad_inches = 0)
        plt.savefig(os.path.join(curdir, 'data', 'hough.png'), format='png')#, bbox_inches = extent, pad_inches = 0)

    #plt.show()
    def fig_minima():
        h = hist[-10:]
        mins, maxs = calc_support_resistance(h.Close)
        minimaIdxs, pmin, mintrend, minwindows = mins
        maximaIdxs, pmax, maxtrend, maxwindows = maxs
        plt.clf()
        plt.gcf().set_size_inches(1024/plt.gcf().dpi, 768/plt.gcf().dpi) #plt.gcf().dpi=100
        plt.subplot(111)
        plt.plot(minimaIdxs, [h.Close.iloc[x] for x in minimaIdxs], 'yo', label='Minima')
        plt.plot(maximaIdxs, [h.Close.iloc[x] for x in maximaIdxs], 'bo', label='Maxima')
        from findiff import FinDiff
        dx = 1 #grid scale could be amplified with pennies 0.01
        d_dx = FinDiff(0, dx, 1) #acc=3 #for 5-point stencil, currenly uses +/-1 day only
        d2_dx2 = FinDiff(0, dx, 2) #acc=3 #for 5-point stencil, currenly uses +/-1 day only
        clarr = np.asarray(h.Close)
        mom = d_dx(clarr)
        momacc = d2_dx2(clarr)
        for x in range(len(h)):
            ann = plt.gca().annotate('{}\n'.format(round(mom[x], 2), round(momacc[x], 2)), (x, h.Close.iloc[x]), (x, h.Close.iloc[x] - (h.Close.max() - h.Close.min()) / 3), ha='center') #bbox=dict(boxstyle='round', fc='gray', alpha=0.3)
        #plt.rcParams['font.size']
            ext = ann.get_window_extent(renderer = plt.gcf().canvas.get_renderer()).transformed(plt.gca().transData.inverted())
            ann = plt.gca().annotate('{}'.format(round(momacc[x], 2)), (x, ext.y0), ha='center', va='bottom', color='r')
            next = ann.get_window_extent(renderer = plt.gcf().canvas.get_renderer()).transformed(plt.gca().transData.inverted())
            patch = plt.gca().add_artist(mpatches.FancyBboxPatch((min(ext.x0, next.x0)+0.1, ext.y0), width=max(ext.width, next.width)-0.2, height=ext.height+3, boxstyle='round', fc='gray', alpha=0.3))
            plt.gca().annotate(''.format(round(mom[x], 2), round(momacc[x], 2)), (x, h.Close.iloc[x]), (x, ext.y1+3), arrowprops={'arrowstyle':'-|>'})
        plt.ylim(h.Close.min() - (h.Close.max() - h.Close.min()) / 2.8, h.Close.max() + (h.Close.max() - h.Close.min()) / 10)
        p1 = mpatches.Patch(color='black', label='Velocity')
        p2 = mpatches.Patch(color='red', label='Acceleration')
        plt.plot(range(len(h.index)), h.Close, 'g--', label='Close Price')
        plt.xlim(plt.gca().get_xlim()[0] - 0.5, plt.gca().get_xlim()[1] + 0.5)
        plt.title('Closing Price with Pivot Points, Momentum, Acceleration')
        plt.xlabel('Date')
        plt.ylabel('Price')
        plt.legend(handles=plt.gca().get_legend_handles_labels()[0] + [p1, p2])
        plt.gca().xaxis.set_major_locator(ticker.MaxNLocator(6))
    #plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        plt.gca().xaxis.set_major_formatter(ticker.FuncFormatter(datefmt(h.index)))
        plt.setp(plt.gca().get_xticklabels(), rotation=30, ha='right')
        plt.savefig(os.path.join(curdir, 'data', 'extrema.svg'), format='svg', bbox_inches = 'tight')
        plt.savefig(os.path.join(curdir, 'data', 'extrema.png'), format='png', bbox_inches = 'tight')
    #plt.show()
    def fig_reimann():
        mins, maxs = calc_support_resistance(hist[-250:].Close, sortError = True)
        minimaIdxs, pmin, mintrend, minwindows = mins
        maximaIdxs, pmax, maxtrend, maxwindows = maxs
        plt.clf()
        plt.gcf().set_size_inches(800/plt.gcf().dpi, 720/plt.gcf().dpi) #plt.gcf().dpi=100
        plt.subplot(211)
        plt.title('Closing Price with Resistance and Area')
        plt.xlabel('Date')
        plt.ylabel('Price')
        trendline = maxtrend[0]
        base = trendline[0][0]
        m, b, ser = trendline[1][0], trendline[1][1], hist[-250:][base:trendline[0][-1]+1].Close
        plt.plot(range(base, trendline[0][-1]+1), hist[-250:][base:trendline[0][-1]+1].Close, 'b-', label='Price')
        plt.plot((base, trendline[0][-1]+1), (m * base + b, m * (trendline[0][-1]+1) + b), 'r-', label='Resistance')
        plt.gca().xaxis.set_major_locator(ticker.MaxNLocator(6))
    #plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        plt.gca().xaxis.set_major_formatter(ticker.FuncFormatter(datefmt(hist[-250:].index)))
        plt.setp(plt.gca().get_xticklabels(), rotation=30, ha='right')
        plt.legend()
        plt.subplot(212)
        plt.ylabel('Price Difference from Trend')
        #plt.plot(hist.Close.iloc[-250:])
        isMin = False
        S = sum([max(0, (m * (x+base) + b) - y if isMin else y - (m * (x+base) + b)) for x, y in enumerate(ser)])
        area = S / len(ser)
        for x, y in enumerate(ser):
            plt.bar(x, (m * (x+base) + b) - y if isMin else y - (m * (x+base) + b), color='r' if (y < (m * (x+base) + b) if isMin else y > (m * (x+base) + b)) else 'gray')

        plt.annotate(r'S={}, $\frac{{{}}}{{{}}}$={}$\frac{{\$}}{{day}}$'.format(round(S, 2), round(S, 2), len(range(base, trendline[0][-1]+1)), round(area, 2)) + '\n' + r'Reimann Sum where $\Delta x=x_i-x_{i-1}$,' + '\n' + '$x_i^* \in [x_{i-1}, x_i]$: $S=\sum_{i=1}^n{f(x_i^*)\Delta x_i}$', (0, plt.gca().get_ylim()[0]+5), va='bottom')
        plt.gca().xaxis.set_major_locator(ticker.MaxNLocator(6))
    #plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        plt.gca().xaxis.set_major_formatter(ticker.FuncFormatter(datefmt(hist[-250:].index)))
        plt.setp(plt.gca().get_xticklabels(), rotation=30, ha='right')
        plt.savefig(os.path.join(curdir, 'data', 'reimann.svg'), format='svg', bbox_inches = 'tight')
        plt.savefig(os.path.join(curdir, 'data', 'reimann.png'), format='png', bbox_inches = 'tight')
    #plt.show()
    def fig_suppres():
        plot_sup_res_date(hist[-250:].Close, hist[-250:].index, fromwindows=False, sortError = True)
        plt.savefig(os.path.join(curdir, 'data', 'suppreserr.svg'), format='svg', bbox_inches = 'tight')
        plt.savefig(os.path.join(curdir, 'data', 'suppreserr.png'), format='png', bbox_inches = 'tight')
        plot_sup_res_date(hist[-250:].Close, hist[-250:].index, fromwindows=False)
        plt.savefig(os.path.join(curdir, 'data', 'suppres.svg'), format='svg', bbox_inches = 'tight')
        plt.savefig(os.path.join(curdir, 'data', 'suppres.png'), format='png', bbox_inches = 'tight')

    import matplotlib.gridspec as gridspec
    import matplotlib.patches as mpatches
    sz = plt.gcf().get_size_inches()
    fig_slopeint()
    fig_linregrs()
    fig_hough()
    fig_minima()
    fig_reimann()
    plt.gcf().set_size_inches(sz)
    fig_suppres()
def test_sup_res(curdir):
    data = [0, 1, 2, 3, 2, 1, 0, 1, 2, 3, 2, 1, 0, 1, 2, 3, 2, 1, 0, 1, 2, 3, 2, 1, 0]
    data = [float(x) for x in data]
    result = (([6, 12, 18], [0.0, 0.0], [([6, 12, 18], (0.0, 0.0, 0.0, 0.0, 0.0, 0.0))], [[([6, 12, 18], (0.0, 0.0, 0.0, 0.0, 0.0, 0.0))]]), ([3, 9, 15, 21], [0.0, 3.0], [([3, 9, 15, 21], (0.0, 3.0, 0.0, 0.0, 0.0, 0.0))], [[([3, 9, 15, 21], (0.0, 3.0, 0.0, 0.0, 0.0, 0.0))]]))
    assert result == calc_support_resistance(data, extmethod=METHOD_NAIVE)
    assert result == calc_support_resistance(data, extmethod=METHOD_NAIVECONSEC)
    assert result == calc_support_resistance(data)
    assert result == calc_support_resistance(np.array(data))
    import pandas as pd
    assert result == calc_support_resistance(pd.Series(data))
    assert result == calc_support_resistance(data, method=METHOD_NCUBED)
    assert result == calc_support_resistance(data, method=METHOD_HOUGHPOINTS)
    assert result == calc_support_resistance(data, method=METHOD_HOUGHLINES)
    assert result == calc_support_resistance(data, method=METHOD_PROBHOUGH)
    data = [0, 1, 2, 3, 2, 1, 1, 1, 2, 4, 3, 2, 2, 2, 3, 5, 4, 3, 3, 3, 4, 6, 5, 4, 4]
    data = [float(x) for x in data]
    result = (([], [np.nan, np.nan], [], [[]]), ([3, 9, 15, 21], [0.16666666666666677, 2.499999999999998], [([3, 9, 15, 21], (0.16666666666666666, 2.5, 0.0, 0.0, 0.0, 0.0))], [[([3, 9, 15, 21], (0.16666666666666666, 2.5, 0.0, 0.0, 0.0, 0.0))]]))
    assert result == calc_support_resistance(data, extmethod=METHOD_NAIVE)
    result = (([7, 13, 19], [0.1666666666666666, -0.1666666666666652], [([7, 13, 19], (0.16666666666666666, -0.16666666666666652, 0.0, 0.0, 0.0, 0.0))], [[([7, 13, 19], (0.16666666666666666, -0.16666666666666652, 0.0, 0.0, 0.0, 0.0))]]), ([3, 9, 15, 21], [0.16666666666666677, 2.499999999999998], [([3, 9, 15, 21], (0.16666666666666666, 2.5, 0.0, 0.0, 0.0, 0.0))], [[([3, 9, 15, 21], (0.16666666666666666, 2.5, 0.0, 0.0, 0.0, 0.0))]]))
    assert result == calc_support_resistance(data, extmethod=METHOD_NAIVECONSEC)
    result = (([23], [np.nan, np.nan], [], [[]]), ([3, 9, 15, 21], [0.16666666666666677, 2.499999999999998], [([3, 9, 15, 21], (0.16666666666666666, 2.5, 0.0, 0.0, 0.0, 0.0))], [[([3, 9, 15, 21], (0.16666666666666666, 2.5, 0.0, 0.0, 0.0, 0.0))]]))
    assert result == calc_support_resistance(data)
    assert result == calc_support_resistance(data, method=METHOD_NCUBED)
    assert result == calc_support_resistance(data, method=METHOD_HOUGHPOINTS)
    assert result == calc_support_resistance(data, method=METHOD_HOUGHLINES)
    assert result == calc_support_resistance(data, method=METHOD_PROBHOUGH)
    import yfinance as yf #pip install yfinance
    tick = yf.Ticker('^GSPC')
    hist = tick.history(period="max", rounding=True)
    plot_sup_res_learn(curdir, hist)
    import matplotlib.pyplot as plt
    plot_sup_res_date(hist[-250:].Close, hist[-250:].index)
    plt.show()
    plot_sup_res_date((hist[-250:].Close, None), hist[-250:].index)
    plt.show()
    plot_sup_res_date((None, hist[-250:].Close), hist[-250:].index)
    plt.show()
    plot_sup_res_date((hist[-250:].Low, hist[-250:].High), hist[-250:].index)
    plt.show()
    plt.clf()
    return None
METHOD_NAIVE, METHOD_NAIVECONSEC, METHOD_NUMDIFF = 0, 1, 2
METHOD_NCUBED, METHOD_NSQUREDLOGN, METHOD_HOUGHPOINTS, METHOD_HOUGHLINES, METHOD_PROBHOUGH = 0, 1, 2, 3, 4
def check_num_alike(h):
    if type(h) is list and all([isinstance(x, (bool, int, float)) for x in h]): return True
    elif type(h) is np.ndarray and h.ndim==1 and h.dtype.kind in 'biuf': return True
    else:
        import pandas as pd
        if type(h) is pd.Series and h.dtype.kind in 'biuf': return True
        else: return False
def get_extrema(h, extmethod=METHOD_NUMDIFF, accuracy=1):
    #h must be single dimensional array-like object e.g. List, np.ndarray, pd.Series
    if type(h) is tuple and len(h) == 2 and (h[0] is None or check_num_alike(h[0])) and (h[1] is None or check_num_alike(h[1])) and (not h[0] is None or not h[1] is None):
        hmin, hmax = h[0], h[1]
        if not h[0] is None and not h[1] is None and len(hmin) != len(hmax): #not strict requirement, but contextually ideal
            raise ValueError('h does not have a equal length minima and maxima data')
    elif check_num_alike(h): hmin, hmax = None, None
    else: raise ValueError('h is not list, numpy ndarray or pandas Series of numeric values or a 2-tuple thereof')
    if extmethod == METHOD_NAIVE:
        #naive method
        import pandas as pd
        def get_minmax(h):
            rollwin = pd.Series(h).rolling(window=3, min_periods=1, center=True)
            minFunc = lambda x: len(x) == 3 and x.iloc[0] > x.iloc[1] and x.iloc[2] > x.iloc[1]
            maxFunc = lambda x: len(x) == 3 and x.iloc[0] < x.iloc[1] and x.iloc[2] < x.iloc[1]
            numdiff_extrema = lambda func: np.flatnonzero(rollwin.aggregate(func)).tolist()
            return minFunc, maxFunc, numdiff_extrema            
    elif extmethod == METHOD_NAIVECONSEC:
        #naive method collapsing duplicate consecutive values
        import pandas as pd
        def get_minmax(h):
            hist = pd.Series(h)
            rollwin = hist.loc[hist.shift(-1) != hist].rolling(window=3, center=True)
            minFunc = lambda x: x.iloc[0] > x.iloc[1] and x.iloc[2] > x.iloc[1]
            maxFunc = lambda x: x.iloc[0] < x.iloc[1] and x.iloc[2] < x.iloc[1]
            def numdiff_extrema(func):
                x = rollwin.aggregate(func)
                return x[x == 1].index.tolist()
            return minFunc, maxFunc, numdiff_extrema
    elif extmethod == METHOD_NUMDIFF:
        #pip install findiff
        from findiff import FinDiff
        dx = 1 #1 day interval
        d_dx = FinDiff(0, dx, 1, acc=accuracy) #acc=3 #for 5-point stencil, currenly uses +/-1 day only
        d2_dx2 = FinDiff(0, dx, 2, acc=accuracy) #acc=3 #for 5-point stencil, currenly uses +/-1 day only
        def get_minmax(h):
            clarr = np.asarray(h, dtype=np.float64)
            mom, momacc = d_dx(clarr), d2_dx2(clarr)
            #print(mom[-10:], momacc[-10:])
            #numerical derivative will yield prominent extrema points only
            def numdiff_extrema(func):
                return [x for x in range(len(mom))
                        if func(x) and
                            (mom[x] == 0 or #either slope is 0, or it crosses from positive to negative with the closer to 0 of the two chosen or prior if a tie
                             (x != len(mom) - 1 and (mom[x] > 0 and mom[x+1] < 0 and h[x] >= h[x+1] or #mom[x] >= -mom[x+1]
                                                     mom[x] < 0 and mom[x+1] > 0 and h[x] <= h[x+1]) or #-mom[x] >= mom[x+1]) or
                              x != 0 and (mom[x-1] > 0 and mom[x] < 0 and h[x-1] < h[x] or #mom[x-1] < -mom[x] or
                                          mom[x-1] < 0 and mom[x] > 0 and h[x-1] > h[x])))] #-mom[x-1] < mom[x])))]
            return lambda x: momacc[x] > 0, lambda x: momacc[x] < 0, numdiff_extrema
    else: raise ValueError('extmethod must be METHOD_NAIVE, METHOD_NAIVECONSEC, METHOD_NUMDIFF')
    if hmin is None and hmax is None:
        minFunc, maxFunc, numdiff_extrema = get_minmax(h)
        return numdiff_extrema(minFunc), numdiff_extrema(maxFunc)
    if not hmin is None:
        minf = get_minmax(hmin)
        if hmax is None: return minf[2](minf[0])
    if not hmax is None:
        maxf = get_minmax(hmax)
        if hmin is None: return maxf[2](maxf[1])
    return minf[2](minf[0]), maxf[2](maxf[1])
    
#returns (list of minima indexes, list of maxima indexes, [support slope coefficient, intersect], [resistance slope coefficient, intersect], [[support point indexes], (slope, intercept, residual, slope error, intercept error, area on wrong side of trend line per time unit)]
def calc_support_resistance(h, extmethod = METHOD_NUMDIFF, method=METHOD_NSQUREDLOGN,
                            window=125, errpct=0.005, hough_scale=0.01, hough_prob_iter=10,
                            sortError=False, accuracy=1):
    if not type(window) is int:
        raise ValueError('window must be of type int')
    if not type(errpct) is float:
        raise ValueError('errpct must be of type float')
    if not type(hough_scale) is float:
        raise ValueError('house_scale must be of type float')
    if not type(hough_prob_iter) is int:
        raise ValueError('house_prob_iter must be of type int')
    if not type(sortError) is bool:
        raise ValueError('sortError must be True of False')
    #h = hist.Close.tolist()
    if type(h) is tuple and len(h) == 2 and (h[0] is None or check_num_alike(h[0])) and (h[1] is None or check_num_alike(h[1])) and (not h[0] is None or not h[1] is None):
        if not h[0] is None and not h[1] is None and len(h[0]) != len(h[1]): #not strict requirement, but contextually ideal
            raise ValueError('h does not have a equal length minima and maxima data')
        hmin, hmax, len_h = h[0], h[1], len(h[1 if h[0] is None else 0])
    elif check_num_alike(h): hmin, hmax, len_h = None, None, len(h)
    else: raise ValueError('h is not list, numpy ndarray or pandas Series of numeric values or a 2-tuple thereof')
    #https://stackoverflow.com/questions/8587047/support-resistance-algorithm-technical-analysis/8590007#8590007
    #print((minimaIdxs[-10:], maximaIdxs[-10:]))
    #https://en.wikipedia.org/wiki/Trend_line_(technical_analysis)
    #It is formed when a diagonal line can be drawn between a minimum of three or more price pivot points. A line can be drawn between any two points, but it does not qualify as a trend line until tested. Hence the need for the third point, the test.
    #Given N points on the plane, what is an efficient algorithm to find all the sets of 3 or more collinear points?
    #also principle of optimality - for each point, calculate angle formed by every other group of 2 points, check for 180 degree angled points also O(n^3)
    #sort the points in some order, and find slope for selected origin point to all other points, sort and check if identical slopes, move on O(n^2*log(n))
    #Hough transform solves with linear complexity
    #https://en.wikipedia.org/wiki/Regression_analysis#Linear_regression
    #line of best fit using least squared method:
    #Xbar=sum of all x over number of x, Ybar=sum of all y over number of y
    #m=sum((x-Xbar) * (y-Ybar) for all (x, y)) / sum((x-Xbar)^2 for all x), b=Ybar-m*Xbar
    #standard error of regression of slope: sqrt(sum((y-yexpected)^2 for all y) / (n-2)) / sqrt(sum((x-Xbar)^2 for all x))
    #standard error of regression of intercept: (standard error of regression of slope) * sqrt(sum(x^2 for all x)/n)
    def get_bestfit3(x0, y0, x1, y1, x2, y2):
        xbar, ybar = (x0 + x1 + x2) / 3, (y0 + y1 + y2) / 3
        xb0, yb0, xb1, yb1, xb2, yb2 = x0-xbar, y0-ybar, x1-xbar, y1-ybar, x2-xbar, y2-ybar
        xs = xb0*xb0+xb1*xb1+xb2*xb2
        m = (xb0*yb0+xb1*yb1+xb2*yb2) / xs
        b = ybar - m * xbar
        ys0, ys1, ys2 = (y0 - (m * x0 + b)),(y1 - (m * x1 + b)),(y2 - (m * x2 + b))
        ys = ys0*ys0+ys1*ys1+ys2*ys2
        ser = np.sqrt(ys / xs)
        return m, b, ys, ser, ser * np.sqrt((x0*x0+x1*x1+x2*x2)/3)
    def get_bestfit(pts):
        xbar, ybar = [sum(x) / len(x) for x in zip(*pts)]
        def subcalc(x, y):
            tx, ty = x - xbar, y - ybar
            return tx * ty, tx * tx, x * x
        (xy, xs, xx) = [sum(q) for q in zip(*[subcalc(x, y) for x, y in pts])]
        m = xy / xs
        b = ybar - m * xbar
        ys = sum([np.square(y - (m * x + b)) for x, y in pts])
        ser = np.sqrt(ys / ((len(pts) - 2) * xs))
        return m, b, ys, ser, ser * np.sqrt(xx / len(pts))
    def get_trend(Idxs, h, fltpct, min_h, max_h):
        trend = []
        for x in range(len(Idxs)): #unfortunately an O(n(n-1)(n-2))=O((n^2-n)(n-2))=O(n^3-3n^2-2n)~=O(n^3) algorithm but meets the strict definition of a trendline
            for y in range(x+1, len(Idxs)):
                #slope = (h[Idxs[x]] - h[Idxs[y]]) / (Idxs[x] - Idxs[y]) #m=dy/dx #if slope 0 then intercept does not exist constant y where y=b
                #intercept = h[Idxs[x]] - slope * Idxs[x] #y=mx+b, b=y-mx
                for z in range(y+1, len(Idxs)):
                    #distance = abs(slope * Idxs[z] + intercept - h[Idxs[z]]) #distance to y value based on x with slope-intercept
                    trend.append(([Idxs[x], Idxs[y], Idxs[z]], get_bestfit3(Idxs[x], h[Idxs[x]], Idxs[y], h[Idxs[y]], Idxs[z], h[Idxs[z]])))
        return list(filter(lambda val: val[1][3] <= fltpct, trend))
    def get_trend_opt(Idxs, h, fltpct, min_h, max_h):
        slopes, trend = [], []
        for x in range(len(Idxs)): #O(n^2*log n) algorithm
            slopes.append([])
            for y in range(x+1, len(Idxs)):
                slope = (h[Idxs[x]] - h[Idxs[y]]) / (Idxs[x] - Idxs[y]) #m=dy/dx #if slope 0 then intercept does not exist constant y where y=b
                #intercept = h[Idxs[x]] - slope * Idxs[x] #y=mx+b, b=y-mx
                slopes[x].append((slope, y))
        for x in range(len(Idxs)):
            slopes[x].sort() #key=lambda val: val[0])
            CurIdxs = [Idxs[x]]
            for y in range(0, len(slopes[x])):
                #distance = abs(slopes[x][y][2] * slopes[x][y+1][1] + slopes[x][y][3] - h[slopes[x][y+1][1]])
                CurIdxs.append(Idxs[slopes[x][y][1]])
                if len(CurIdxs) < 3: continue
                res = get_bestfit([(p, h[p]) for p in CurIdxs])
                if res[3] <= fltpct:
                    CurIdxs.sort()
                    if len(CurIdxs) == 3:
                        trend.append((CurIdxs, res))
                        CurIdxs = list(CurIdxs)
                    else: CurIdxs, trend[-1] = list(CurIdxs), (CurIdxs, res)
                    #if len(CurIdxs) >= MaxPts: CurIdxs = [CurIdxs[0], CurIdxs[-1]]
                else: CurIdxs = [CurIdxs[0], CurIdxs[-1]] #restart search from this point
        return trend
    def make_image(Idxs, h, min_h, max_h):
        #np.arctan(2/len_h), np.arctan(2/int((hist.Close.max() - m + 1) * (1/hough_scale))) #minimal angles to find all points
        max_size = int(np.ceil(2/np.tan(np.pi / (360 * 5)))) #~1146
        m, tested_angles = min_h, np.linspace(-np.pi / 2, np.pi / 2, 360*5) #degree of precision from 90 to 270 degrees with 360*5 increments
        height = int((max_h - m + 0.01) * (1/hough_scale))
        mx = min(max_size, height)
        scl = (1/hough_scale) * mx / height
        image = np.zeros((mx, len_h)) #in rows, columns or y, x image format
        for x in Idxs:
            image[int((h[x] - m) * scl), x] = 255
        return image, tested_angles, scl, m
    def find_line_pts(Idxs, x0, y0, x1, y1, h, fltpct):
        s = (y0 - y1) / (x0 - x1)
        i, dnm = y0 - s * x0, np.sqrt(1 + s*s)
        dist = [(np.abs(i+s*x-h[x])/dnm, x) for x in Idxs]
        dist.sort() #(key=lambda val: val[0])
        pts, res = [], None
        for x in range(len(dist)):
            pts.append((dist[x][1], h[dist[x][1]]))
            if len(pts) < 3: continue
            r = get_bestfit(pts)
            if r[3] > fltpct:
                pts = pts[:-1]
                break
            res = r
        pts = [x for x, _ in pts]
        pts.sort()
        return pts, res
    def hough_points(pts, width, height, thetas):
        diag_len = int(np.ceil(np.sqrt(width * width + height * height)))
        rhos = np.linspace(-diag_len, diag_len, diag_len * 2.0)
        # Cache some resuable values
        cos_t = np.cos(thetas)
        sin_t = np.sin(thetas)
        num_thetas = len(thetas)
        # Hough accumulator array of theta vs rho
        accumulator = np.zeros((2 * diag_len, num_thetas), dtype=np.uint64)
        # Vote in the hough accumulator
        for i in range(len(pts)):
            x, y = pts[i]
            for t_idx in range(num_thetas):
                # Calculate rho. diag_len is added for a positive index
                rho = int(round(x * cos_t[t_idx] + y * sin_t[t_idx])) + diag_len
                accumulator[rho, t_idx] += 1
        return accumulator, thetas, rhos
    def houghpt(Idxs, h, fltpct, min_h, max_h):
        max_size = int(np.ceil(2/np.tan(np.pi / (360 * 5)))) #~1146
        m, tested_angles = min_h, np.linspace(-np.pi / 2, np.pi / 2, 360*5) #degree of precision from 90 to 270 degrees with 360*5 increments
        height = int((max_h - m + 1) * (1/hough_scale))
        mx = min(max_size, height)
        scl = (1/hough_scale) * mx / height
        acc, theta, d = hough_points([(x, int((h[x] - m) * scl)) for x in Idxs], mx, len_h, np.linspace(-np.pi / 2, np.pi / 2, 360*5))
        origin, lines = np.array((0, len_h)), []
        for x, y in np.argwhere(acc >= 3):
            dist, angle = d[x], theta[y]
            y0, y1 = (dist - origin * np.cos(angle)) / np.sin(angle)
            y0, y1 = y0 / scl + m, y1 / scl + m
            pts, res = find_line_pts(Idxs, 0, y0, len_h, y1, h, fltpct)
            if len(pts) >= 3: lines.append((pts, res))
        return lines
    def hough(Idxs, h, fltpct, min_h, max_h):
        image, tested_angles, scl, m = make_image(Idxs, h, min_h, max_h)
        from skimage.transform import hough_line, hough_line_peaks
        hl, theta, d = hough_line(image, theta=tested_angles)
        origin, lines = np.array((0, image.shape[1])), []
        for pts, angle, dist in zip(*hough_line_peaks(hl, theta, d, threshold=2)): #> threshold
            y0, y1 = (dist - origin * np.cos(angle)) / np.sin(angle)
            y0, y1 = y0 / scl + m, y1 / scl + m
            pts, res = find_line_pts(Idxs, 0, y0, image.shape[1], y1, h, fltpct)
            if len(pts) >= 3: lines.append((pts, res))
        return lines
    def prob_hough(Idxs, h, fltpct, min_h, max_h):
        image, tested_angles, scl, m = make_image(Idxs, h, min_h, max_h)
        from skimage.transform import probabilistic_hough_line
        lines = []
        for x in range(hough_prob_iter):
            lines.extend(probabilistic_hough_line(image, threshold=2, theta=tested_angles, line_length=0,
                                            line_gap=int(np.ceil(np.sqrt(np.square(image.shape[0]) + np.square(image.shape[1]))))))
        l = []
        for (x0, y0), (x1, y1) in lines:
            if x0 == x1: continue
            if x1 < x0: (x0, y0), (x1, y1) = (x1, y1), (x0, y0)
            y0, y1 = y0 / scl + m, y1 / scl + m
            pts, res = find_line_pts(Idxs, x0, y0, x1, y1, h, fltpct)
            if len(pts) >= 3: l.append((pts, res))
        return l
    def merge_lines(Idxs, trend, h, fltpct):
        for x in Idxs:
            l = []
            for i, (p, r) in enumerate(trend):
                if x in p: l.append((r[0], i))
            l.sort() #key=lambda val: val[0])
            if len(l) > 1: CurIdxs = list(trend[l[0][1]][0])
            for (s, i) in l[1:]:
                CurIdxs += trend[i][0]
                CurIdxs = list(dict.fromkeys(CurIdxs))
                CurIdxs.sort()
                res = get_bestfit([(p, h[p]) for p in CurIdxs])
                if res[3] <= fltpct: trend[i-1], trend[i], CurIdxs = ([], None), (CurIdxs, res), list(CurIdxs)
                else: CurIdxs = list(trend[i][0]) #restart search from here
        return list(filter(lambda val: val[0] != [], trend))
    def measure_area(trendline, isMin, h): # Reimann sum of line to discrete time series data
        #first determine the time range, and subtract the line values to obtain a single function
        #support subtracts the line minus the series and eliminates the negative values
        #resistances subtracts the series minus the line and eliminate the negatives
        base = trendline[0][0]
        m, b, ser = trendline[1][0], trendline[1][1], h[base:trendline[0][-1]+1]
        return sum([max(0, (m * (x+base) + b) - y if isMin else y - (m * (x+base) + b)) for x, y in enumerate(ser)]) / len(ser)
    def window_results(trends, isMin, h):
        windows = [[] for x in range(len(divide)-1)]
        for x in trends:
            fstwin, lastwin = int(x[0][0] / window), int(x[0][-1] / window)
            wins = [[] for _ in range(fstwin, lastwin+1)]
            for y in x[0]: wins[int(y / window) - fstwin].append(y)
            for y in range(0, lastwin-fstwin):
                if len(wins[y+1]) == 0 and len(wins[y]) >= 3: windows[fstwin+y].append(wins[y])
                if len(wins[y]) + len(wins[y + 1]) >= 3:
                    windows[fstwin+y+1].append(wins[y] + wins[y+1])
            if lastwin-fstwin==0 and len(wins[0]) >= 3: windows[fstwin].append(wins[0])
        def fitarea(x):
            fit = get_bestfit([(y, h[y]) for y in x])
            return (x, fit + (measure_area((x, fit), isMin, h),))
        def dosort(x):
            x.sort(key = lambda val: val[1][skey])
            return x
        return [dosort(list(fitarea(pts) for pts in x)) for x in windows]
    #print((mintrend[:5], maxtrend[:5]))
    
    #find all places where derivative is 0 - in finite case when it crosses positive to negative and choose the closer to 0 value
    #second derivative being positive or negative decides if they are minima or maxima
    #now for all pairs of 3 points construct the average line, rate it based on # of additional points, # of points on the wrong side of the line, and the margin of error for the line passing through all of them
    #finally select the best based on this rating

    #first find the peaks and troughs
    #https://github.com/dysonance/Trendy/blob/master/trendy.py #not proper trendlines only takes extremal points, and next best extrema, not 3 points
    #https://github.com/harttraveller/roughsr2/blob/master/roughsr2.py
    #https://www.candlestick.ninja/2019/02/support-and-resistance.html
    #https://www.candlestick.ninja/2019/02/identifying-support-and-resistance-part2.html
    #zmin, zmne, _, _, _ = np.polyfit(minimaIdxs, ymin, 1, full=True)  #y=zmin[0]*x+zmin[1]
    #pmin = np.poly1d(zmin).c
    #zmax, zmxe, _, _, _ = np.polyfit(maximaIdxs, ymax, 1, full=True) #y=zmax[0]*x+zmax[1]
    #pmax = np.poly1d(zmax).c
    def overall_line(idxs, vals):
        if len(idxs) <= 1: pm, zme = [np.nan, np.nan], [np.nan]
        else:
            p, r = np.polynomial.polynomial.Polynomial.fit(idxs, vals, 1, full=True) #more numerically stable
            pm, zme = list(reversed(p.convert().coef)), r[0]
            if len(pm) == 1: pm.insert(0, 0.0)
        return pm  
    def calc_all(idxs, h, isMin):
        min_h, max_h = min(h), max(h)
        scale = (max_h - min_h) / len_h
        fltpct = scale * errpct
        midxs = [[] for _ in range(len(divide)-1)]
        for x in idxs: midxs[int((x + rem) / window)].append(x)
        mtrend = []
        for x in range(len(divide)-1-1):
            m = midxs[x] + midxs[x+1]
            mtrend.extend(trendmethod(m, h, fltpct, min_h, max_h))
        if len(divide) == 2:
            mtrend.extend(trendmethod(midxs[0], h, fltpct, min_h, max_h))
        mtrend = merge_lines(idxs, mtrend, h, fltpct)
        mtrend = [(pts, (res[0], res[1], res[2], res[3], res[4], measure_area((pts, res), isMin, h))) for pts, res in mtrend]
        mtrend.sort(key=lambda val: val[1][skey])
        mwindows = window_results(mtrend, isMin, h)
        pm = overall_line(idxs, [h[x] for x in idxs])
        #print((pmin, pmax, zmne, zmxe))
        return pm, mtrend, mwindows
    if method == METHOD_NCUBED:
        trendmethod = get_trend
    elif method == METHOD_NSQUREDLOGN:
        trendmethod = get_trend_opt
    elif method == METHOD_HOUGHPOINTS:
        trendmethod = houghpt
    #pip install scikit-image
    elif method == METHOD_HOUGHLINES:
        trendmethod = hough
    elif method == METHOD_PROBHOUGH:
        trendmethod = prob_hough
    else: raise ValueError('method must be one of METHOD_NCUBED, METHOD_NSQUREDLOGN, METHOD_HOUGHPOINTS, METHOD_HOUGHLINES, METHOD_PROBHOUGH')
    extremaIdxs = get_extrema(h, extmethod, accuracy)
    divide = list(reversed(range(len_h, -window, -window)))
    rem, divide[0] = window - len_h % window, 0
    if rem == window: rem = 0
    skey = 3 if sortError else 5
    if hmin is None and hmax is None:
        pmin, mintrend, minwindows = calc_all(extremaIdxs[0], h, True)
        pmax, maxtrend, maxwindows = calc_all(extremaIdxs[1], h, False)
    else:
        if not hmin is None:
            pmin, mintrend, minwindows = calc_all(extremaIdxs if hmax is None else extremaIdxs[0], hmin, True)
            if hmax is None: return (extremaIdxs, pmin, mintrend, minwindows)
        if not hmax is None:            
            pmax, maxtrend, maxwindows = calc_all(extremaIdxs if hmin is None else extremaIdxs[1], hmax, False)
            if hmin is None: return (extremaIdxs, pmax, maxtrend, maxwindows)
    return (extremaIdxs[0], pmin, mintrend, minwindows), (extremaIdxs[1], pmax, maxtrend, maxwindows)

def plot_sup_res_date(hist, idx, numbest = 2, fromwindows = True, pctbound=0.1,
                      extmethod = METHOD_NUMDIFF, method=METHOD_NSQUREDLOGN, window=125,
                      errpct = 0.005, hough_scale=0.01, hough_prob_iter=10, sortError=False, accuracy=1,
                      title='Prices with Support/Resistance Trend Lines', y_axis_label='Price', y_label='Close Price'):
    import matplotlib.ticker as ticker
    return plot_support_resistance(hist, ticker.FuncFormatter(datefmt(idx)), numbest, fromwindows,
                                   pctbound, extmethod, method, window, errpct, hough_scale, hough_prob_iter, sortError, accuracy, title, y_axis_label, y_label)

def plot_support_resistance(hist, xformatter = None, numbest = 2, fromwindows = True,
                            pctbound=0.1, extmethod = METHOD_NUMDIFF, method=METHOD_NSQUREDLOGN,
                            window=125, errpct = 0.005, hough_scale=0.01, hough_prob_iter=10, sortError=False, accuracy=1,
                            title='Prices with Support/Resistance Trend Lines', y_axis_label='Price', y_label='Close Price'):
    import matplotlib.pyplot as plt
    import matplotlib.ticker as ticker
    ret = calc_support_resistance(hist, extmethod, method, window, errpct, hough_scale, hough_prob_iter, sortError, accuracy)
    plt.clf()
    plt.subplot(111)
    if len(ret) == 2:
        minimaIdxs, pmin, mintrend, minwindows = ret[0]
        maximaIdxs, pmax, maxtrend, maxwindows = ret[1]
        if type(hist) is tuple and len(hist) == 2 and check_num_alike(hist[0]) and check_num_alike(hist[1]):
            len_h = len(hist[0])
            min_h, max_h = min(min(hist[0]), min(hist[1])), max(max(hist[0]), max(hist[1]))
            disp = [(hist[0], minimaIdxs, pmin, 'yo', 'Avg. Support', 'y--'), (hist[1], maximaIdxs, pmax, 'bo', 'Avg. Resistance', 'b--')]
            dispwin = [(hist[0], minwindows, 'Support', 'g--'), (hist[1], maxwindows, 'Resistance', 'r--')]
            disptrend = [(hist[0], mintrend, 'Support', 'g--'), (hist[1], maxtrend, 'Resistance', 'r--')]
            plt.plot(range(len_h), hist[0], 'k--', label=f'Low {y_label}')
            plt.plot(range(len_h), hist[1], 'm--', label=f'High {y_label}')
        else:
            len_h = len(hist)
            min_h, max_h = min(hist), max(hist)
            disp = [(hist, minimaIdxs, pmin, 'yo', 'Avg. Support', 'y--'), (hist, maximaIdxs, pmax, 'bo', 'Avg. Resistance', 'b--')]
            dispwin = [(hist, minwindows, 'Support', 'g--'), (hist, maxwindows, 'Resistance', 'r--')]
            disptrend = [(hist, mintrend, 'Support', 'g--'), (hist, maxtrend, 'Resistance', 'r--')]
            plt.plot(range(len_h), hist, 'k--', label=y_label)
    else:
        minimaIdxs, pmin, mintrend, minwindows = ([], [], [], []) if hist[0] is None else ret
        maximaIdxs, pmax, maxtrend, maxwindows = ([], [], [], []) if hist[1] is None else ret
        len_h = len(hist[1 if hist[0] is None else 0])
        min_h, max_h = min(hist[1 if hist[0] is None else 0]), max(hist[1 if hist[0] is None else 0])
        disp = [(hist[1], maximaIdxs, pmax, 'bo', 'Avg. Resistance', 'b--') if hist[0] is None else (hist[0], minimaIdxs, pmin, 'yo', 'Avg. Support', 'y--')]
        dispwin = [(hist[1], maxwindows, 'Resistance', 'r--') if hist[0] is None else (hist[0], minwindows, 'Support', 'g--')]
        disptrend = [(hist[1], maxtrend, 'Resistance', 'r--') if hist[0] is None else (hist[0], mintrend, 'Support', 'g--')]
        plt.plot(range(len_h), hist[1 if hist[0] is None else 0], 'k--', label= ('High' if hist[0] is None else 'Low') + ' Price')
    for h, idxs, pm, clrp, lbl, clrl in disp:
        plt.plot(idxs, [h[x] for x in idxs], clrp)
        plt.plot([0, len_h-1],[pm[1],pm[0] * (len_h-1) + pm[1]],clrl, label=lbl)
    def add_trend(h, trend, lbl, clr, bFirst):
        for ln in trend[:numbest]:
            maxx = ln[0][-1]+1
            while maxx < len_h:
                ypred = ln[1][0] * maxx + ln[1][1]
                if (h[maxx] > ypred and h[maxx-1] < ypred or h[maxx] < ypred and h[maxx-1] > ypred or
                    ypred > max_h + (max_h-min_h)*pctbound or ypred < min_h - (max_h-min_h)*pctbound): break
                maxx += 1
            x_vals = np.array((ln[0][0], maxx)) # plt.gca().get_xlim())
            y_vals = ln[1][0] * x_vals + ln[1][1]
            if bFirst:
                plt.plot([ln[0][0], maxx], y_vals, clr, label=lbl)
                bFirst = False
            else: plt.plot([ln[0][0], maxx], y_vals, clr)
        return bFirst
    if fromwindows:
        for h, windows, lbl, clr in dispwin:
            bFirst = True
            for trend in windows:
                bFirst = add_trend(h, trend, lbl, clr, bFirst)
    else:
        for h, trend, lbl, clr in disptrend:
            add_trend(h, trend, lbl, clr, True)
    plt.title(title)
    plt.xlabel('Date')
    plt.ylabel(y_axis_label)
    plt.legend()
    plt.gca().xaxis.set_major_locator(ticker.MaxNLocator(6))
    #plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    if not xformatter is None: plt.gca().xaxis.set_major_formatter(xformatter)
    plt.setp(plt.gca().get_xticklabels(), rotation=30, ha='right')
    #plt.gca().set_position([0, 0, 1, 1])
    #plt.savefig(os.path.join(curdir, 'data', 'suppres.svg'), format='svg', bbox_inches = 'tight')
    #plt.show()
    return plt.gcf()
