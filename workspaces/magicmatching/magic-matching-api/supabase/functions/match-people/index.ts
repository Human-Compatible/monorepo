import 'xhr_polyfill';
import { serve } from 'std/server';
import { Configuration, OpenAIApi } from 'openai';
import { createClient } from '@supabase/supabase-js';

import { corsHeaders } from '../_shared/cors.ts'

serve(async (req) => {
	// Handle CORS

	//console.log({req})

	if (req.method === 'OPTIONS') {
		return new Response('ok', { headers: corsHeaders });
	}

	// Search query is passed in request payload
	let { query, match_threshold, match_count } = await req.json();
	match_threshold = match_threshold === undefined ? 0.78 : match_threshold; // Choose an appropriate threshold for your data
	match_count = match_count === undefined ? 10 : match_count; // Choose the number of matches
	//console.log({query})
	console.log({ match_threshold });
	console.log({ match_count });

	// OpenAI recommends replacing newlines with spaces for best results
	const input = query.replace(/\n/g, ' ');

	console.log({ input });

	const configuration = new Configuration({ apiKey: Deno.env.get('OPENAI_API_KEY') });
	const openai = new OpenAIApi(configuration);

	// Generate a one-time embedding for the query itself
	const embeddingResponse = await openai.createEmbedding({
		model: 'text-embedding-ada-002',
		input,
	});

	const [{ embedding }] = embeddingResponse.data.data;
	console.log({ embedding });

	const supabaseClient = createClient(Deno.env.get('SUPABASE_URL'), Deno.env.get('SUPABASE_SERVICE_ROLE_KEY'));

	// In production we should handle possible errors
	//const { data: persons } = await supabaseClient.rpc('match_person_sections', {
	const persons_match = await supabaseClient.rpc('match_person_sections', {
		embedding,
		match_threshold,
		match_count,
		min_content_length: 5,
	});

	return new Response(JSON.stringify({ persons_match }), {
		headers: { ...corsHeaders, 'Content-Type': 'application/json' },
	});
});

// To invoke:
// curl -L -X POST 'https://ptrmlwxusgzqzspiayja.functions.supabase.co/match-persons' \
//   --header 'Authorization: Bearer ....' \
//   --header 'Content-Type: application/json' \
//   --data '{"query":"Fun and friendly person"}'



// To invoke:
// curl -i --location --request POST 'http://localhost:54321/functions/v1/' \
//   --header 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZS1kZW1vIiwicm9sZSI6ImFub24iLCJleHAiOjE5ODM4MTI5OTZ9.CRXP1A7WOeoJeXxjNni43kdQwgnWNReilDMblYTn_I0' \
//   --header 'Content-Type: application/json' \
//   --data '{"name":"Functions"}'



