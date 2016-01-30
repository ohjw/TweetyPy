from bottle import route, request, debug, run, template, redirect
import urllib2
import twurl
import json
import sqlite3
import pickle
from operator import itemgetter
from pytz import timezone
from datetime import datetime

session = {'archiveID': 1, 'user_details': []}


def make_menu():
    global session
    trends = get_trends()
    menu = "<h2 id = 'homeName'>TweetyPy</h2>"
    menu += "<img id = 'homeImage' src='http://wallpapercave.com/wp/dYlAC1J.png'>"
    menu += "<h4 class = 'heading'>Current User</h4>"
    menu += "<ul><li class = 'menuOptions'><a id = 'timelineLink' href='/'>" + str(
        session['user_details'][1]) + "'s Timeline </a></li></ul><br>"
    menu += "<h4 class = 'heading'>My Archives</h4>"

    connect = sqlite3.connect('twitterDB.db')
    cursor = connect.cursor()

    # get all owners archives - names and id
    owned_archives = get_owners_archives()
    menu += "<ul>"
    for owned_archive in owned_archives:
        cursor.execute("SELECT tweet FROM tweets WHERE archiveID=?", (owned_archive[0],))
        result = cursor.fetchall()
        menu += "<li class = 'menuOptions'><a class='menuItem' href='/showArchive/" + str(owned_archive[0]) + "'>" + \
                owned_archive[1] + " (" + str(
            len(result)) + ")</a></li><br>"
    menu += "</ul>"
    menu += "<h4 class = 'heading'>Shared Archives</h4>"

    # get all shared archives - names and id
    cursor.execute(
        "SELECT id, name FROM archives WHERE id=(SELECT archiveID FROM archiveUsers WHERE sharedUserID=?) "
        "ORDER BY name ASC", (str(session['user_details'][0])))
    shared_archives = cursor.fetchall()
    menu += "<ul>"
    for shared_archive in shared_archives:
        # get the length of the archive to display
        cursor.execute("SELECT tweet FROM tweets WHERE archiveID=?", (shared_archive[0],))
        result = cursor.fetchall()
        menu += "<li class = 'menuOptions'><a class='menuItem' href='/showArchive/" + str(shared_archive[0]) + "'>" + \
                shared_archive[1] + " (" + str(
            len(result)) + ")</a></li><br>"
    menu += "</ul>"
    menu += "<h4 class = 'heading'>New Archive</h4>"
    menu += '''<form method='post' action='/addArchive'>
               <input class = 'center-align' type='text' name='newArchive' size='15' placeholder='Archive Name'><br>
               <input type='submit' name='submit' value='Create'>
               </form>'''

    menu += trends

    cursor.close()
    connect.close()
    return menu

def get_trend_name(trends):
    names = []
    trend_obj = trends['trends']

    html = ''
    for trend in trend_obj:
        if 'name' in trend:
            names.append([trend['name'], trend['query']])

    sorted_trends = sorted(names, key=itemgetter(0))

    for name in sorted_trends:
        html += "<tr><td><a class = 'trendLinks' href='/trend/" + name[1] + "'>" + name[0] + "</a></td></tr>"

    return html


def get_trends():
    twitter_url = "https://api.twitter.com/1.1/trends/place.json?"
    parameters = {'id': 1}
    data = call_api(twitter_url, parameters)
    js = json.loads(data)
    html = "<h4 class = 'heading'>Trends</h4>"
    html += "<table id = 'trends'>"

    for item in js:
        html += get_trend_name(item)

    html += "</table>"
    return html


def get_owners_archives():
    # get all owners archives - names and id
    connect = sqlite3.connect('twitterDB.db')
    cursor = connect.cursor()
    cursor.execute("SELECT DISTINCT archives.id, archives.name FROM archives WHERE "
                   "archives.ownerID=? ORDER BY archives.name ASC",
                   (session['user_details'][0],))
    owned_archives = cursor.fetchall()
    cursor.close()
    connect.close()

    return owned_archives


