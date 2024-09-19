from flask import Flask, render_template_string

app = Flask(__name__)

@app.route('/')
def index():
    # HTML content including your script
    html_content = '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Axi Support Bot</title>
    </head>
    <body>
        <h1>Welcome to the Axi Support Bot</h1>
        <!-- Your script goes here -->
        <script id="ze-snippet" src="https://static.zdassets.com/ekr/snippet.js?key=d0572b05-fe1b-463d-8726-ac1b7d1bb074"></script>
    </body>
    </html>
    '''
    return render_template_string(html_content)

if __name__ == '__main__':
    app.run(debug=True)
