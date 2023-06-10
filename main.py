from flask import Flask, render_template, request
import pylucene
from pylucene import retrieve



num_docs = 10
index_dir = 'sample_lucene_index/'
app = Flask(__name__)

@app.route("/", methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        keyword = request.form['keyword']
        # perform search logic here
        # replace the following with the appropriate search logic
        results = [retrieve(index_dir, keyword, num_docs)] #my new attempt
        #results = ['Result 1', 'Result 2', 'Result 3']
        return render_template('index.html', keyword=keyword, results=results)
    
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)
    
    
