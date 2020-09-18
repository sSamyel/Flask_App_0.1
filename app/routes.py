from datetime import datetime

from PIL import Image, ImageDraw, ImageFont, ImageFilter
import sys
from flask import render_template, redirect, request
from flask_login import login_user, logout_user, login_required, current_user
from imageio import imwrite

from app import app, db
from app.forms import LoginForm, RegistrationForm, SettingForm, FileForm, EditorForm, GalleryForm, Editor2Form, CutForm, RotateForm, ResizeForm, BrightForm, ContrastForm
from app.models import User, Gallery



import keras
from keras.models import load_model, model_from_json
from keras.applications.inception_resnet_v2 import InceptionResNetV2
from keras.preprocessing import image
from keras.engine import Layer
from keras.applications.inception_resnet_v2 import preprocess_input
from keras.layers import Conv2D, UpSampling2D, InputLayer, Conv2DTranspose, Input, Reshape, merge, concatenate
from keras.layers import Activation, Dense, Dropout, Flatten
from keras.layers.normalization import BatchNormalization
from keras.callbacks import TensorBoard
from keras.models import Sequential, Model
from keras.layers.core import RepeatVector, Permute
from keras.preprocessing.image import ImageDataGenerator, array_to_img, img_to_array, load_img
from skimage.color import rgb2lab, lab2rgb, rgb2gray, gray2rgb
from skimage.transform import resize
from skimage.io import imsave
import numpy as np
import os
import random
import tensorflow as tf


@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


@app.route('/mainPage', methods=['GET','POST'])
def index():
    global username,commentary, tname, tmail, login, image, inception
    form = LoginForm()
    form2 = RegistrationForm()
    if form.validate_on_submit():
        usname = form.username.data
        password = form.password.data
        users = User.query.all()
        for u in users:
            if usname == u.username and password == u.password_hash:
                login_user(u)
                username = usname
                commentary = u.commentary
                tname = u.login
                tmail = u.email
                image = u.picture
                return render_template("mainPage.html", username=current_user.username, commentary=current_user.commentary, login=current_user.login, form=form, form2=form2, shown='yes', image=image)
    if form2.validate_on_submit():
        username = form2.username.data
        password = form2.password.data
        login = form2.login.data
        fullname = form2.fullname.data
        email = form2.email.data
        picture = "avatar.png"
        commentary = "Добро пожаловать!"
        user = User(username=username, password_hash=password, login=login, fullname=fullname, email=email, picture=picture, commentary=commentary)
        db.session.add(user)
        db.session.commit()
        users = User.query.all()
        for u in users:
            if u.username == username:
                p = Gallery(user = username, gallery='', count=0, user_id=u.id)
                db.session.add(p)
                db.session.commit()
        username = ""
        tname = ""
        tmail = ""
        return render_template('mainPage.html', username = username, commentary = commentary, login = tname, form=form, form2=form2, shown='yes', image=picture)
    return render_template('mainPage.html', username = username, commentary = commentary, login = tname, form=form, form2=form2, shown='no', image=image)


@app.route('/main')
def main():
    return redirect('/mainPage')

@app.route('/')
@app.route('/seti')
def seti():
    return redirect('/main')

#imot = inception
#inception.graph = tf.get_default_graph()

def create_inception_embedding(grayscaled_rgb, inception):
    grayscaled_rgb_resized = []
    for i in grayscaled_rgb:
        i = resize(i, (299, 299, 3), mode='constant')
        grayscaled_rgb_resized.append(i)
    grayscaled_rgb_resized = np.array(grayscaled_rgb_resized)
    grayscaled_rgb_resized = preprocess_input(grayscaled_rgb_resized)
    with inception.graph.as_default():
        embed = inception.predict(grayscaled_rgb_resized)
    return embed

@app.route('/editor2', methods=['GET','POST'])
def editor2():
    form = Editor2Form()
    form2 = CutForm()
    form3 = RotateForm()
    form4 = ResizeForm()
    form5 = BrightForm()
    form6 = ContrastForm()
    if form.validate_on_submit():
        image = form.file_object.data
        image.save(app.root_path + '/static/' + 'images.jpg')
        return render_template('Editor2.html', image='images.jpg', color='no',form=form, form2=form2, form3=form3, form4=form4, form5=form5, form6=form6)
    return render_template('Editor2.html', image='none', color='no',form=form, form2=form2, form3=form3, form4=form4, form5=form5, form6=form6)

