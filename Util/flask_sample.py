from flask import Flask
app = Flask(__name__)

@app.route("/")
def flask_sample():
    return '''
                <!DOCTYPE html>
                <html>
                    <body>
                        <div style="text-align:center;">
                            <div style="background-color:#eee;padding:10px 20px;">
                                <h2 style="font-family:Georgia, 'Times New Roman', Times, serif;color:#FF0000">TEMPERATURA DO USUÁRIO MUITO ALTA</h2>
                            </div>
                            
                            <div style="text-align:center;">
                                <h3>INVENZI</h3>
                                <p>Nome:nome</p>
                                <p>ID Usuário:chid</p>
                                <p>Documento:idnumber</p>
                                <p>Empresa:empresa</p>
                                <p>Local:sourcename</p>
                                <p>Data/Hora:date</p>
                                <a href="#">Read more</a>
                            </div>
                        </div>
                    </body>
                </html>
            '''

if __name__ == "__main__":
    app.run()

# <!DOCTYPE html>
# <html lang="en">
# <head>
#     <meta charset="UTF-8">
#     <title>Make A Short URL</title>
# </head>
# <body>
# <h1>Make A Short URL</h1>
# <form action="shortenurl">
#     <label for="url">Enter URL</label>
#     <input type="url" name="url" value="" required>
#     <label for="shortcode">Enter Name</label>
#     <input type="text" name="shortcode" value="" required>
#     <input type="submit" value="Submit">
# </form>

# </body>
# </html>