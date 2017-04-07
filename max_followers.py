import twitter, twitter_config, sys, ast, random, json
from datetime import datetime
from os import path

ordinal = lambda n: "%d%s" % (n,"tsnrhtdd"[(n/10%10!=1)*(n%10<4)*n%10::4])

users = [
        'THE_TALlBAN'
        #'FucktardIdiot'
        #'TheGeoff6Blues'
        ]

#states_file = '/home/pi/git/twitter_max_followers/states.dict'
states_file = 'states.dict'
#log_file = '/home/pi/git/twitter_max_followers/log.txt'
log_file = 'log.txt'

def check_follows(tw, state, user):
    try:
        followers = tw.GetFollowers(user_id=twitter_config.accounts[user]['id'])

    except Exception as e:
        print sys.exc_info()
        return state
    
    current_followers = [(f.id, f.screen_name) for f in followers]

    if len(current_followers) <= state['max_followers']:
        state['followers'] = current_followers
        print 'Ahh {1}... just right. You have {0} grateful followers.'.format(len(current_followers), user)
    else:
        print 'Oh no {1}!! You have {0} followers! Thats too many!!! Lets block some'.format(len(current_followers), user)

        new_follows = [nf for nf in current_followers if nf[0] not in [f[0] for f in state['followers']]]
        blocks = new_follows[:len(current_followers) - state['max_followers']]
        
        for n, block in enumerate(blocks):
            status = random.choice(state['status_formats'])
            status = status.format(ordinal(len(state['blocks'])+1),
                                   ordinal(state['max_followers']+1),
                                   block[1])
            try:
                tw.CreateBlock(user_id=block[0])
                tw.DestroyBlock(user_id=block[0])
                tw.PostUpdate(status=status)
                state['blocks'].append(block[0])
                #print status
                'Blocked {0}!!'.format(block[1])
            except Exception as e:
                print sys.exc_info()
                return state
            
        with open(log_file, 'a') as lf:
            lf.write('Blocked at {0}:\n      {1}'.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S'),','.join([b[1] for b in blocks])))
            
    #state['blocks'] = [b for b in set(state['blocks'])]
    return state


if __name__ == '__main__':
    # Load the last state of things
    if path.isfile(states_file):
        states = json.load(open(states_file, 'r'))
    else:
        # Or make it with defaults
        states = dict()
    for user in [u for u in users if u not in states.keys()]:
        states[user] = dict(followers=[],
                            max_followers=68,
                            blocks=[],
                            status_formats=['Welcome to my {0} {1} follower @{2}, who i shall now block.',
                                            'Salutations to @{2}, my {0} {1} follower - who i shall now block.',
                                            'Congratulations, @{2}! You are my {0} {1} follower! And now you will be blocked. Better luck next time!'])
        
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
            #exit()
        
        #user_state = check_follows(tw, states[user], user)
        user_state = check_follows(tw, states[user], user)

        states[user] = user_state

        with open(states_file, 'w') as file:
            json.dump(states, file)