@app.route('/editor2/cut', methods=['GET', 'POST'])
def cut():
    form = Editor2Form()
    form2 = CutForm()
    form3 = RotateForm()
    form4 = ResizeForm()
    form5 = BrightForm()
    form6 = ContrastForm()
    if form2.validate_on_submit():
        x1 = form2.x1.data;
        y1 = form2.y1.data;
        x2 = form2.x2.data;
        y2 = form2.y2.data;
        print(x1 + " " + y1 + " " + x2 + " " + y2)
        image = Image.open(app.root_path + '/static/images.jpg')
        cropped = image.crop((int(x1), int(y1), int(x2), int(y2)))
        cropped.save(app.root_path + '/static/' + 'cropped' + 'image.jpg')
        croppedFile = "cropped"+"image.jpg"
        return render_template('Editor2.html', image=croppedFile, color='no',form=form, form2=form2, form3=form3, form4=form4, form5=form5, form6=form6)

@app.route('/editor2/rotate', methods=['GET', 'POST'])
def rotate():
    form = Editor2Form()
    form2 = CutForm()
    form3 = RotateForm()
    form4 = ResizeForm()
    form5 = BrightForm()
    form6 = ContrastForm()
    if form3.validate_on_submit():
        image = Image.open(app.root_path + '/static/images.jpg')
        num = request.form['numRange']
        rotated = image.rotate(int(num))
        rotated.save(app.root_path + '/static/' + 'rotated' + 'image.jpg')
        rotatedFile = "rotated"+"image.jpg"
        return render_template('Editor2.html', image=rotatedFile, color='no',form=form, form2=form2, form3=form3, form4=form4, form5=form5, form6=form6)

@app.route('/editor2/resize', methods=['GET', 'POST'])
def resizen():
    form = Editor2Form()
    form2 = CutForm()
    form3 = RotateForm()
    form4 = ResizeForm()
    form5 = BrightForm()
    form6 = ContrastForm()
    if form4.validate_on_submit():
        numHeight = request.form['numHeight']
        numWidth = request.form['numWidth']
        image = Image.open(app.root_path + '/static/images.jpg')
        imageResize = image.resize((int(numHeight), int(numWidth)), Image.ANTIALIAS)
        imageResize.save(app.root_path + '/static/' + 'resize' + 'image.jpg')
        resizeFile = "resize"+"image.jpg"
        return render_template('Editor2.html', image=resizeFile, color='no',form=form, form2=form2, form3=form3, form4=form4, form5=form5, form6=form6)


@app.route('/editor2/bright', methods=['GET', 'POST'])
def bright():
    form = Editor2Form()
    form2 = CutForm()
    form3 = RotateForm()
    form4 = ResizeForm()
    form5 = BrightForm()
    form6 = ContrastForm()
    if form4.validate_on_submit():
        brightness = float(request.form['numRangeBright'])
        source = Image.open(app.root_path + '/static/images.jpg')
        result = Image.new('RGB', source.size)
        for x in range(source.size[0]):
            for y in range(source.size[1]):
                r, g, b = source.getpixel((x, y))

                red = int(r * brightness)
                red = min(255, max(0, red))

                green = int(g * brightness)
                green = min(255, max(0, green))

                blue = int(b * brightness)
                blue = min(255, max(0, blue))

                result.putpixel((x, y), (red, green, blue))
        result.save(app.root_path + '/static/' + 'bright' + 'image.jpg')
        BrightFile = "bright"+"image.jpg"
        return render_template('Editor2.html', image=BrightFile, color='no',form=form, form2=form2, form3=form3, form4=form4, form5=form5, form6=form6)

