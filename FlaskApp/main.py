from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/", methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        keyword = request.form['keyword']
        # perform search logic here
        # replace the following with the appropriate search logic
        results = ['Result 1', 'Result 2', 'Result 3']
        return render_template('index.html', keyword=keyword, results=results)
    
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)