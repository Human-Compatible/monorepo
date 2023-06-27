import 'xhr_polyfill';
import { serve } from 'std/server';
import { Configuration, OpenAIApi } from 'openai';
import { createClient } from '@supabase/supabase-js';

// import config from '../_shared/config.ts';
import { corsHeaders } from '../_shared/cors.ts'

console.log('INIT: add-person');

const generateEmbeddings = async (person) => {
	const configuration = new Configuration({ apiKey: config.openai_key });
	const openai = new OpenAIApi(configuration);

	// const supabaseClient = createClient(config.supabase_url, config.supabase_service_key);
	const supabaseClient = createClient(Deno.env.get('SUPABASE_URL'), Deno.env.get('SUPABASE_SERVICE_ROLE_KEY'));

	console.log(person);
	const { organization_id, username, meta, location, sections } = person;

	//       // Check for existing person in DB and compare checksums
	//       const { error: fetchPersonError, data: existingPerson } = await supabaseClient
	//         .from('person')
	//         .select('id, username, checksum')
	//         .filter('username', 'eq', username)
	//         .limit(1)
	//         .maybeSingle()
	//
	//       if (fetchPersonError) {
	//         throw fetchPersonError
	//       }

	// Create/update person record. Intentionally clear checksum until we
	// have successfully generated all person sections.
	const { error: upsertPersonError, data: upsertperson } = await supabaseClient
		.from('person')
		.upsert(
			{
				organization_id: 1,
				username,
				location,
				meta,
			},
			{ onConflict: 'username' }
		)
		.select()
		.limit(1)
		.single();

	if (upsertPersonError) {
		throw upsertPersonError;
	}

	console.log(`[${username}] Adding ${sections.length} person sections (with embeddings)`);

	for (const { slug, heading, content } of sections) {
		// OpenAI recommends replacing newlines with spaces for best results
		const input = content.replace(/\n/g, ' ');

		try {
			const embeddingResponse = await openai.createEmbedding({
				model: 'text-embedding-ada-002',
				input,
			});

			if (embeddingResponse.status !== 200) {
				throw new Error(inspect(embeddingResponse.data, false, 2));
			}

			const [responseData] = embeddingResponse.data.data;

			const { error: insertPersonSectionError, data: personSection } = await supabaseClient
				.from('person_section')
				.insert({
					person_id: upsertperson.id,
					content,
					token_count: embeddingResponse.data.usage.total_tokens,
					embedding: responseData.embedding,
				})
				.select()
				.limit(1)
				.single();

			if (insertPersonSectionError) {
				throw insertPersonSectionError;
			}
		} catch (err) {
			// TODO: decide how to better handle failed embeddings
			console.error(
				`Failed to generate embeddings for '${username}' person section starting with '${input.slice(
					0,
					40
				)}...' due to: ${JSON.stringify(err)}`
			);

			throw err;
		}
	}
}
serve(async (req) => {
	console.log({req})

	if (req.method === 'OPTIONS') {
		return new Response('ok', { headers: corsHeaders });
	}

	const { person } = await req.json();
	console.log({person})
	await generateEmbeddings(person);

	const data = {
		message: `Created embeding for ${person.username}!`,
	};

	return new Response(JSON.stringify(data), { headers: { ...corsHeaders, 'Content-Type': 'application/json' } });
});

// To invoke:
// curl -i --location --request POST 'http://localhost:54321/functions/v1/' \
//   --header 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZS1kZW1vIiwicm9sZSI6ImFub24iLCJleHAiOjE5ODM4MTI5OTZ9.CRXP1A7WOeoJeXxjNni43kdQwgnWNReilDMblYTn_I0' \
//   --header 'Content-Type: application/json' \
//   --data '{"name":"Functions"}'