def check_archive_owner(user, archive_id):
    connect = sqlite3.connect('twitterDB.db')
    cursor = connect.cursor()
    cursor.execute("SELECT * FROM archives WHERE ownerID=? and id=?", (user, archive_id,))
    found = cursor.fetchone()
    cursor.close()
    connect.close()

    if found:
        # current user is the archive owner
        return found
    else:
        return False


def get_archive_name(count):
    # check if archive is owned by the current user
    users_owned_archive = check_archive_owner(session['user_details'][0], session['archiveID'])

    # retrieve the current archives name
    connect = sqlite3.connect('twitterDB.db')
    cursor = connect.cursor()
    cursor.execute("SELECT name FROM archives WHERE id=?", (session['archiveID'],))
    archive_name = cursor.fetchone()

    header = "<h2 class = 'pageHeading'>Archive: " + str(archive_name[0]) + " ({}) </h2>".format(count)

    # if user owns the archive then allow them to share it and delete it
    if users_owned_archive:
        # get all users to share archive with
        users = make_share_archive_dropdown()

        # enable owner to delete their archive
        header += "<p class = 'pageHeading'><a href='/deleteArchive'>[Delete Archive]</a></p>"
        header += users
    else:
        # display name of user who shared the archive
        archive_owner = get_archive_owner()
        header += "<p class = 'pageHeading'>Shared by: " + str(archive_owner[1]) + "</p>"
        header += "<p class = 'pageHeading'><a href='/unfollowArchive'> [Unfollow Archive]</a></p>"

    cursor.close()
    connect.close()
    return header


def get_archive_owner():
    connect = sqlite3.connect('twitterDB.db')
    cursor = connect.cursor()

    # get archive owners id and name
    cursor.execute("SELECT id, name FROM users WHERE id=(SELECT ownerID FROM archives WHERE id=?)",
                   (session['archiveID']))
    archive_owner = cursor.fetchone()

    return archive_owner


def make_share_archive_dropdown():
    connect = sqlite3.connect('twitterDB.db')
    cursor = connect.cursor()

    # retrieve all names and ids except the owner and already shared users
    cursor.execute(
        "SELECT id, name FROM users WHERE NOT EXISTS "
        "(SELECT * FROM archiveUsers WHERE archiveUsers.sharedUserID=users.id "
        "AND archiveUsers.archiveID=?) AND id != ? ORDER by users.name ASC",
        (session['archiveID'], session['user_details'][0],))
    user_results = cursor.fetchall()

    cursor.close()
    connect.close()

    # display a dropdown with a list of all available users to share with
    html = "<form name ='shareArchive' method='POST' action='/shareArchive'>"
    html += "<p class = 'center-align'><select name='sharedUserID' onchange='form.submit()'>"
    html += "<option>- - Share archive with - -</option>"
    for user in user_results:
        html += "<option value='" + str(user[0]) + "'>" + user[1] + "</option>"
    html += "</select></form></p>"

    return html


@route('/shareArchive', method='post')
def share_archive():
    shared_user_id = request.POST.get('sharedUserID', '').strip()
    connect = sqlite3.connect('twitterDB.db')
    cursor = connect.cursor()

    # add user to archive users list to enable them to view the shared archive
    cursor.execute("INSERT INTO archiveUsers (archiveID, sharedUserID) VALUES (?,?)",
                   (session['archiveID'], shared_user_id))
    connect.commit()
    cursor.close()
    connect.close()

    redirect('/showArchive/' + session['archiveID'])


def call_api(twitter_url, parameters):
    url = twurl.augment(twitter_url, parameters)
    connection = urllib2.urlopen(url)
    return connection.read()


