from flask import Flask, render_template, send_file, make_response, url_for, Response, request, redirect
app = Flask(__name__)
import pandas as pd

import io
import geopandas as gpd
import contextily
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

stazioni = pd.read_csv("/workspace/Flask/correzioneVer/correzioneFilaA/file/coordfix_ripetitori_radiofonici_milano_160120_loc_final.csv", sep=";")
stazioni_geo = gpd.read_file("/workspace/Flask/correzioneVer/correzioneFilaA/file/stazioniradio.geojson")
quartieri = gpd.read_file("/workspace/Flask/esercizio6/zip files/ds964_nil_wm (2).zip")
@app.route('/', methods=['GET'])
def HomeP():
    return render_template("home.html")


@app.route('/selezione', methods=['GET'])
def selezione():
    scelta = request.args["scelta"]
    if scelta == "es1":
            # redirect, invece di usare render_template
        return redirect("/numero")
    elif scelta == "es2":
            # redirect to
        return redirect("/input")
    else:
            # redirect to
        return redirect("/dropdown")


@app.route('/numero', methods=['GET'])
def numero():
    # numero di stazione per ogni municipio
    global risultato
    risultato = stazioni.groupby(stazioni.MUNICIPIO, as_index = False).count().filter(items=["MUNICIPIO", "BOUQUET"]).sort_values(by="BOUQUET", ascending = True)
    return render_template("link1.html", tabella = risultato.to_html())


@app.route('/grafico.png', methods=['GET'])
def grafico():
        # costruzione del grafico ( a barre )

    fig, ax = plt.subplots(figsize = (6,4))

    x = risultato.MUNICIPIO
    y = risultato.BOUQUET

    ax.bar(x, y, color = "#304C89")


        #visualizzazione del grafico
    output = io.BytesIO()
    # stampa l'immagine sul canale della comunicazione
    FigureCanvas(fig).print_png(output)
    # manda come risposta, quello che ce nell'output
    return Response(output.getvalue(), mimetype='image/png')


@app.route('/input', methods=['GET'])
def inputt():
    return render_template("link2.html")


@app.route('/ricerca', methods=['GET'])
def ricerca():
    global quartiere, stazquartiere
    # prendi il quartiere inserito
    quartinserito = request.args["quartiere"]
    # cercare nel dataframe dei quartieri il quartiere inserito
    quartiere = quartieri[quartieri.NIL.str.contains(quartinserito)]
    # cercare gli stazioni all'interno del quartiere inserito
    stazquartiere = stazioni_geo[stazioni_geo.within(quartiere.geometry.squeeze())]

    return render_template("elenco1.html", tabella = stazquartiere.to_html())

@app.route('/mappa', methods=['GET'])
def mappa():
        # costruzione della mappa 

    fig, ax = plt.subplots(figsize = (12,8))

    quartiere.to_crs(epsg=3857).plot(ax=ax, alpha=0.5, edgecolor = "k", linewidth = 4)
    stazquartiere.to_crs(epsg=3857).plot(ax=ax, markersize = 6, color='red')
    contextily.add_basemap(ax=ax)
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')



@app.route('/dropdown', methods=['GET'])
def dropdown():
    # trasformare in una lista la colonna OPERATORE 
    nomistazioni = stazioni_geo.OPERATORE.to_list()
    # elimina i duplicati con set
    nomistazioni = list(set(nomistazioni))
    # ordinare da A a Z, vengono prima i numeri perche vengono ordinati in base al codice ASCII
    nomistazioni.sort()
    return render_template("dropdown.html", stazioni = nomistazioni)

@app.route('/sceltastazione', methods=['GET'])
def sceltastazione():
    global quartiere2, stazioneutente
    # prendi la stazione scelta
    stazionescelto = request.args["Stazione"]
    # cercare nel dataframe dei stazioni_geo la stazione scelta
    stazioneutente = stazioni_geo[stazioni_geo.OPERATORE == stazionescelto]
    # cercare il quartiere che contiene la stazione scelta
    quartiere2 = quartieri[quartieri.contains(stazioneutente.geometry.squeeze())]

    return render_template("listastazione.html", quartiere2 = quartiere2.NIL)

@app.route('/mappaquartiere', methods=['GET'])
def mappaquartiere():
        # costruzione della mappa 

    fig, ax = plt.subplots(figsize = (12,8))

    quartiere2.to_crs(epsg=3857).plot(ax=ax, alpha=0.5, edgecolor = "k", linewidth = 4)
    stazioneutente.to_crs(epsg=3857).plot(ax=ax, markersize = 6, color='red')
    contextily.add_basemap(ax=ax)
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=3245, debug=True)