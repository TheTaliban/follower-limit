import twitter, twitter_config, sys, ast, random, json
from datetime import datetime
from os import path

ordinal = lambda n: "%d%s" % (n,"tsnrhtdd"[(n/10%10!=1)*(n%10<4)*n%10::4])

users = [
        #'FucktardIdiot',
        'TheGeoff6Blues'
        ]

states_file = '/home/pi/git/twitter_max_followers/states.dict'
log_file = '/home/pi/git/twitter_max_followers/log.txt'

def check_follows(tw, state, user):
    try:
        followers = tw.GetFollowers(user_id=twitter_config.accounts[user]['id'])

    except Exception as e:
        print sys.exc_info()
        return state
    
    if len(followers) <= state['max_followers']:
        print 'Ahh... just right. You have {0} grateful followers.'.format(len(followers))
    else:
        print 'You have {0} followers! Thats too many!!! Lets block some'.format(len(followers))

        blocks = followers[state['max_followers'] - len(followers):]
        blocklist = []

        for n, block in enumerate(blocks):
            blocklist.append(block.screen_name)
            status = random.choice(state['status_formats'])
            status = status.format(ordinal(len(state['blocks'])+n),
                                   ordinal(state['max_followers']),
                                   block.screen_name)
            
        with open(log_file, 'a') as lf:
            lf.write('Blocked at {0}:\n      {1}'.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S'),','.join(blocklist)))

    return state


if __name__ == '__main__':
    # Load the last state of things
    if path.isfile(states_file):
        states = json.load(open(states_file, 'r'))
    else:
        # Or make it with defaults
        for user in users:
            states = dict()
            states[user] = dict(
                            max_followers=25,
                            blocks=[],
                            status_formats=['Welcome to my {0} {1} follower @{2}, who i shall now block.'])
        
        with open(states_file, 'w') as file:
            json.dump(states, file)

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
        print states
        
        user_state = check_follows(tw, states[user], user)

        states[user] = user_state

        with open(states_file, 'w') as file:
            json.dump(states, file)
