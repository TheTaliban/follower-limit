import twitter, twitter_config, sys, ast 
from os import path 
users = ['spacedicks1488' , 'TheGeoff6Blues']
states_file = '/home/pi/git/twitter_dm_echo/states.dict' 

#if path.isfile(states_file):
#    states = dict(open(states_file, 'r').read()) 
#else:
#    states = dict()
#    for user in users:
#        states[user] = {'since_id': 0}
#        states['user']['since_id'] = 0
#    states['blacklist_patterns'] = [] 
#    with open(states_file, 'w') as file:
#        file.write(str(states))

def check_tweets(tw, states, user):
    try:
        dms = tw.GetDirectMessages(since_id=states[user]['since_id'])
    
    except Exception as e:
        print sys.exc_info()
        return

    if dms:
        states[user]['since_id'] = dms[0].id
        for dm in dms:
            #if dm.entities.media.media_url:
            #    print dm.entities.media.media_url
            try:
                tw.PostUpdate(dm.AsDict()['text']) 
            except Exception as e:
                print sys.exc_info()
#    return states
    with open(states_file, 'w') as file:
        file.write(str(states))


if __name__ == '__main__':
    if path.isfile(states_file):
        states = ast.literal_eval(open(states_file, 'r').read())
    else:
        states = dict.fromkeys(users)
        for user in users:
            states[user] = {'since_id': 0, 'blacklist_users': [], 'blacklist_patterns': []}

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
        user_state = check_tweets(tw, states, user)
