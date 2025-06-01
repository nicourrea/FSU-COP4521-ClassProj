from flask import Flask, render_template


# init of the flask app
app = Flask(__name__)

# initial route that goes to homepage
@app.route('/')
def home():
   return render_template('home.html')

# main function run
if __name__  == '__main__':
    app.run(debug=True)
