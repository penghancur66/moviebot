from flask import Flask, request, jsonify
from datetime import date
import os
import dialogflow
import requests
import json
import pymysql.cursors

app = Flask(__name__)

# run Flask app
if __name__ == "__main__":
    app.run()

@app.route('/get_movie_detail', methods=['POST'])
def get_movie_detail():
    data = request.get_json(silent=True)
    message = data['queryResult']['queryText']
    movie = data['queryResult']['parameters']['movie']
    api_key = os.getenv('OMDB_API_KEY')
    movie_detail = requests.get('http://www.omdbapi.com/?t={0}&apikey={1}'.format(movie, api_key)).content
    movie_det = json.loads(movie_detail)

    connection = pymysql.connect(host='db4free.net', user='mangtri78', password='mangtri123', db='db_chatbot', cursorclass=pymysql.cursors.DictCursor)
    lastidout = ''
    try:
        with connection.cursor() as cursor:
            sql = "INSERT INTO inbox (tanggal, pesan) VALUES (%s, %s)"
            cursor.execute(sql, (date.today().strftime("%Y-%m-%d"), message))
            lastid = cursor.lastrowid
            sql = "INSERT INTO outbox (id_inbox, tanggal, title, released, actors, plot, runtime, genre) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
            cursor.execute(sql, (lastid, date.today().strftime("%Y-%m-%d"), movie_det['Title'], movie_det['Released'], movie_det['Actors'], movie_det['Plot'], movie_det['Runtime'], movie_det['Genre']))
            lastidout = cursor.lastrowid
        connection.commit()
    except Exception as error:
        print(error)

    try:
        with connection.cursor() as cursor:    
            perbarui = "UPDATE outbox SET status = '1' WHERE id = %s"
            cursor.execute(perbarui,(lastidout))
        connection.commit()
    except Exception as error:
        print(error)

    try:
        res = ''
        with connection.cursor() as cursor:
            response = "SELECT title, released, actors, plot, runtime, genre from outbox WHERE id = %s"
            cursor.execute(response,(lastidout))
            cari = cursor.fetchall()
            for row in cari:
                res = "Title: {}\nReleased: {}\nActors: {}\nPlot: {}\nRuntime: {}\nGenre: {}".format(row['title'], row['released'], row['actors'], row['plot'], row['runtime'], row['genre'])
            print(lastidout)
        reply = {
            "fulfillmentText": res,
        }
        return jsonify(reply)
    except Exception as error:
        print(error)
    finally:
        connection.close()
