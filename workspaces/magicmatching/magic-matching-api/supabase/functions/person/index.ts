import { serve } from 'std/server';
import { createClient, SupabaseClient } from '@supabase/supabase-js';

import { corsHeaders } from '../_shared/cors.ts'

interface Person {
	path: string;
	checksum: string;
	meta: object;
}
//   status: number

async function getPerson(supabaseClient: SupabaseClient, username: string) {
	const { data: person, error } = await supabaseClient.from('person').select('*').eq('path', username);
	if (error) throw error;

	return new Response(JSON.stringify({ person }), {
		headers: { ...corsHeaders, 'Content-Type': 'application/json' },
		status: 200,
	});
}

async function getAllPersons(supabaseClient: SupabaseClient) {
	const { data: persons, error } = await supabaseClient.from('person').select('*');
	if (error) throw error;

	return new Response(JSON.stringify({ persons }), {
		headers: { ...corsHeaders, 'Content-Type': 'application/json' },
		status: 200,
	});
}

async function deletePerson(supabaseClient: SupabaseClient, username: string) {
	const { error } = await supabaseClient.from('person').delete().eq('path', username);
	if (error) throw error;

	return new Response(JSON.stringify({}), {
		headers: { ...corsHeaders, 'Content-Type': 'application/json' },
		status: 200,
	});
}

async function updatePerson(supabaseClient: SupabaseClient, username: string, person: Person) {
	const { error } = await supabaseClient.from('person').update({path: person.path, meta: person.meta }).eq('path', username);
	if (error) throw error;

	return new Response(JSON.stringify({ person }), {
		headers: { ...corsHeaders, 'Content-Type': 'application/json' },
		status: 200,
	});
}

async function createPerson(supabaseClient: SupabaseClient, person: Person) {
	const { error } = await supabaseClient.from('person').insert({path: person.path, meta: person.meta});
	if (error) throw error;

	return new Response(JSON.stringify({ path: person.path, meta: person.meta }), {
		headers: { ...corsHeaders, 'Content-Type': 'application/json' },
		status: 200,
	});
}

serve(async (req) => {
	const { url, method } = req;

	console.log('URL: ', url);

	// This is needed if you're planning to invoke your function from a browser.
	if (method === 'OPTIONS') {
		return new Response('ok', { headers: corsHeaders });
	}

	try {
		const supabaseClient = createClient(Deno.env.get('SUPABASE_URL'), Deno.env.get('SUPABASE_SERVICE_ROLE_KEY'));
		// Create a Supabase client with the Auth context of the logged in user.
// 		const supabaseClient = createClient(
// 			// Supabase API URL - env var exported by default.
// 			Deno.env.get('SUPABASE_URL') ?? '',
// 			// Supabase API ANON KEY - env var exported by default.
// 			Deno.env.get('SUPABASE_ANON_KEY') ?? '',
// 			// Create client with Auth context of the user that called the function.
// 			// This way your row-level-security (RLS) policies are applied.
// 			{ global: { headers: { Authorization: req.headers.get('Authorization')! } } }
// 		);

		// For more details on URLPattern, check https://developer.mozilla.org/en-US/docs/Web/API/URL_Pattern_API
		const personPattern = new URLPattern({ pathname: '/person/:username' });
		const matchingPath = personPattern.exec(url);
		const username = matchingPath ? matchingPath.pathname.groups.username : null;

		console.log('PERSON USERNAME: ', username);

		let person = null;
		if (method === 'POST' || method === 'PUT') {
			const body = await req.json();
			person = body.person;
		}

		console.log('PERSON: ', person);

		// call relevant method based on method and username
		switch (true) {
			case username && method === 'GET':
				return getPerson(supabaseClient, username as string);
			case username && method === 'PUT':
				return updatePerson(supabaseClient, username as string, person);
			case username && method === 'DELETE':
				return deletePerson(supabaseClient, username as string);
			case method === 'POST':
				return createPerson(supabaseClient, person);
			case method === 'GET':
				return getAllPersons(supabaseClient);
			default:
				return getAllPersons(supabaseClient);
		}
	} catch (error) {
		console.error(error);

		return new Response(JSON.stringify({ error: error.message }), {
			headers: { ...corsHeaders, 'Content-Type': 'application/json' },
			status: 400,
		});
	}
});
