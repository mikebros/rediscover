import requests

#auth details
lastFmAPIKey = 'xxx'
spotifyAuthToken = 'xxx='
spotifyRefreshToken = 'xxx'

#playlists
rediscoverPlaylist = '1frv2udr1TM9T43xWksiny'
guitarPlaylist = '2xnV5KuZ4mHnWgd9cGPZPV'
limboPlaylist = '6MHKoVNR2GMUzEaTeJ27Xq'

def getLastFmTracks():
    url = 'http://ws.audioscrobbler.com/2.0/?method=user.gettoptracks&user=mikebros&api_key=' + lastFmAPIKey + '&format=json&period=6month'

    response = requests.get(url)
    songs=response.json()["toptracks"]["track"]

    lastFmTracks = set()
    for song in songs:
        if (int(song["playcount"]) > 9):
            track = song["name"] + "~by~" + song["artist"]["name"]
            lastFmTracks.add(track)
            #print(track)

    return lastFmTracks

def getSpotifyAccessToken():
    url = 'https://accounts.spotify.com/api/token'
    headers = {'Authorization':'Basic ' + spotifyAuthToken}
    payload = {'grant_type': 'refresh_token','refresh_token': spotifyRefreshToken}
    r = requests.post(url, headers=headers, data=payload)
    #print(r.text)

    response_json=r.json()
    access_token = response_json['access_token']
    #print(access_token)

    return access_token

def getSpotifyTracks(spotifyAccessToken):
    #url = 'https://api.spotify.com/v1/me/playlists'
    #headers = {'Authorization':'Bearer ' + spotifyAccessToken}
    #r = requests.get(url, headers=headers)

    url = 'https://api.spotify.com/v1/users/1244599073/playlists/' + rediscoverPlaylist + '/tracks'
    headers = {'Authorization':'Bearer ' + spotifyAccessToken}

    isNext=True
    spotifyTracks=set()
    spotifyIds={}

    while(isNext):
        #print(url)
        r = requests.get(url, headers=headers)
        response_json=r.json()
        songs = response_json['items']

        if response_json['next'] is None:
           isNext=False
        else:
            url = response_json['next']
        for song in songs:
            track = song['track']['name'] + "~by~" + song['track']['artists'][0]['name']
            #print(track)
            spotifyTracks.add(track)
            spotifyIds[track] = song['track']['id']

    return [spotifyTracks, spotifyIds]        


def moveTracks(trackList, spotifyIds, spotifyAccessToken):
    headers = {'Authorization':'Bearer ' + spotifyAccessToken}
    #count = 0
    #{ "tracks": [{ "uri": "spotify:track:4iV5W9uYEdYUVa79Axb7Rh" },{"uri": "spotify:track:1301WleyT98MSxVHPZCA6M" }] }
    #trackIdList = []
    
    for track in trackList:
        #count = count + 1
        trackId = spotifyIds[track]

        url='https://api.spotify.com/v1/users/1244599073/playlists/' + limboPlaylist + '/tracks'
        payload = '{"uris": ["spotify:track:' +trackId + '"]}'
        r = requests.post(url, headers=headers, data=payload)
        #response_json=r.json()
        print("adding track: " + track.replace('~by~', " by ") + " to Limbo")

        url='https://api.spotify.com/v1/users/1244599073/playlists/' + rediscoverPlaylist + '/tracks'
        payload = '{"uris": ["spotify:track:' +trackId + '"]}'
        r = requests.delete(url, headers=headers, data=payload)
        #response_json=r.json()
        print("removing track: " + track.replace('~by~', " by ") + " from Rediscover")

def rediscover(event, context):

    lastFmTracks = getLastFmTracks()
    spotifyAccessToken = getSpotifyAccessToken()
    spotifyTrackInfo = getSpotifyTracks(spotifyAccessToken)

    spotifyTracks = spotifyTrackInfo[0]
    spotifyIds = spotifyTrackInfo[1]

    #merge
    both = lastFmTracks & spotifyTracks

    if(len(both) > 0):
        moveTracks(both, spotifyIds, spotifyAccessToken)
    else:
        print('nothing to move')


if __name__ == "__main__":
    rediscover("event", "context")