@app.route('/editor2/contrast', methods=['GET', 'POST'])
def contrast():
    form = Editor2Form()
    form2 = CutForm()
    form3 = RotateForm()
    form4 = ResizeForm()
    form5 = BrightForm()
    form6 = ContrastForm()
    if form4.validate_on_submit():
        coefficient = float(request.form['numRangeContrast'])
        source = Image.open(app.root_path + '/static/images.jpg')
        result = Image.new('RGB', source.size)

        avg = 0
        for x in range(source.size[0]):
            for y in range(source.size[1]):
                r, g, b = source.getpixel((x, y))
                avg += r * 0.299 + g * 0.587 + b * 0.114
        avg /= source.size[0] * source.size[1]

        palette = []
        for i in range(256):
            temp = int(avg + coefficient * (i - avg))
            if temp < 0:
                temp = 0
            elif temp > 255:
                temp = 255
            palette.append(temp)

        for x in range(source.size[0]):
            for y in range(source.size[1]):
                r, g, b = source.getpixel((x, y))
                result.putpixel((x, y), (palette[r], palette[g], palette[b]))
        result.save(app.root_path + '/static/' + 'contrast' + 'image.jpg')
        BrightFile = "contrast"+"image.jpg"
        return render_template('Editor2.html', image=BrightFile, color='no',form=form, form2=form2, form3=form3, form4=form4, form5=form5, form6=form6)

@app.route('/editor2/grayScale', methods=['GET', 'POST'])
def grayScale():
    form = Editor2Form()
    form2 = CutForm()
    form3 = RotateForm()
    form4 = ResizeForm()
    form5 = BrightForm()
    form6 = ContrastForm()
    source = Image.open(app.root_path + '/static/images.jpg')
    result = Image.new('RGB', source.size)
    for x in range(source.size[0]):
        for y in range(source.size[1]):
            r, g, b = source.getpixel((x, y))
            gray = int(r * 0.2126 + g * 0.7152 + b * 0.0722)
            result.putpixel((x, y), (gray, gray, gray))
    result.save(app.root_path + '/static/' + 'grayScale' + 'image.jpg')
    BrightFile = "grayScale"+"image.jpg"
    return render_template('Editor2.html', image=BrightFile, color='no',form=form, form2=form2, form3=form3, form4=form4, form5=form5, form6=form6)

@app.route('/editor2/whiteBlack', methods=['GET', 'POST'])
def whiteBlack():
    form = Editor2Form()
    form2 = CutForm()
    form3 = RotateForm()
    form4 = ResizeForm()
    form5 = BrightForm()
    form6 = ContrastForm()
    source = Image.open(app.root_path + '/static/images.jpg')
    result = Image.new('RGB', source.size)
    brightness = 0.8
    separator = 255 / brightness / 2 * 3
    for x in range(source.size[0]):
        for y in range(source.size[1]):
            r, g, b = source.getpixel((x, y))
            total = r + g + b
            if total > separator:
                result.putpixel((x, y), (255, 255, 255))
            else:
                result.putpixel((x, y), (0, 0, 0))
    result.save(app.root_path + '/static/' + 'whiteBlack' + 'image.jpg')
    BrightFile = "whiteBlack"+"image.jpg"
    return render_template('Editor2.html', image=BrightFile, color='no',form=form, form2=form2, form3=form3, form4=form4, form5=form5, form6=form6)

@app.route('/editor2/negative', methods=['GET', 'POST'])
def negative():
    form = Editor2Form()
    form2 = CutForm()
    form3 = RotateForm()
    form4 = ResizeForm()
    form5 = BrightForm()
    form6 = ContrastForm()
    source = Image.open(app.root_path + '/static/images.jpg')
    result = Image.new('RGB', source.size)
    for x in range(source.size[0]):
        for y in range(source.size[1]):
            r, g, b = source.getpixel((x, y))
            result.putpixel((x, y), (255 - r, 255 - g, 255 - b))
    result.save(app.root_path + '/static/' + 'negative' + 'image.jpg')
    BrightFile = "negative"+"image.jpg"
    return render_template('Editor2.html', image=BrightFile, color='no',form=form, form2=form2, form3=form3, form4=form4, form5=form5, form6=form6)

