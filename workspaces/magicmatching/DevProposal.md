## Discourse plugin requirements

- admin prefs
  - plugin enabled
  - ~~automatching enabled~~ feature for future milestone
  - api url
  - api token
  - introductions channel id
  - matching requests channel id

- `user_created`/`user_updated` handler

  post user 'profile' to matching api, includes group/roles membership, uses about-me and other standard Discourse fields to populate the matching profile - will be idempotent request to api matching (POST only, no PUT)

- `post_created` - in 'introductions' channel

  post and poster (user) details used to update user profile in matching api

- `post_created` (or maybe `topic_created`) - in 'matching requests' channel

  post/topic/user_id details used to initiate matching request from matching api - will add post to topic with details of response from matching api

## Possible additions (future milestones):

- `post_created` - in all channels listed in 'user profile channels' admin pref 

  post and poster (user) details used to update user profile in matching api, based on content of user's posts

- `post_created` (or `chatmsg_created`??) - in 'matching admin' channel

  poster (user) details used to manage auto-matching config, eg user writes "match me once each week" and plugin sends "auto matching" request to matching api


