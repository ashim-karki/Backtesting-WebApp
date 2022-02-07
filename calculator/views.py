from django.shortcuts import render

# Create your views here.

from django.shortcuts import render

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_agg import FigureCanvasAgg
from django.http import HttpResponse

import pandas as pd
from ta import add_all_ta_features
from ta.utils import dropna
# from ta.volatility import BollingerBands
from PIL import Image

from flask import send_file 
from flask import request
import io
import base64
from datetime import datetime

# Create your views here.

def index(request):
    return render(request, "input.html")
    
def drop_down(request):
    strategy = request.POST.get("strategy")
    company = request.POST.get("company")
    path = company + ".csv"
    
    num1=request.POST['num1']
    num2=request.POST['num2']
    a=float(num1)*100
    b=float(num2)*100
    iaf=int(a)/100
    maxaf=int(b)/100
    if strategy == "PARABOLIC SAR":

#PSAR CALCULATION
        def psar(barsdata):
            num1=request.POST['num1']
            num2=request.POST['num2']
            a=float(num1)*100
            b=float(num2)*100
            iaf=int(a)/100
            maxaf=int(b)/100
            length = len(barsdata)
            dates = list(barsdata['Date'])
            high = list(barsdata['High'])
            low = list(barsdata['Low'])
            close = list(barsdata['Close'])
            psar = close[0:len(close)]
            psarbull = [None] * length
            psarbear = [None] * length
            bull = True
            af = iaf
            ep = low[0]
            hp = high[0]
            lp = low[0]
            
            for i in range(2,length):
                if bull:
                    psar[i] = psar[i - 1] + af * (hp - psar[i - 1])
                else:
                    psar[i] = psar[i - 1] + af * (lp - psar[i - 1])
                
                reverse = False
                
                if bull:
                    if low[i] < psar[i]:
                        bull = False
                        reverse = True
                        psar[i] = hp
                        lp = low[i]
                        af = iaf
                else:
                    if high[i] > psar[i]:
                        bull = True
                        reverse = True
                        psar[i] = lp
                        hp = high[i]
                        af = iaf
            
                if not reverse:
                    if bull:
                        if high[i] > hp:
                            hp = high[i]
                            af = min(af + iaf, maxaf)
                        if low[i - 1] < psar[i]:
                            psar[i] = low[i - 1]
                        if low[i - 2] < psar[i]:
                            psar[i] = low[i - 2]
                    else:
                        if low[i] < lp:
                            lp = low[i]
                            af = min(af + iaf, maxaf)
                        if high[i - 1] > psar[i]:
                            psar[i] = high[i - 1]
                        if high[i - 2] > psar[i]:
                            psar[i] = high[i - 2]
                            
                if bull:
                    psarbull[i] = psar[i]
                else:
                    psarbear[i] = psar[i]

            return {"dates":dates, "high":high, "low":low, "close":close, "psar":psar, "psarbear":psarbear, "psarbull":psarbull}

        #if __name__ == "__main__":
        barsdata = pd.read_csv(path)
        #Reindex the data: ascending dates are expected in the function
        barsdata = barsdata.reindex(index=barsdata.index[::-1])
        #Convert strings to actual timestamps
        barsdata['Date'] = [datetime.strptime(x, '%Y-%m-%d') for x in barsdata['Date']]
        startidx = 0
        endidx = len(barsdata)
            
        result = psar(barsdata)
        dates = result['dates'][startidx:endidx]
        close = result['close'][startidx:endidx]
        psarbear = result['psarbear'][startidx:endidx]
        psarbull = result['psarbull'][startidx:endidx]
        barsdata['psarbull']=psarbull
        barsdata['psarbear']=psarbear
        df=barsdata.fillna(0)
        BP=[]
        SP=[]
        for i in range(len(df)):
            if(i<len(df)-2):
                if(df['psarbull'].iloc[i])==0 and df['psarbull'].iloc[i+1]!=0:
                    BP.append(i+1)
                if(df['psarbear'].iloc[i])==0 and df['psarbear'].iloc[i+1]!=0:
                    SP.append(i+1)
        df['Date']=pd.to_datetime(df['Date'])
        df2=df.set_index("Date")
            
        #INSIGHTS EXTRACTION
        Buying=[]
        Selling=[]
        for i in (BP):
            Buying.append(df2['Close'].iloc[i])
        for i in (SP):
            Selling.append(df2['Close'].iloc[i])
            profit=[]
        loss=[]
        for i in range(len(Buying)):
            a=Selling[i]-Buying[i]
            if(a>0):
                profit.append(a)
            else:
                loss.append(abs(a))
        total=len(profit)+len(loss)
        gross_profit=sum(profit)
        gross_loss=sum(loss)
        if(gross_profit>gross_loss):
            net=gross_profit-gross_loss
        else:
            net=gross_loss-gross_profit



        if(gross_profit>gross_loss):
            po="Profit"
            col="#b0ffc5"
            
        elif(gross_loss>gross_profit):
            po="Loss"
            col="f7abab"
        no_of_win=len(profit)
        no_of_loss=len(loss)
        # per_profitable=(no_of_win/no_of_loss)*100
        Largest_winning=max(profit)
        Largest_loss=max(loss)
        


        #CHARTING SECTION
        fig, ax = plt.subplots(figsize=(16,9))
        ax.plot(dates, close,linewidth=2)
        ax.scatter(dates, psarbull,color='green',marker=',',alpha=1,s=1)
        ax.scatter(dates, psarbear,color='red',marker=',',alpha=1,s=1)
        ax.scatter(df2.iloc[BP].index,df2.iloc[BP]['Close'],marker='^',color='g',s=200)
        ax.scatter(df2.iloc[SP].index,df2.iloc[SP]['Close'],marker='v',color='r',s=200)
        ax.set_facecolor('#F1F1F1')
        ax.grid()
       
        response = HttpResponse(content_type = 'image/png')
        canvas = FigureCanvasAgg(fig)
        canvas.print_png(response)

        canvas.draw()
        rgba = np.asarray(canvas.buffer_rgba())
        im = Image.fromarray(rgba)
        im.save(r"test.bmp")

        #mg = io.BytesIO()
        #fig.savefig(img, format='png',
                    #bbox_inches='tight')
        #img.seek(0)
        
        with open("test.bmp", "rb") as img_file:
            b64_string = base64.b64encode(img_file.read())
        # a=str(no_of_win)
        # a=Largest_loss
        
        # data=None
            
        data=[b64_string.decode('utf-8'),gross_profit,gross_loss,net,total,no_of_win,no_of_loss,Largest_winning,Largest_loss,po,col]
            # {'gross_loss':gross_loss},
            # {'b64':b64_string}

        return render(request, "result.html", {"data":data})
   
    if strategy == "Moving_Average":
        num1 = request.POST['num1']
        num2 = request.POST['num2']
        # print(num1)
        df=pd.read_csv(path)
        df1=pd.read_csv(path)
        df=df1.drop(columns=["Percent Change","Symbol"])
        df['Date']=pd.to_datetime(df['Date'])
        df2=df.set_index("Date")
        df3=df2.dropna()
        num1=5
        num2=9
        df3['MA20']=df2["Close"].rolling(int(num1)).mean()
        df3['MA50']=df2["Close"].rolling(int(num2)).mean()
        Buy= []
        Sell= []

        for i in range(len(df3)):
            if df3.MA20.iloc[i] > df3.MA50.iloc[i]\
            and df3.MA20.iloc[i-1]<df3.MA50.iloc[i-1]:
                Buy.append(i)

            elif df3.MA20.iloc[i]<df3.MA50.iloc[i]\
            and df3.MA20.iloc[i-1] > df3.MA50.iloc[i-1]:
                Sell.append(i)
             
        Buying=[]
        Selling=[]
        for i in (Buy):
            Buying.append(df2['Close'].iloc[i])
        for i in (Sell):
            Selling.append(df2['Close'].iloc[i])
        profit=[]
        loss=[]
        for i in range(len(Buying)):
            a=Selling[i]-Buying[i]
            if(a>0):
                profit.append(a)
            else:
                loss.append(abs(a))
        # total=len(profit)+len(loss)
        gross_profit=sum(profit)
        gross_loss=sum(loss)
        if(gross_profit>gross_loss):
            net=gross_profit-gross_loss
        else:
            net=gross_loss-gross_profit
        no_of_win=len(profit)
        no_of_loss=len(loss)
        total=no_of_win+no_of_loss
        # per_profitable=(no_of_win/no_of_loss)*100
        if(gross_profit>gross_loss):
            po="Profit"
            col="#b0ffc5"
            
        elif(gross_loss>gross_profit):
            po="Loss"
            col="f7abab"
        try:
            Largest_winning=max(profit)
        except:
            Largest_winning=0
        try:
            Largest_loss=max(loss)
        except:
            Largest_loss=0
         
        t = df3["Close"]
        s = df3['MA20']
        u=df3['MA50']
        fig, ax = plt.subplots(figsize=(16,9))
        ax.set_title("SMA CrossOver")
        ax.plot(t,linewidth=2,c='black')
        ax.plot(s,linewidth=1,c="orange")
        ax.plot(u)
        ax.scatter(df3.iloc[Buy].index,df3.iloc[Buy]['Close'],marker='^',color='g',s=300)
        ax.scatter(df3.iloc[Sell].index,df3.iloc[Sell]['Close'],marker='v',color='r',s=300)
        ax.grid()
        
        response = HttpResponse(content_type = 'image/png')
        canvas = FigureCanvasAgg(fig)
        canvas.print_png(response)
        #return response

        canvas.draw()
        rgba = np.asarray(canvas.buffer_rgba())
        im = Image.fromarray(rgba)
        im.save("test.bmp")

        #mg = io.BytesIO()
        #fig.savefig(img, format='png',
                    #bbox_inches='tight')
        #img.seek(0)

        with open("test.bmp", "rb") as img_file:
            b64_string = base64.b64encode(img_file.read())

        # data=[b64_string.decode('utf-8'),,b,iaf,maxaf,per_profitable,"ANIL HENC",Largest_loss]
        data=[b64_string.decode('utf-8'),gross_profit,gross_loss,net,(no_of_win+no_of_loss),no_of_win,no_of_loss,Largest_winning,Largest_loss,po,col]
        return render(request, "result.html", {"data":data })