def make_archive_dropdown(tweet_id):
    connect = sqlite3.connect('twitterDB.db')
    cursor = connect.cursor()

    cursor.execute("SELECT id, name, ownerID from archives "
                   "WHERE NOT EXISTS(SELECT * FROM tweets WHERE tweets.tweetID=? AND archives.id = archiveID) "
                   "AND ownerID=?", (tweet_id, session['user_details'][0],))
    archives = cursor.fetchall()

    html = "<select name='archiveID' onchange='form.submit()'>"
    html += "<option>- - Save to - -</option>"
    for archive in archives:
            html += "<option value='" + str(archive[0]) + "'>" + archive[1] + "</option>"
    html += "</select>"
    cursor.close()
    connect.close()

    return html


def make_tweet(item, mode, archive_list):
    global session
    html, tweet_html, links = '', item['text'], ''
    user_mentions, hashtags, images, urls = [], [], [], []

    # @username
    if 'user_mentions' in item['entities']:
        for user in item['entities']['user_mentions']:
            user_mentions.append([user['indices'][0], user['indices'][1], 'user', user['screen_name']])

    # hashtags
    if 'hashtags' in item['entities']:
        for hashtag in item['entities']['hashtags']:
            hashtags.append(hashtag['text'])

    # images
    if 'media' in item['entities']:
        for image in item['entities']['media']:
            images.append(image['media_url'])

    # all URLS
    if 'urls' in item['entities']:
        for url in item['entities']['urls']:
            urls.append([url['url'], url['expanded_url']])

    if mode == 'myTimeline':
        links = "<form name='archive' method='post' action='/archive'>"
        links += "<input type='hidden' name='tweetID' value='" + str(item['id']) + "'>"
        links += archive_list
        links += "</form>"
    elif mode == 'archive':
        is_owner = check_archive_owner(session['user_details'][0], session['archiveID'])

        # enable user to move the tweets in the archive and also delete them if they are the owner
        if is_owner:
            links = "<a href='/moveUp/" + str(item['id']) + "'><img class = 'archiveArrows' title = 'Move Up' alt = 'Move Up' src='https://cdn3.iconfinder.com/data/icons/google-material-design-icons/48/ic_keyboard_arrow_up_48px-128.png' /></a><br>" + \
                    "<a href='/moveDown/" + str(item['id']) + "'><img class = 'archiveArrows' title = 'Move Down' alt = 'Move Down' src='https://cdn3.iconfinder.com/data/icons/google-material-design-icons/48/ic_keyboard_arrow_down_48px-128.png'</a><br>" + \
                    "<a href='/deleteTweet/" + str(item['id']) + "'><img id = 'deleteIcon' title = 'Remove Tweet' alt ='Remove Tweet' src='https://cdn2.iconfinder.com/data/icons/gentle-edges-icon-set/128/Iconfinder_0041_5.png'</a>"
    else:
        return

    sorted_user_mentions = sorted(user_mentions, key=itemgetter(0))
    sorted_hashtags = sorted(hashtags, key=itemgetter(0))
    sorted_images = sorted(images, key=itemgetter(0))
    sorted_urls = sorted(urls, key=itemgetter(0))

    for user in sorted_user_mentions:
        tweet_html = tweet_html.replace("@" + user[3], "<a href='/userMentions/" + user[3] + "'>@" + user[3] + "</a>")

    for hashtag in sorted_hashtags:
        tweet_html = tweet_html.replace("#" + hashtag, "<a href='/searchHashtag/" + hashtag + "'>#" + hashtag + " </a>")

    for url in sorted_urls:
        tweet_html = tweet_html.replace(url[0], "<a target='_blank' href='" + url[1] + "'>" + url[0] + "</a>")

    for image in sorted_images:
        tweet_html += "<br><img id = 'tweetedImage' src='" + image + "'>"

    # tweet timestamp
    utc = timezone('UTC')
    created_at = datetime.strptime(item['created_at'], '%a %b %d %H:%M:%S +0000 %Y')
    tweet_date = utc.localize(created_at)

    html += "<table><tr valign='top'><td width='70'>"
    html += "<img src='" + item['user']['profile_image_url'] + "'></td>"
    html += "<td id = 'userField' >" + item['user']['name'] + "<a id ='userHandle' href='/userMentions/" + item['user'][
        'screen_name'] + "'> @" + item['user']['screen_name'] + "</a>"
    html += "<div id='date'> " + str(tweet_date) + "</div>"
    html += "</td></tr>"
    html += "<tr><td>" + links + "</td><td class='tweetField'>" + tweet_html + "<br>"
    html += "<div class = 'statField'><img class = 'statIcon' src='https://cdn3.iconfinder.com/data/icons/social-1/100/retweet-128.png'>" \
            + str(item['retweet_count']) + \
            "<img class = 'statIcon' src='https://cdn0.iconfinder.com/data/icons/very-basic-android-l-lollipop-icon-pack/24/like-128.png'>" \
            + str(item['favorite_count']) + "</div>"
    html += "</td></tr></table><hr>"

    return html


