# Magic Matching

## Discovery (Proof of Concept)

With a few design choices available, it was important to ensure the preferred solution was suitable. The high-level objective is a system to  provide a way for users of a private Discourse instance to get matched with each other, using an Ai matching algorithm. This POC was a discovery exercise into Discourse plugins, and connecting the plugin to an Ai matching API.

Some of the considerations:

- the Discourse "interface" can be purely via contents of topics/posts and user profiles (no UI elements needed)
- individual privacy must be maintained, conversations should not pollute via Ai
- the matching API can be separate from Discourse, but must be able to run self-hosted (& open-source)

This discovery exercise focussed mainly on Discourse; the proposed solution for Ai matching has been tested previously. 

Three techniques were considered within Discourse to operate as the "interface":

- webhooks (configured via Discourse admin UI)
- external service making API calls to Discourse
- plugin 

The webhooks solution could theoretically be good enough; calling the matching API on different Discourse events. But the lack of custom Auth headers, no mangling of request body, etc. makes it a poor choice.

Having an external service make API calls is technically possible; there is good API support in Discourse - and it would be completely flexible. But rather than being event driven, the service would need to do regular polling for new posts. There is little benefit and lots of extra effort, so it's a poor choice. 

Using a plugin was a pretty obvious choice from the start, but that's confirmed now with the due-diligence for webhooks and api-calls. The POC has handlers for `post_created` and `user_updated` events. Those handlers make http (REST) calls to the matching API. The handlers have access to both the `post` and `user` data/fields, so there shouldn't be any issues creating relevant payloads to send to the matching API.

The matching API is provided by Supabase (self-hosted). It has first-class support for "all" postgres features, including `pg_vector`. There is also great support for "serverless" functions via Deno. It expected that the same postgres instance will be used for both Discourse and Supasbase. The Supabase self-hosted requirements will still need to be reviewed by @SimonBiggs.

If the matching API needs to send requests to Discourse (eg. as result of scheduled/cron matching job), then the Discourse API is available.

### Privacy

The details of keeping personal data safe were not covered during this discovery. There is clear relationship between people (users) in Discourse and the channels/posts they have access to; and Postgres has full relational database features, including row-level-security, so there shouldn't be any traditional issues with keeping data safe and isolated. As long as the traditional data privacy is ensured, then no additional leakage should be introduced via Ai, since data and resulting embeddings are isolated. 

### Authentication

Although Supabase has a robust user auth system built in, it's not a good fit for the single API service (eg Discourse plugin) since there is no automated support for API keys. The self-hosted Supabase may be more flexible with setup of API keys. The worst case is using the key for the main Supabsase "service account"; it is a sensitive key, but internals of a Discourse server can be considered safe. 

### Open AI

The Supabase serverless functions are using Open AI to create embeddings. 

### Configuration

Configuration variables for plugins in Discourse are easy to expose via the Admin UI. A sample set of config values was taken from another Discourse plugin; the `token` and `url` config fields were used successfully as part of this POC. 

### Extra

The plugin has some extra code for modifying the Discourse UI - it was part of the early discovery process and is left as an artefact.

None of the API, database schema, or other code should be considered intentional design for the actual project. The design is for sake of proof-of-concept, nothing more. 

The Discourse docs are (ummmm) disappointing. The discovery process could have been much quicker and less painful with some better docs. But it's not a complete black box, and code is pretty good.

### Conclusion

Using a Discourse plugin to interface between users and the Ai matching service should work well. The plugin is event-driven so responses to match requests (via user posting) can happen in (near) real time (delay is due to Ai requests). The plugin has easy access to all relevant post & user data which can be packaged for sending to the matching API. The matching API is really just postgres (with pg_vector) so can handle both Ai storage/queries as well as data security. 

There are lots of details that still need to be specced, but no red flags or blockers are apparent. 

All the underlying software is opensource and the new/custom software will be provided with an open-source license.