@app.route('/editor2/sepia', methods=['GET', 'POST'])
def sepia():
    form = Editor2Form()
    form2 = CutForm()
    form3 = RotateForm()
    form4 = ResizeForm()
    form5 = BrightForm()
    form6 = ContrastForm()
    source = Image.open(app.root_path + '/static/images.jpg')
    result = Image.new('RGB', source.size)
    for x in range(source.size[0]):
        for y in range(source.size[1]):
            r, g, b = source.getpixel((x, y))
            red = int(r * 0.393 + g * 0.769 + b * 0.189)
            green = int(r * 0.349 + g * 0.686 + b * 0.168)
            blue = int(r * 0.272 + g * 0.534 + b * 0.131)
            result.putpixel((x, y), (red, green, blue))
    result.save(app.root_path + '/static/' + 'sepia' + 'image.jpg')
    BrightFile = "sepia"+"image.jpg"
    return render_template('Editor2.html', image=BrightFile, color='no',form=form, form2=form2, form3=form3, form4=form4, form5=form5, form6=form6)

@app.route('/editor2/text', methods=['GET', 'POST'])
def text():
    form = Editor2Form()
    form2 = CutForm()
    form3 = RotateForm()
    form4 = ResizeForm()
    form5 = BrightForm()
    form6 = ContrastForm()
    source = Image.open(app.root_path + '/static/images.jpg')
    idraw = ImageDraw.Draw(source)
    text = request.form['x']
    fontText = request.form['font'] + ".ttf"
    sizeText = int(request.form['size'])
    x = int(request.form['x1'])
    y = int(request.form['y1'])
    #print(text + ' ' + fontText + ' ' + sizeText + ' ' + x + ' ' + y)
    font = ImageFont.truetype(fontText, size=sizeText)
    idraw.text((x, y), text, font=font)
    source.save(app.root_path + '/static/' + 'idraw' + 'image.jpg')
    BrightFile = "idraw"+"image.jpg"
    return render_template('Editor2.html', image=BrightFile, color='no',form=form, form2=form2, form3=form3, form4=form4, form5=form5, form6=form6)

@app.route('/editor2/fuzziness', methods=['GET', 'POST'])
def fuzziness():
    form = Editor2Form()
    form2 = CutForm()
    form3 = RotateForm()
    form4 = ResizeForm()
    form5 = BrightForm()
    form6 = ContrastForm()
    image = Image.open(app.root_path + '/static/images.jpg')
    blurred_jelly = image.filter(ImageFilter.BLUR)
    blurred_jelly.save(app.root_path + '/static/' + 'fuzziness' + 'image.jpg')
    BrightFile = "fuzziness"+"image.jpg"
    return render_template('Editor2.html', image=BrightFile, color='no',form=form, form2=form2, form3=form3, form4=form4, form5=form5, form6=form6)

@app.route('/editor2/sharpness', methods=['GET', 'POST'])
def sharpness():
    form = Editor2Form()
    form2 = CutForm()
    form3 = RotateForm()
    form4 = ResizeForm()
    form5 = BrightForm()
    form6 = ContrastForm()
    image = Image.open(app.root_path + '/static/images.jpg')
    blurred_jelly = image.filter(ImageFilter.SHARPEN)
    blurred_jelly.save(app.root_path + '/static/' + 'sharpness' + 'image.jpg')
    BrightFile = "sharpness"+"image.jpg"
    return render_template('Editor2.html', image=BrightFile, color='no',form=form, form2=form2, form3=form3, form4=form4, form5=form5, form6=form6)

@app.route('/editor2/reverse', methods=['GET', 'POST'])
def reverse():
    form = Editor2Form()
    form2 = CutForm()
    form3 = RotateForm()
    form4 = ResizeForm()
    form5 = BrightForm()
    form6 = ContrastForm()
    image = Image.open(app.root_path + '/static/images.jpg')
    result = np.fliplr(image)
    im = Image.fromarray(result)
    im.save(app.root_path + '/static/' + 'reverse' + 'image.jpg')
    BrightFile = "reverse"+"image.jpg"
    return render_template('Editor2.html', image=BrightFile, color='no',form=form, form2=form2, form3=form3, form4=form4, form5=form5, form6=form6)