def show_my_timeline():
    twitter_url = 'https://api.twitter.com/1.1/statuses/home_timeline.json'
    parameters = {'count': 15}
    data = call_api(twitter_url, parameters)
    js = json.loads(data)
    html = ''

    for item in js:
        archives = make_archive_dropdown(item['id'])
        html += make_tweet(item, 'myTimeline', archives)
    return html


def get_tweet(tweet_id):
    twitter_url = 'https://api.twitter.com/1.1/statuses/show.json'
    parameters = {'id': tweet_id}
    data = call_api(twitter_url, parameters)
    return json.loads(data)


def show_stored_tweets(archive_id):
    connect = sqlite3.connect('twitterDB.db')
    cursor = connect.cursor()
    cursor.execute("SELECT tweet FROM tweets WHERE archiveID=? ORDER BY position ASC", (archive_id,))
    result = cursor.fetchall()
    count = len(result)
    cursor.close()
    connect.close()
    html = ''

    for tweet in result:
        html += make_tweet(pickle.loads(tweet[0]), 'archive', '')
    return html, count


@route('/archive', method='post')
def archive_tweet():
    global session
    archive_id = request.POST.get('archiveID', '').strip()
    tweet_id = request.POST.get('tweetID', '').strip()
    pickled_tweet = pickle.dumps(get_tweet(tweet_id))
    connect = sqlite3.connect('twitterDB.db')
    cursor = connect.cursor()
    cursor.execute("SELECT position FROM tweets WHERE archiveID=? ORDER BY position DESC LIMIT 1",
                   (session['archiveID']))
    db_row = cursor.fetchone()

    if db_row is not None:
        next_position = int(db_row[0]) + 1
    else:
        next_position = 1
    cursor.execute("INSERT INTO tweets (tweetID, tweet, archiveID, position) VALUES (?,?,?,?)",
                   (tweet_id, sqlite3.Binary(pickled_tweet), archive_id, next_position))
    connect.commit()
    cursor.close()
    connect.close()
    session['archiveID'] = archive_id
    html, count = show_stored_tweets(archive_id)

    return template('showTweets.tpl', heading=get_archive_name(count), menu=make_menu(), html=html)


@route('/deleteTweet/<id>')
def delete_tweet(id):
    connect = sqlite3.connect('twitterDB.db')
    cursor = connect.cursor()
    cursor.execute("DELETE FROM tweets WHERE tweetID=? AND archiveID=?", (id, session['archiveID']))
    connect.commit()
    cursor.close()
    connect.close()
    html, count = show_stored_tweets(session['archiveID'])

    return template('showTweets.tpl', heading=get_archive_name(count), menu=make_menu(), html=html)


