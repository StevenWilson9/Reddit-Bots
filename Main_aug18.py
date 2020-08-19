import praw, re, os
reddit = praw.Reddit("RSB1", user_agent="bot1 user agent")
subreddit = reddit.subreddit('learnpython')
# subreddit = reddit.subreddit('pythonforengineers')

# TODO
#   Is there a way to have it hosted/ leave it running?


def convert_string(string):
    format_items = re.compile(r"\.format\((.*?)\)")
    vlst = format_items.search(string).group(1).replace(' ', '').split(",")

    cut_end = re.compile(r"(.*)\.format\(")
    string = cut_end.search(string).group(1)
    if "'" in string and '"' in string:
        if string.index("'") < string.index('"'):
            string = string.replace('"', 'f"', 1)
        else:
            string = string.replace("'", "f'", 1)
    else:
        string = string.replace('"', 'f"', 1).replace("'", "f'", 1)

    if "=" in vlst[0]:
        return convert_string_dic(vlst, string)
    else:
        return convert_string_nodic(vlst, string)


def convert_string_nodic(vlst, string):
    nlst = []
    for i in vlst:
        nlst.append('{' + i + '}')

    for elem in nlst:
        string = string.replace('{}', elem, 1)
    return string


def convert_string_dic(vlst, string):
    a, b = [], []
    for i in vlst:
        aa, bb = i.split('=')
        a.append(aa)
        b.append(bb)
    for i in range(len(a)):
        string = string.replace(a[i], b[i])
    return string


def closereplylog():
    with open("posts_replied_to.txt", "w") as replied:
        for post_id in posts_replied_to:
            replied.write(post_id + "\n")


# Check for DMs
go, lst = False, []
for item in reddit.inbox.unread(limit=None):
    lst.append(f"{item.author} says:\n {item.body}")
    item.mark_read()
if lst == []:
    print("No new messages")
    go = True
else:
    for message in lst:
        print(message)


if go is True:
    if not os.path.isfile("posts_replied_to.txt"):
        posts_replied_to = []
    else:
        with open("posts_replied_to.txt", "r") as f:
            posts_replied_to = list(filter(None, f.read().split("\n")))
    ro = re.compile(r"( {4}.*(\.format)\(.*)")


    # for submission in subreddit.stream.submissions():

# findcomments
    comments = subreddit.stream.comments()
    comments_searched = 0
    for comment in comments:
        comments_searched += 1
        if comments_searched == 100:
            print("last 100 comments_searched. Searching for more...")
        if comments_searched > 100:
            print("comments_searched: ", comments_searched)
        if comment.link_url in posts_replied_to or comment.author == "FString-Bot":
            continue
        mo = ro.search(comment.body)
        if mo is not None:
            ostring = mo.group(1)
            nstring = convert_string(ostring)

            footer = """***
[^Direct ^message](https://www.reddit.com/message/compose/?to=FString-Bot)\
^( me if I've replied inappropriately.)"""

            comment_body = f"""You seem to have used the .format() format. \
However as of Python 3.6 released in August 2015, current best practice is to use \
[f-Strings](https://www.python.org/dev/peps/pep-0498/#abstract) \
which provide a concise, readable way to include the value of Python expressions inside strings. \
Original code: \n \n
{ostring} \n\n  f-string format:
\n\n{nstring} \n\n{footer} """

            print(comment.link_url)
            print(comment.author)
            print(comment.body)

            comment.reply(comment_body)
            posts_replied_to.append(comment.link_url)
            break

    closereplylog()