@app.route('/editor3', methods=['GET', 'POST'])
def color():
    global username
    form = Editor2Form()
    form2 = CutForm()
    form3 = RotateForm()
    form4 = ResizeForm()
    form5 = BrightForm()
    form6 = ContrastForm()
    users = User.query.all()
    for u in users:
        if u.username == username:
            userId = u.id
    gallery = Gallery.query.all()
    for p in gallery:
        if p.user_id == userId:
            countPhoto = p.count
            galleryPhoto = p.gallery

    keras.backend.clear_session()
    inception = InceptionResNetV2(weights="inception_resnet_v2_weights_tf_dim_ordering_tf_kernels.h5", include_top=True)
    inception.graph = tf.get_default_graph()

    model = load_model('model.h5')

    color_me = []
    #for filename in os.listdir(app.root_path + '/Test'):
    color_me.append(img_to_array(load_img(app.root_path + '/static/' + 'images.jpg')))
    color_me = np.array(color_me, dtype=float)
    gray_me = gray2rgb(rgb2gray(1.0 / 255 * color_me))
    color_me_embed = create_inception_embedding(gray_me, inception)
    color_me = rgb2lab(1.0 / 255 * color_me)[:, :, :, 0]
    color_me = color_me.reshape(color_me.shape + (1,))

    # Test model
    output = model.predict([color_me, color_me_embed])
    output = output * 128

    # Output colorizations
    for i in range(len(output)):
        cur = np.zeros((256, 256, 3))
        cur[:, :, 0] = color_me[i][:, :, 0]
        cur[:, :, 1:] = output[i]
        countPhoto = countPhoto + 1
        name = username + "img_" + str(countPhoto) + ".png"
        imsave("app/static/" + name, lab2rgb(cur))
        imsave('app/static/colorImage.jpg', lab2rgb(cur))
        p.count = countPhoto
        p.gallery = galleryPhoto + " " + name
        db.session.commit()
    return render_template('Editor2.html', image='images.jpg', color='yes',form=form, form2=form2, form3=form3, form4=form4, form5=form5, form6=form6)

@app.route('/editor', methods=['GET','POST'])
def editor():
    global username
    form = EditorForm()
    if form.validate_on_submit():
        users = User.query.all()
        for u in users:
            if u.username == username:
                 userId = u.id
        gallery = Gallery.query.all()
        for p in gallery:
            if p.user_id == userId:
                countPhoto = p.count
                galleryPhoto = p.gallery

        picture = form.file_object.data
        picture.save(app.root_path + '/Test/' + 'images.jpg')
        keras.backend.clear_session()
        inception = InceptionResNetV2(weights="inception_resnet_v2_weights_tf_dim_ordering_tf_kernels.h5", include_top=True)
        inception.graph = tf.get_default_graph()

        model = load_model('model.h5')

        color_me = []
        for filename in os.listdir(app.root_path + '/Test'):
            color_me.append(img_to_array(load_img(app.root_path + '/Test/' + filename)))
        color_me = np.array(color_me, dtype=float)
        gray_me = gray2rgb(rgb2gray(1.0 / 255 * color_me))
        color_me_embed = create_inception_embedding(gray_me, inception)
        color_me = rgb2lab(1.0 / 255 * color_me)[:, :, :, 0]
        color_me = color_me.reshape(color_me.shape + (1,))

        # Test model
        output = model.predict([color_me, color_me_embed])
        output = output * 128

        # Output colorizations
        for i in range(len(output)):
            cur = np.zeros((256, 256, 3))
            cur[:, :, 0] = color_me[i][:, :, 0]
            cur[:, :, 1:] = output[i]
            countPhoto = countPhoto + 1
            name = username + "img_" + str(countPhoto) + ".png"
            imsave("app/static/" + name, lab2rgb(cur))
            p.count = countPhoto
            p.gallery = galleryPhoto + " " + name
            db.session.commit()
        return render_template('Editor.html', image=name, form=form)
    return render_template('Editor.html', image='none', form=form)


