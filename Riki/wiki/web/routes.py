"""
    Routes
    ~~~~~~
"""
from wiki.web.user import UserManager
import os
from flask import Blueprint
from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from flask_login import current_user
from flask_login import login_required
from flask_login import login_user
from flask_login import logout_user
from wiki.core import Processor
from wiki.web.forms import EditorForm
from wiki.web.forms import LoginForm
from wiki.web.forms import SearchForm
from wiki.web.forms import URLForm
from wiki.web import current_wiki
from wiki.web import current_users
from wiki.web.user import protect
from wiki.web.forms import RegisterForm
from config import USER_DIR
from wiki.web.user import UserRegistrationController
from wiki.web.file_storage import FileManager

bp = Blueprint('wiki', __name__)
DIRECTORY = "UserFileStorage"


@bp.route('/')
@protect
def home():
    page = current_wiki.get('home')
    if page:
        return display('home')
    return render_template('home.html')


@bp.route('/index/')
@protect
def index():
    pages = current_wiki.index()
    return render_template('index.html', pages=pages)


@bp.route('/<path:url>/')
@protect
def display(url):
    page = current_wiki.get_or_404(url)
    return render_template('page.html', page=page)


@bp.route('/create/', methods=['GET', 'POST'])
@protect
def create():
    form = URLForm()
    if form.validate_on_submit():
        return redirect(url_for(
            'wiki.edit', url=form.clean_url(form.url.data)))
    return render_template('create.html', form=form)


@bp.route('/edit/<path:url>/', methods=['GET', 'POST'])
@protect
def edit(url):
    page = current_wiki.get(url)
    form = EditorForm(obj=page)
    if form.validate_on_submit():
        if not page:
            page = current_wiki.get_bare(url)
        form.populate_obj(page)
        page.save()
        flash('"%s" was saved.' % page.title, 'success')
        return redirect(url_for('wiki.display', url=url))
    return render_template('editor.html', form=form, page=page)


@bp.route('/preview/', methods=['POST'])
@protect
def preview():
    data = {}
    processor = Processor(request.form['body'])
    data['html'], data['body'], data['meta'] = processor.process()
    return data['html']


@bp.route('/move/<path:url>/', methods=['GET', 'POST'])
@protect
def move(url):
    page = current_wiki.get_or_404(url)
    form = URLForm(obj=page)
    if form.validate_on_submit():
        newurl = form.url.data
        current_wiki.move(url, newurl)
        return redirect(url_for('wiki.display', url=newurl))
    return render_template('move.html', form=form, page=page)


@bp.route('/delete/<path:url>/')
@protect
def delete(url):
    page = current_wiki.get_or_404(url)
    current_wiki.delete(url)
    flash('Page "%s" was deleted.' % page.title, 'success')
    return redirect(url_for('wiki.home'))


@bp.route('/tags/')
@protect
def tags():
    tags = current_wiki.get_tags()
    return render_template('tags.html', tags=tags)


@bp.route('/tag/<string:name>/')
@protect
def tag(name):
    tagged = current_wiki.index_by_tag(name)
    return render_template('tag.html', pages=tagged, tag=name)


@bp.route('/search/', methods=['GET', 'POST'])
@protect
def search():
    form = SearchForm()
    if form.validate_on_submit():
        results = current_wiki.search(form.term.data, form.ignore_case.data)
        return render_template('search.html', form=form,
                               results=results, search=form.term.data)
    return render_template('search.html', form=form, search=None)


@bp.route('/user/login/', methods=['GET', 'POST'])
def user_login():
    form = LoginForm()
    if form.validate_on_submit():
        user = current_users.get_user(form.name.data)
        login_user(user)
        user.set('authenticated', True)
        flash('Login successful.', 'success')
        return redirect(request.args.get("next") or url_for('wiki.index'))
    return render_template('login.html', form=form)


@bp.route('/user/logout/')
@login_required
def user_logout():
    current_user.set('authenticated', False)
    logout_user()
    flash('Logout successful.', 'success')
    return redirect(url_for('wiki.index'))


@bp.route('/user/')
@login_required
def user_index():
    user_data = {
        'name': current_user.name,
        'email': current_user.get('email'),
        'active': current_user.is_active(),
        'authenticated': current_user.is_authenticated(),
        'roles': current_user.get('roles'),

    }
    return render_template("account.html", user=user_data)


@bp.route('/user/edit')
def user_edit():
    pass


@bp.route('/user/create/', methods=['GET', 'POST'])
def user_create():
    form = RegisterForm()
    user_manager = UserManager(USER_DIR)
    registration_controller = UserRegistrationController(user_manager)

    if form.validate_on_submit() and registration_controller.register_user(form):
        return redirect(url_for('wiki.user_login'))

    return render_template('register.html', form=form)


@bp.route('/user/<int:user_id>/')
def user_admin(user_id):
    pass


@bp.route('/user/delete/<string:user_id>/', methods=['GET', 'POST'])
@protect
def user_delete(user_id):
    user = current_users.get_user(user_id)
    if request.method == 'POST':
        # Perform the user deletion logic here
        user_manager = UserManager(USER_DIR)
        user_manager.delete_user(user.name)
        flash('User {} has been deleted.'.format(user.name), 'success')
        return redirect(url_for('wiki.index'))

    return render_template('delete_user.html', user=user)


"""
    Error Handlers
    ~~~~~~~~~~~~~~
"""


@bp.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404


@bp.route('/file_storage/', methods=['GET', 'POST'])
@protect
def file_storage():
    file_manager = FileManager(DIRECTORY)
    files = file_manager.get_downloadable_files()
    return render_template('file_storage.html', files=files)


@bp.route('/delete_file/<path:file_name>/')
@protect
def delete_file(file_name):
    file_manager = FileManager(DIRECTORY)
    success = file_manager.delete_file(file_name)
    if success:
        flash(f"Successfully deleted file {file_name}")
    else:
        flash(f"Unknown issue... failed to delete file {file_name}")
    return redirect(url_for('wiki.file_storage'))


@bp.route('/download_file/<path:file_name>/')
@protect
def download_file(file_name):
    file_manager = FileManager(DIRECTORY)
    print(file_name)
    return file_manager.download_file(file_name)


@bp.route('/upload_file/', methods=['GET', 'POST'])
@protect
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        file_manager = FileManager(DIRECTORY)
        success = file_manager.upload_file(file)
        if success:
            flash(f"Successfully uploaded file {file.filename}")
        elif file.filename == "":
            flash("Please select a file to upload first!!!")
        else:
            flash(f"Upload failed... file {file.filename} already exists!")
    return redirect(url_for('wiki.file_storage'))

