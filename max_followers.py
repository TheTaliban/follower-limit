import twitter, twitter_config, sys, ast, random
from datetime import datetime
from os import path

ordinal = lambda n: "%d%s" % (n,"tsnrhtdd"[(n/10%10!=1)*(n%10<4)*n%10::4])

users = ['FucktardIdiot']
states_file = '/home/pi/git/twitter_max_followers/states.dict'

def check_follows(tw, states, user):
    try:
        followers = tw.GetFollowersList(since_id=states[user]['since_id'])

    except Exception as e:
        print sys.exc_info()
        return

    if len(followers) > user['max_follower_count']:
        blocks = followers[user['max_follower_count'] - len(followers):]
        user['blocks'][datetime.now()] = blocks
        for block in blocks:
            #if dm.entities.media.media_url:
            #    print dm.entities.media.media_url
            try:
                status = random.choice(user['status_formats'])
                status = status.format(ordinal(len(user['blocks'])),
                                       ordinal(user['max_follower_count']),
                                       block.screen_name)
                print status
                #tw.PostUpdate(dm.AsDict()['text'])
            except Exception as e:
                print sys.exc_info()

    return states


if __name__ == '__main__':
    # Load the last state of things
    if path.isfile(states_file):
        states = dict(open(states_file, 'r').read())
    else:
        # Or make it with defaults
        for user in users:
            states = dict()
            states[user] = {'max_followers': 1999,
                            'blocks': {datetime.now(): []},
                            'status_formats': ['Welcome to my {0} {1} follower {2}, who i shall now block.']}
        with open(states_file, 'w') as file:
            file.write(str(states))


    for user in users:
        cred = twitter_config.accounts[user]
        try:
            tw = twitter.Api(consumer_key=cred['consumer_key'],
                             consumer_secret=cred['consumer_secret'],
                             access_token_key=cred['access_token_key'],
                             access_token_secret=cred['access_token_secret'])
        except Exception, e:
            print e
            print 'Error on init'
            exit()

        user_state = check_follows(tw, states, user)
        states[user] = user_state
        
        with open(states_file, 'w') as file:
            file.write(str(states))