@app.route('/gallery', methods=['GET','POST'])
def gallery():
    global username
    form = GalleryForm()
    users = User.query.all()
    for u in users:
        if u.username == username:
                userId = u.id
    gallery = Gallery.query.all()
    for p in gallery:
        if p.user_id == userId:
            countPhoto = p.count
            galleryPhoto = p.gallery
            arr = galleryPhoto.split(" ")
            arr.pop(0)
    if form.validate_on_submit():
        galleryPhoto = galleryPhoto.replace(" "+form.text.data, "")
        print(galleryPhoto)
        p.gallery = galleryPhoto;
        db.session.commit()
        p.gallery = galleryPhoto;
        arr = galleryPhoto.split(" ")
        arr.pop(0)
        return render_template('PhotoGallery.html', count=countPhoto, image=arr, form=form)
    return render_template('PhotoGallery.html', count = countPhoto, image = arr, form=form)

@app.route('/login', methods=['GET','POST'])
def login():
    global username,commentary, tname, tmail
    form = LoginForm()
    #users = User.query.all()
    #for u in users:
        #db.session.delete(u)
    #db.session.commit()
    if form.validate_on_submit():
        usname = form.username.data
        password = form.password.data
        users = User.query.all()
        for u in users:
            if usname == u.username and password == u.password_hash:
                login_user(u)
                username = usname
                commentary = u.commentary
                tname = u.login
                tmail = u.email
                return render_template("mainPage.html", username=current_user.username, commentary=current_user.commentary, login=current_user.login, form=form)
    logout_user()
    return render_template("login.html", form=form)

username = ""
origin = ""
tmail=""
tname = ""
image = ""
commentary = "Добро пожаловать!"

@app.route('/registration', methods=['GET','POST'])
def registration():
    global NUM_USER
    global username
    global login, tname, tmail
    form = RegistrationForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        login = form.login.data
        fullname = form.fullname.data
        email = form.email.data
        picture = "avatar.png"
        commentary = "Добро пожаловать!"
        user = User(username=username, password_hash=password, login=login, fullname=fullname, email=email, picture=picture, commentary=commentary)
        db.session.add(user)
        db.session.commit()

        NUM_USER += 1
        return redirect('/mainPage')
    else:
        logout_user()
    return render_template("registration.html", form=form)

@app.route('/profile', methods = ['GET', 'POST'])
def profile():
    global username
    users = User.query.all()
    for u in users:
        if u.username == username:
            name = u.username
            fullname = u.fullname
            login = u.login
            email = u.email
            form = FileForm()
            fname = u.picture
            if form.validate_on_submit():
                f = form.file_object.data
                fname = f.filename
                u.picture = f.filename
                db.session.commit()
            return render_template("profile.html", name=name, fullname=fullname, login=login, email=email, fname=fname, form=form )
    return redirect('/login')


@app.route("/logout")
@login_required
def logout():
    global commentary, tname, username
    logout_user()
    username = ""
    tname = ""
    commentary = "Добро пожаловать!"
    return redirect('/main')

@app.route('/setting', methods=['GET', 'POST'])
def setting():
    global tmail, username, commentary, origin, tname, image
    origin = username
    users = User.query.all()
    for u in users:
        if u.username == username:
            form = SettingForm(current_user.username, current_user.email)
            if form.validate_on_submit():
                usernam = form.username.data
                password = form.password.data
                login = form.login.data
                fullname = form.fullname.data
                email = form.email.data
                picture = form.file_object.data
                commentar = form.commentary.data
                if commentar != "":
                   u.commentary = commentar
                   commentary = commentar
                if picture != None:
                   picture.save(app.root_path + '/static/' + picture.filename)
                   u.picture = picture.filename
                   image = picture.filename
                if email != "":
                   tmail = email
                   u.email = email
                if fullname != "":
                   u.fullname = fullname
                if login != "":
                   u.login = login
                   tname = login
                if usernam != "":
                   u.username = usernam
                   username = usernam
                if password != "":
                   u.password_hash = password
                db.session.commit()
                return redirect('/profile')
            return render_template('setting.html', form=form)


app.run(port=8090, host='127.0.0.1')