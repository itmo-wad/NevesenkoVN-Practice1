from flask import Flask, render_template, redirect, request, url_for, session, flash
import os
import pymongo
import bcrypt
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "testing"

picFolder = os.path.join('static','images')
app.config['UPLOAD_FOLDER'] = picFolder
app.config['UPLOAD_IMAGES_FOLDER'] = os.path.join('static','uploaded') 
favicon = os.path.join(app.config['UPLOAD_FOLDER'], 'favicon.ico')
style = os.path.join(app.config['UPLOAD_FOLDER'], '../style.css')

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

client = pymongo.MongoClient("mongodb+srv://N0L1F3R:Qwe12345@cluster0.9ye0c.mongodb.net/test")
db = client.get_database('users')
records = db.register

def allowed_file(filename):
  return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/")
def redirectToSignUp():
  return redirect("/auth")

@app.route("/secret")
def index():
  if session.get('userName') is None:
    return redirect("/auth")
  return render_template("index.html", fav = favicon, styleCss = style)


@app.route("/auth", methods=['post', 'get'])
def authentification():
  message = 'Please login to your account'

  if request.method == "POST":
    user = request.form.get("userName")
    password = request.form.get("password")

    user_found = records.find_one({"userName": user})
    if user_found:
      user_val = user_found['userName']
      passwordcheck = user_found['password']
            
      if password == passwordcheck:
        session["userName"] = user_val
        return redirect("/secret")
      else:
        if "userName" in session:
          return redirect("/secret")
        message = 'Wrong password'
        return render_template('auth.html', message=message, fav = favicon, styleCss = style)
    else:
      message = 'user not found'
      return render_template('auth.html', message=message, fav = favicon, styleCss = style)
  return render_template("auth.html", fav = favicon, styleCss = style)

@app.route("/signup", methods=['post', 'get'])

def signUp():
  message = ''
  if request.method == "POST":
    user = request.form.get("userName")
        
    password1 = request.form.get("password1")
    password2 = request.form.get("password2")
        
    user_found = records.find_one({"userName": user})

    if user_found:
      message = 'There already is a user by that name'
      return render_template('signup.html', message=message, fav = favicon, styleCss = style)
    if password1 != password2:
      message = 'Passwords should match!'
      return render_template('signup.html', message=message, fav = favicon, styleCss = style)
    else:
      user_input = {'userName': user, 'password': password2}
      records.insert_one(user_input)
      return render_template('index.html', fav = favicon, styleCss = style)

  return render_template("signup.html", fav = favicon, styleCss = style)

@app.route("/upload", methods=['post', 'get'])
def uploadImg():
  message = ''
  if request.method == 'POST':
    if 'file' not in request.files:
      flash('No file part')
      return redirect("/upload")
    file = request.files['file']
    if file.filename == '':
      flash('No selected file')
      return redirect("/upload")
    if file and allowed_file(file.filename):
      filename = secure_filename(file.filename)
      file.save(os.path.join(app.config['UPLOAD_IMAGES_FOLDER'], filename))
      filepath = os.path.join(app.config['UPLOAD_IMAGES_FOLDER'], filename)
      return render_template('upload.html', filename = filename, fav = favicon, styleCss = style)
  return render_template('upload.html', fav = favicon, styleCss = style)

@app.route("/uploaded/<filename>")
def ShowImg(filename):
  return redirect('static', filename='Uploaded/' + filename)



if __name__ == "__main__":
  app.run(host="localhost", port=5000)