@route('/moveUp/<id>')
def move_up(id):
    global session
    connect = sqlite3.connect('twitterDB.db')
    cursor = connect.cursor()

    cursor.execute("SELECT position FROM tweets WHERE tweetID=? AND archiveID=?", (id, session['archiveID']))
    position = cursor.fetchone()[0]
    cursor.execute(
        "SELECT tweetID, position FROM tweets WHERE position<? AND archiveID=? ORDER BY position DESC LIMIT 1",
        (position, session['archiveID']))
    db_row = cursor.fetchone()

    if db_row is not None:
        other_id, other_position = db_row[0], db_row[1]
        cursor.execute("UPDATE tweets SET position=? WHERE tweetID=? AND archiveID=? ",
                       (other_position, id, session['archiveID']))
        cursor.execute("UPDATE tweets SET position=? WHERE tweetID=? AND archiveID=?",
                       (position, other_id, session['archiveID']))
        connect.commit()
    cursor.close()
    connect.close()
    html, count = show_stored_tweets(session['archiveID'])
    return template('showTweets.tpl', heading=get_archive_name(count), menu=make_menu(), html=html)


@route('/moveDown/<id>')
def move_down(id):
    global session
    connect = sqlite3.connect('twitterDB.db')
    cursor = connect.cursor()

    cursor.execute("SELECT position FROM tweets WHERE tweetID=? AND archiveID=?", (id, session['archiveID']))
    position = cursor.fetchone()[0]
    cursor.execute(
        "SELECT tweetID, position FROM tweets WHERE position>? AND archiveID=? ORDER BY position ASC LIMIT 1",
        (position, session['archiveID']))
    db_row = cursor.fetchone()

    if db_row is not None:
        other_id, other_position = db_row[0], db_row[1]
        cursor.execute("UPDATE tweets SET position=? WHERE tweetID=? AND archiveID=? ",
                       (other_position, id, session['archiveID']))
        cursor.execute("UPDATE tweets SET position=? WHERE tweetID=? AND archiveID=?",
                       (position, other_id, session['archiveID']))
        connect.commit()
    cursor.close()
    connect.close()
    html, count = show_stored_tweets(session['archiveID'])
    return template('showTweets.tpl', heading=get_archive_name(count), menu=make_menu(), html=html)


@route('/showArchive/<archive_id>')
def show_archive(archive_id):
    global session
    session['archiveID'] = archive_id
    html, count = show_stored_tweets(archive_id)

    return template('showTweets.tpl', heading=get_archive_name(count), menu=make_menu(), html=html)


@route('/addArchive', method='post')
def add_archive():
    new_archive = request.POST.get('newArchive', '').strip()
    if new_archive != '':
        connect = sqlite3.connect('twitterDB.db')
        cursor = connect.cursor()

        # add new archive name and owner to db
        cursor.execute("INSERT INTO archives (name, ownerID) VALUES (?,?)", (new_archive, session['user_details'][0],))
        connect.commit()

        cursor.close()
        connect.close()

    user = session['user_details'][1] + '\'s'
    html = show_my_timeline()
    return template('showTweets.tpl', heading=user + " Timeline", menu=make_menu(), html=html)


@route('/deleteArchive')
def delete_archive():
    connect = sqlite3.connect('twitterDB.db')
    cursor = connect.cursor()
    cursor.execute("DELETE from archives WHERE id=?", (session['archiveID']))
    cursor.execute("DELETE from tweets WHERE archiveID=?", (session['archiveID']))
    connect.commit()
    cursor.close()
    connect.close()

    user = session['user_details'][1] + '\'s'
    html = show_my_timeline()
    return template('showTweets.tpl', heading=user + " Timeline", menu=make_menu(), html=html)


@route('/unfollowArchive')
def delete_archive():
    global session
    connect = sqlite3.connect('twitterDB.db')
    cursor = connect.cursor()

    # delete current user from the archiveUsers if they decide to unfollow
    cursor.execute("DELETE FROM archiveUsers WHERE sharedUserID=? AND archiveID=?",
                   (session['user_details'][0], session['archiveID'], ))
    connect.commit()
    cursor.close()
    connect.close()

    user = session['user_details'][1] + '\'s'
    html = show_my_timeline()

    return template('showTweets.tpl', heading=user + " Timeline", menu=make_menu(), html=html)


