import requests

lastFmAPIKey = 'xxxx'
spotifyAuthToken = 'xxxx'
spotifyRefreshToken = 'xxxx'

def rediscover(event, context):

    #Last.fm

    url = 'http://ws.audioscrobbler.com/2.0/?method=user.gettoptracks&user=mikebros&api_key=' + lastFmAPIKey + '&format=json&period=6month'

    response = requests.get(url)
    songs=response.json()["toptracks"]["track"]

    lastFmTracks = set()
    for song in songs:
        if (int(song["playcount"]) > 9):
            track = song["name"] + "~by~" + song["artist"]["name"]
            lastFmTracks.add(track)
            #print(track)

    #Spotify

    url = 'https://accounts.spotify.com/api/token'
    headers = {'Authorization':'Basic ' + spotifyAuthToken}
    payload = {'grant_type': 'refresh_token','refresh_token': spotifyRefreshToken}
    r = requests.post(url, headers=headers, data=payload)
    #print(r.text)

    response_json=r.json()
    access_token = response_json['access_token']
    #print(access_token)

    url = 'https://api.spotify.com/v1/me/playlists'
    headers = {'Authorization':'Bearer ' + access_token}

    r = requests.get(url, headers=headers)
    #print(r.text)

    url = 'https://api.spotify.com/v1/users/1244599073/playlists/1frv2udr1TM9T43xWksiny/tracks'
    #1frv2udr1TM9T43xWksiny rediscover
    #2xnV5KuZ4mHnWgd9cGPZPV guitar

    headers = {'Authorization':'Bearer ' + access_token}

    isNext=True
    spotifyTracks=set()
    spotifyIds={}

    while(isNext):
        #print(url)
        r = requests.get(url, headers=headers)
        response_json=r.json()
        songs = response_json['items']
        #print(len(songs))

        if response_json['next'] is None:
           isNext=False
        else:
            url = response_json['next']
        

        for song in songs:
            track = song['track']['name'] + "~by~" + song['track']['artists'][0]['name']
            #print(track)
            spotifyTracks.add(track)
            spotifyIds[track] = song['track']['id']

    #print(spotifyTracks)
    #print(spotifyIds)


    #merge
    both = lastFmTracks & spotifyTracks
    #print(both)
    for track in both:
        trackId = spotifyIds[track]

        url="https://api.spotify.com/v1/tracks/" + trackId
        r = requests.get(url)
        response_json=r.json()
        #print(response_json)
        
        url="https://api.spotify.com/v1/users/1244599073/playlists/6MHKoVNR2GMUzEaTeJ27Xq/tracks"
        payload = '{"uris": ["spotify:track:' +trackId + '"]}'
        r = requests.post(url, headers=headers, data=payload)
        response_json=r.json()

        url="https://api.spotify.com/v1/users/1244599073/playlists/1frv2udr1TM9T43xWksiny/tracks"
        payload = '{"uris": ["spotify:track:' +trackId + '"]}'
        r = requests.delete(url, headers=headers, data=payload)
        response_json=r.json()
        print("removing track: " + track + " from Rediscover")



    #In Limbo: 6MHKoVNR2GMUzEaTeJ27Xq

if __name__ == "__main__":
    rediscover("event", "context")