def search_for_tweets(search_term):
    twitter_url = 'https://api.twitter.com/1.1/search/tweets.json'
    url = twurl.augment(twitter_url, {'q': search_term, 'count': 10})
    connection = urllib2.urlopen(url)
    data = connection.read()
    js = json.loads(data)
    html = ''

    for item in js['statuses']:
        archives = make_archive_dropdown(item['id'])
        html += make_tweet(item, 'myTimeline', archives)
    return html


@route('/userMentions/<name>')
def user_mentions(name):
    name = "@" + name
    html = search_for_tweets(name)

    return template('showTweets.tpl', heading=name, menu=make_menu(), html=html)


@route('/searchHashtag/<hashtag>')
def search_for_hashtag(hashtag):
    hashtag = "#" + hashtag
    html = search_for_tweets(hashtag)

    return template('showTweets.tpl', heading=hashtag, menu=make_menu(), html=html)


@route('/trend/<trend>')
def search_for_trend(trend):
    html = search_for_tweets(trend)

    return template('showTweets.tpl', heading=trend, menu=make_menu(), html=html)

@route('/')
def index():
    global session

    if not session['user_details']:
        redirect('/login')

    else:
        user = session['user_details'][1] + '\'s'
        html = show_my_timeline()
        return template('showTweets.tpl', heading=user + " Timeline", menu=make_menu(), html=html)


def check_login(name, password):
    global session
    connect = sqlite3.connect('twitterDB.db')
    cursor = connect.cursor()

    cursor.execute("SELECT * FROM users WHERE name=? and password=?", (name, password))
    found = cursor.fetchone()
    cursor.close()
    connect.close()

    if found:
        # user exists and password matches
        session['user_details'] = found
        return True
    else:
        # user does not exist or password does not match
        return False


@route('/login')
def login():
    return template('loginOrRegister.tpl', message='', link='/register',
                    linkMessage='New User? Sign up to TweetyPy here', post='/checkLogin')


@route('/logout')
def logout():
    session.clear()
    redirect('/login')


@route('/checkLogin', method='post')
def login_submit():
    global session
    name = request.forms.get('name')
    password = request.forms.get('password')
    if check_login(name, password):
        redirect('/')
    else:
        return template('successOrFailure.tpl', message='Tweety is not happy with the details provided!',
                        link='/login', linkMessage='--> Try Again <--',
                        image='http://www.picturesanimations.com/t/tweety/t17.gif',
                        imageClass='failureImage')


def add_details(name, password):
    connect = sqlite3.connect('twitterDB.db')
    cursor = connect.cursor()

    # add new user name and password to db
    cursor.execute("INSERT INTO users (name, password) VALUES (?, ?)", (name, password,))
    connect.commit()
    cursor.close()
    connect.close()

    return template('successOrFailure.tpl', message='Welcome to TweetyPy!',
                    link='/login', linkMessage='--> Log in <--',
                    image='http://s.myniceprofile.com/myspacepic/438/43884.gif', imageClass='successImage')


@route('/register')
def sign_up():
    return template('loginOrRegister.tpl', message='Sign up to TweetyPy!', link='/login',
                    linkMessage='Already a member? Log in', post='/checkSignUp')


@route('/checkSignUp', method='post')
def check_sign_up():
    name = request.forms.get('name')
    password = request.forms.get('password')

    if name == '' or password == '':
        return template('successOrFailure.tpl', message='Tweety is not happy with the details provided!',
                        link='/register', linkMessage='--> Try Again <--',
                        image='http://www.picturesanimations.com/t/tweety/t17.gif', imageClass='failureImage')
    else:
        return add_details(name, password)


debug(True)
run(reloader=True)
